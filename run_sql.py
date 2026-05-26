# import required libraries
import duckdb
import os

# Get current script directory to make code portable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build file paths dynamically (no hardcoding)
db_path = os.path.join(BASE_DIR, "nba_data.duckdb")
sql_path = os.path.join(BASE_DIR, "Abolfazl_Zolfaghari_Hadrian_SQL_Assessment.sql")

try:
    # Connect to DuckDB database.
    # It Opens database file relative to script location.
    con = duckdb.connect(db_path)

    # Load SQL file
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Execute full SQL script. It Runs all tasks (1–6) inside DuckDB.
    con.execute(sql_script)

    print("SQL Assessment file executed successfully")

    # Validation checks
    # Confirms data loaded correctly and pipeline works
    print("Games count:", con.sql("SELECT COUNT(*) FROM games").fetchall())
    print("Teams count:", con.sql("SELECT COUNT(*) FROM teams").fetchall())

except FileNotFoundError as e:
    print("FILE NOT FOUND ERROR:", e)

except duckdb.Error as e:
    print("DUCKDB ERROR (SQL issue):", e)

except Exception as e:
    print("UNEXPECTED ERROR:", e)