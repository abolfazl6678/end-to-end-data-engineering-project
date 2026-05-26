# ********************************************************************
# Hadrian Business Analyst SQL Assessment (Bonus Question)
# Requirement:
# Create interactive visualizations using Plotly and/or Streamlit
#
# Candidate Name: Abolfazl Zolfaghari
# Database Used: DuckDB
#
# Purpose of this file:
# This script creates an interactive dashboard that reads NBA data
# already stored in DuckDB, performs SQL-based analytics, and displays
# charts in a browser using Streamlit.
#
# Assumptions:
# 1. The data has already been loaded and refreshed by running
#    load_data.py in the same project folder.
# 2. The file nba_data.duckdb exists in the project folder.
# 3. DuckDB contains at minimum:
#       - games table
#       - teams table
#
# Execution Instructions:
# 1. Open Command Prompt / PowerShell / VS Code Terminal
# 2. Change directory to the project folder:
#
#       cd "address to the folder"
#
# 3. Run the dashboard:
#
#       streamlit run nba_interactive_bonus.py
#
# 4. A browser page opens automatically and displays the dashboard.
# ********************************************************************

# ********************************************************************
# Import Required Libraries
# ********************************************************************
# streamlit:
# Used to build interactive web dashboards using Python only.
import streamlit as st

# duckdb:
# Used to connect to local DuckDB database and run SQL queries.
import duckdb

# plotly.express:
# Quick chart creation library for line charts / bar charts.
import plotly.express as px

# pandas:
# Used for data cleaning, joins, sorting, and reshaping tables.
import pandas as pd

# plotly.graph_objects:
# More advanced chart customization if needed.
import plotly.graph_objects as go


# ********************************************************************
# Streamlit Page Configuration
# ********************************************************************
# set_page_config controls browser tab title and page layout.
# layout="wide" gives more horizontal space for charts.
st.set_page_config(
    page_title="NBA Dashboard",
    layout="wide"
)

# Main title shown at top of dashboard page.
st.title("NBA Team Performance Dashboard")

# ********************************************************************
# Connect to DuckDB
# ********************************************************************
# Connect to local DuckDB file that stores cleaned NBA data.
# If file exists, it opens.
# If path is wrong, connection fails.
conn = duckdb.connect(
    r"C:\Users\K56C\Desktop\Abolfazl_Zolfaghari_Hadrian_Assessment\nba_data.duckdb"
)

# ********************************************************************
# Safety Check: Ensure Required Tables Exist
# ********************************************************************
# SHOW TABLES returns all tables currently inside DuckDB.
# fetchall() returns list of tuples.
tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]

# If games or teams table is missing:
# Show error in dashboard and stop execution safely.
if "games" not in tables or "teams" not in tables:
    st.error(
        "Missing required tables in DuckDB "
        "(games / teams). Please run load_data.py first."
    )
    st.stop()



# ********************************************************************
# Build Team Statistics Using SQL
# ********************************************************************
# Purpose:
# Create a season-level summary for every team:
#   - average points scored
#   - average points allowed
#
# Why CTE?
# Makes SQL cleaner and easier to explain.

df = conn.execute("""

WITH base_games AS (

    ----------------------------------------------------
    -- Home team perspective
    -- Each row becomes one team record
    ----------------------------------------------------
    SELECT
        season,
        home_team AS team,
        home_score AS points_scored,
        away_score AS points_allowed
    FROM games

    UNION ALL

    ----------------------------------------------------
    -- Away team perspective
    -- Same game contributes another row
    ----------------------------------------------------
    SELECT
        season,
        away_team AS team,
        away_score AS points_scored,
        home_score AS points_allowed
    FROM games
)

--------------------------------------------------------
-- Final aggregation:
-- Calculate average points by team and season
--------------------------------------------------------
SELECT
    team,
    season,
    AVG(points_scored)  AS avg_points_scored,
    AVG(points_allowed) AS avg_points_allowed
FROM base_games
GROUP BY team, season

""").fetchdf()

# fetchdf() converts SQL result directly into pandas dataframe.


# ********************************************************************
# Clean Season Values
# ********************************************************************
# Sometimes season may appear as float (2023.0).
# Convert to integer for cleaner chart labels.
df["season"] = df["season"].astype(float).astype(int)


# ********************************************************************
# Load Teams Table
# ********************************************************************
# teams table contains conference/division metadata.
teams_df = conn.execute(
    "SELECT * FROM teams"
).fetchdf()


# ********************************************************************
# Merge Team Metadata
# ********************************************************************
# Join performance table with teams table
# to add conference and division columns.
df = df.merge(
    teams_df,
    left_on="team",
    right_on="team_name",
    how="left"
)


# ********************************************************************
# Create Complete Season Range
# ********************************************************************
# Purpose:
# If a team has no row in one season,
# charts can shrink or misalign.
# We create full season list for consistency.

all_seasons = sorted(df["season"].unique())

# If no data exists, fallback values used.
min_season = min(all_seasons) if all_seasons else 2022
max_season = max(all_seasons) if all_seasons else 2024

# Example:
# [2021,2022,2023,2024]
complete_seasons = list(
    range(min_season, max_season + 1)
)


# ********************************************************************
# Sidebar Filters
# ********************************************************************
# Sidebar gives user interactive controls.

st.sidebar.header("Filters")

# Dropdown list of all teams.
team_list = sorted(df["team"].unique())

selected_team = st.sidebar.selectbox(
    "Select Team",
    team_list
)

# Dropdown list of conferences.
conference_list = ["All"] + sorted(
    df["conference"].dropna().unique().tolist()
)

selected_conf = st.sidebar.selectbox(
    "Select Conference",
    conference_list
)


# ********************************************************************
# Apply Filters
# ********************************************************************
# Keep only selected team.
filtered_df = df[df["team"] == selected_team]

# If conference selected, apply second filter.
if selected_conf != "All":
    filtered_df = filtered_df[
        filtered_df["conference"] == selected_conf
    ]

# Sort by season for proper chart order.
filtered_df = filtered_df.sort_values("season")


# ********************************************************************
# Fill Missing Seasons
# ********************************************************************
# Create dataframe containing all seasons.
complete_df = pd.DataFrame({
    "season": complete_seasons
})

# Left join ensures every season appears,
# even if no stats exist for selected team.
filtered_df_complete = complete_df.merge(
    filtered_df,
    on="season",
    how="left"
)


# ********************************************************************
# KPI Metrics Row
# ********************************************************************
# Create 3 columns across page.
col1, col2, col3 = st.columns(3)

# Show high-level metrics.
col1.metric("Teams", df["team"].nunique())
col2.metric("Seasons", df["season"].nunique())
col3.metric("Selected Team", selected_team)

# Horizontal divider line.
st.divider()


# ********************************************************************
# Chart 1: Offense vs Defense Trend
# ********************************************************************
st.subheader(f"{selected_team} Performance Trend")

# Create line chart with 2 metrics.
fig1 = px.line(
    filtered_df_complete,
    x="season",
    y=[
        "avg_points_scored",
        "avg_points_allowed"
    ],
    markers=True,
    title="Offense vs Defense Over Time"
)

# Improve axis readability.
fig1.update_xaxes(
    tickformat="d",          # integer labels
    dtick=1,                # show every season
    tickvals=complete_seasons,
    title_font=dict(size=24),
    tickfont=dict(size=18)
)

fig1.update_yaxes(
    title_font=dict(size=24),
    tickfont=dict(size=18)
)

# Improve title / legend / tooltip font.
fig1.update_layout(
    title_font=dict(size=18),
    legend_font=dict(size=16),
    legend_title_font=dict(size=18),
    hoverlabel=dict(font_size=12)
)

# Display chart.
st.plotly_chart(
    fig1,
    use_container_width=True
)


# ********************************************************************
# Chart 2: Average Points Scored
# ********************************************************************
fig2 = px.bar(
    filtered_df_complete,
    x="season",
    y="avg_points_scored",
    text_auto=True,
    title="Average Points Scored Per Season"
)

# Fixed bar width so bars do not resize
# when some seasons are missing.
fig2.update_traces(
    textfont_size=12,
    width=0.6
)

# Axis formatting.
fig2.update_xaxes(
    tickformat="d",
    dtick=1,
    tickvals=complete_seasons,
    title_font=dict(size=24),
    tickfont=dict(size=18),
    range=[min_season - 0.5, max_season + 0.5]
)

fig2.update_yaxes(
    title_font=dict(size=24),
    tickfont=dict(size=18)
)

fig2.update_layout(
    title_font=dict(size=18),
    hoverlabel=dict(font_size=12),
    bargap=0.2
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ********************************************************************
# Chart 3: Conference Comparison
# ********************************************************************
st.subheader("Conference Comparison")

# Calculate mean scoring by conference + season.
conf_df = df.groupby(
    ["conference", "season"]
)["avg_points_scored"].mean().reset_index()

conf_df = conf_df.sort_values("season")

# Build complete rows for each conference.
conferences = conf_df["conference"].unique()
complete_conf_list = []

for conference in conferences:

    conf_subset = conf_df[
        conf_df["conference"] == conference
    ]

    conf_complete = complete_df.merge(
        conf_subset,
        on="season",
        how="left"
    )

    conf_complete["conference"] = conference

    complete_conf_list.append(conf_complete)

# If data exists, plot grouped bars.
if complete_conf_list:

    conf_df_complete = pd.concat(
        complete_conf_list,
        ignore_index=True
    )

    fig3 = px.bar(
        conf_df_complete,
        x="season",
        y="avg_points_scored",
        color="conference",
        barmode="group",
        title="Conference Scoring Comparison",
        text_auto=True
    )

    # Fixed width grouped bars.
    fig3.update_traces(
        textfont_size=12,
        width=0.4
    )

    fig3.update_xaxes(
        tickformat="d",
        dtick=1,
        tickvals=complete_seasons,
        title_font=dict(size=24),
        tickfont=dict(size=18),
        range=[min_season - 0.5, max_season + 0.5]
    )

    fig3.update_yaxes(
        title_font=dict(size=24),
        tickfont=dict(size=18)
    )

    fig3.update_layout(
        title_font=dict(size=24),
        legend_font=dict(size=18),
        legend_title_font=dict(size=14),
        hoverlabel=dict(font_size=12),
        bargap=0.2,
        bargroupgap=0.1
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

else:
    st.warning(
        "No conference data available for comparison"
    )


# ********************************************************************
# Raw Data Viewer
# ********************************************************************
# Expandable section for reviewer to inspect rows.
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)


# ********************************************************************
# Close Database Connection
# ********************************************************************
# Good practice to release connection resources.
conn.close()