# import required libraries
import requests
import json
import pandas as pd
import time
import duckdb

# ********************************************************************
# 1. Check API connection (API-NBA) using obtained API key (explained in README):
# ********************************************************************

print("******************************************************")
print("1. Check API connection (API-NBA) using obtained API key (explained in README)")


# Copy API key from account (As explained in README)
API_KEY = "55349773c22b153b017022b73bf2b494"

HEADERS = {
    "x-rapidapi-host": "v2.nba.api-sports.io",
    "x-rapidapi-key": API_KEY
}

# Check API connectivity for NBA Teams and Games endpoints
# HTTP status codes:
# 200 -> Success (API is working)
# 401 -> Unauthorized (invalid API key)
# 403 -> Forbidden (access restricted by plan or permissions)

print("API connection Testing results:")
url_teams = "https://v2.nba.api-sports.io/teams"
url_games = "https://v2.nba.api-sports.io/games"

url_teams_games = [url_teams, url_games]
api_teams_games = ['teams', 'games']

# Validate and display connection status for both endpoints
# (Teams and Games) before proceeding with data extraction

for i in range(2):
    # Make a GET request to the endpoints using API authentication headers.
    # This step connects to the external API and returns raw JSON data.
    test_response = requests.get(url_teams_games[i], headers=HEADERS)
    # Show api status connection
    if test_response.status_code == 200:
        print(f"    API for NBA {api_teams_games[i]} endpoint connected successfully!")
    else:
        print(f"    API connection failed. code: {test_response.status_code}")
        print("    Please check API key, internet connection and API limits.")
        exit()

# ********************************************************************
# 2. Inspect the team data and the games data structures
# ********************************************************************
print("******************************************************")
print("2. Inspect the team data and the games data structures:")

# Inspect API endpoint response structures to identify where the required fields are located.
# Required fields from teams endpoint:
# team_id, team_name, conference, division
#
# Required fields from games endpoint:
# game_id, season, date, home_team, away_team, home_score, away_score

for i in range(2):

    if api_teams_games[i] == "games":
        inspection_response = requests.get(
            url_teams_games[i],
            headers=HEADERS,
            params={
                "season": "2024",
                "league": "standard"
            }
        )
    else:
        inspection_response = requests.get(
            url_teams_games[i],
            headers=HEADERS
        )
    # Convert the API response (inspection_response) from JSON format into
    # a Python dictionary so its data strcuture can be reviewed.
    data = inspection_response.json()

    if len(data["response"]) > 0:
        print(f"\n One sample record of {api_teams_games[i]} data:")
        print(json.dumps(data["response"][0], indent=2))
    else:
        print(f"\nNo data returned for {api_teams_games[i]}")

# ********************************************************************
# 3. Fetching teams data from teams endpoint
# ********************************************************************
print("******************************************************")
print("3. Fetching teams data from teams endpoint:")
# Purpose:
# We retrieve the full list of NBA teams from the API in order to build
# a clean "teams dimension table" that will later be used for analysis
# and joining with game-level data.

response = requests.get(url_teams, headers=HEADERS)
teams_data = response.json()

# Initialize an empty list to store cleaned and structured team records.
teams = []

# Loop through each team in the API response.
# We filter only real NBA franchises because the API may include
# non-NBA or inactive teams.
# Retrun only requiered fields from teams (team_id, team_name, conference, division)
for team in teams_data['response']:
    if team.get('nbaFranchise') == True:
        # Extract only relevant fields needed for analysis.
        # We ignore unnecessary metadata (logos, alternate leagues, etc.)

        teams.append({
            'team_id': team['id'],
            'team_name': team['name'],
            # Extract conference and division from nested structure safely
            # using .get() to avoid errors if keys are missing.
            'conference': team.get('leagues', {}).get('standard', {}).get('conference'),
            'division': team.get('leagues', {}).get('standard', {}).get('division')
        })

# Convert cleaned list into a structured tabular format (DataFrame)
# to make it ready for SQL loading (DuckDB) and analysis.
teams_df = pd.DataFrame(teams)
print(' ')
print(f"   {len(teams_df)} NBA teams found in the teams data!")

# ********************************************************************
# 4. Fetching games data from games endpoint
# ********************************************************************
print("******************************************************")
print("4. Fetching games data from games endpoint:")

# Purpose:
# Retrieve game-level data for selected seasons in order to build the
# main fact table used for SQL analysis.
#
# This dataset will support calculations such as:
# - win/loss records
# - scoring trends
# - conference performance
# - average points scored and allowed
# - margin of victory analysis

# Initialize an empty list to store cleaned game records
# from multiple seasons before converting to a DataFrame.
all_games = []
# Pick seasons you wanted to have
print(' ')
print('A decade of data (10 years) from 2016 to 2025 are being fetched:')
seasons = list(range(2016, 2026))

# Loop through each selected season and request data separately.
# Pulling one season at a time keeps requests manageable and
# simplifies troubleshooting if an API call fails.
for season in seasons:
    print(f"   Fetching season: {season}...")

    # Build the API request URL with query parameters:
    # season = selected year
    # league = standard NBA league only
    url = f"https://v2.nba.api-sports.io/games?season={season}&league=standard"
    response = requests.get(url, headers=HEADERS)
    games_data = response.json()
    
    for game in games_data.get('response', []):
        
        # Extract only fields required for downstream SQL analysis.
        # Nested JSON values are accessed safely using chained .get()
        # to avoid key errors if fields are missing.

        all_games.append({
            'game_id': game.get('id'),
            'season': game.get('season'),

            # Home and away team names
            'date': game.get('date', {}).get('start'),

            # Home and away team names
            'home_team': game.get('teams', {}).get('home', {}).get('name'),
            'away_team': game.get('teams', {}).get('visitors', {}).get('name'),

            # Final points scored by each team
            'home_score': game.get('scores', {}).get('home', {}).get('points'),
            'away_score': game.get('scores', {}).get('visitors', {}).get('points')
        })
    
    # Pause briefly between API requests to respect rate limits
    # and reduce risk of throttling.
    time.sleep(1)  # Be nice to the API

# Convert collected records into tabular structure for
# DuckDB loading, parquet export, and SQL analysis.
games_df = pd.DataFrame(all_games)

# Print final row count as a simple validation check.
print(' ')
print(f"   {len(teams_df)} total games found!")


# ********************************************************************
# 5. Save cleaned datasets to DuckDB database and Parquet files
# ********************************************************************
print("******************************************************")
print("5. Save cleaned datasets to duckdb database and Parquet files:")
# Purpose:
# Store the processed data in two formats: 1. DuckDB and 2. Parquet


# Connect to DuckDB
# If the file does not already exist, DuckDB creates it automatically.
conn = duckdb.connect('nba_data.duckdb')

print("\n Data of teams and games saved as duckdb file.")
print("    It shows as nba_data.duckdb in the folder containg this code.")

# **********************
# Save Teams Table
# Create (or replace) a SQL table named 'teams'
# using the cleaned pandas DataFrame.
# This makes the data immediately queryable with SQL.
conn.execute("""
CREATE OR REPLACE TABLE teams AS
SELECT * FROM teams_df
""")

# Export the same teams dataset to Parquet format.
# index=False prevents pandas row numbers being saved
# as an unnecessary column.
teams_df.to_parquet('teams.parquet', index=False)

print("\n Data of teams saved as parquet file.")
print("    It shows as teams.parquet in the folder containg this code.")

# **********************
# Save games Table

# Create (or replace) a SQL table named 'games'
# containing the cleaned historical game records.
# This will be the main fact table for performance analysis.
conn.execute("""
CREATE OR REPLACE TABLE games AS
SELECT * FROM games_df
""")

# Export games data to Parquet for efficient storage
# and easy reuse in external tools.
games_df.to_parquet('games.parquet', index=False)

print("\n Data of games saved as parquet file.")
print("    It shows as games.parquet in the folder containg this code.")

# Close database connection after all writes complete.
# Good practice to release resources cleanly.
conn.close()