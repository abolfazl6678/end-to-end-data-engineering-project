# End to end data engineering project
Designed and developed a modern data pipeline and analytics platform using Python, 
SQL, DuckDB, and Streamlit to automate data ingestion, cleansing, validation, storage, and visualization of NBA 
statistics data. The project demonstrates ETL development, database design, analytics engineering, and dashboard 
deployment workflows. It consists of below objectives:

* Retrieve NBA data dynamically from a public API source
* Clean and transform the data using Python
* Store the data in DuckDB and Parquet formats
* Solve business analysis questions using SQL
* Create an interactive dashboard using Streamlit and Plotly

---

# Data Source

NBA data was retrieved using the API-Sports NBA API:

https://api-sports.io/documentation/nba/v2

The following endpoints were used:

* `/teams`
* `/games`

Only standard league NBA franchise teams were included, based on assessment requirements.

---

# Tools & Technologies Used

* python
* SQL
* json
* duckDB
* pandas
* time
* requests
* parquet
* streamlit
* plotly
* VS Code

---

# Project Files Structure

```text
End_to_end_data_engineering_project/
│── load_data.py
│── End_to end data engineering project_SQL.sql
│── run_sql.sql
│── nba_interactive.py
│── nba_data.duckdb
│── teams.parquet
│── games.parquet
│── README.md
└── screenshots/
      ├── team_trend.png
      ├── avg_points_scored_per_person.png
      └── conference_comparison_raw_data.png
```

---

# File Descriptions

## load_data.py

Python ETL script that:

* Connects to NBA API
* Validates API connection
* Downloads teams and games data
* Cleans and structures records
* Loading final data into DuckDB
* Exporting Parquet files

* Outputs created:
  * nba_data.duckdb
  * teams.parquet
  * games.parquet

---

## End_to end data engineering project_SQL.sql

Main SQL file containing solutions for:

1. Basic Data Extraction: Top 10 highest-scoring games in the last decade
2. Win-Loss Records: Win-Loss Record for Each Team (Last Decade)
3. Team Performance by Season: Average Points Scored by Team per Season
4. Conference Analysis: Conference with Most Wins
5. Detailed Game Analysis: Highest Average Margin of Victory
6. Analyzing Team Performance Over Multiple Seasons:Avg Points Scored and Allowed Per Season

  * Note: It also includes data quality checks in the beginging of the file.

---
## run_sql.py

Python automation script used to:

* Connects to DuckDB
* Loads the SQL assessment file
* Executes all SQL tasks automatically
* Performs validation checks
* Confirm row counts for games and teams tables

* Note: This provides a simple one-command method to run the full SQL solution.

---

## nba_interactive.py

Interactive dashboard created using Streamlit + Plotly.

Includes:

* Team filters
* Conference filters
* KPI metrics
* Team performance trends
* Conference comparison charts
* Raw data viewer

---

## nba_data.duckdb

Main analytical database file.
Contains structured relational tables including:
* games
* teams

Used for:

Interactive dashboard created using Streamlit + Plotly.

* SQL queries
* Dashboard analytics
* Data validation
* Fast local querying without external database software

---

## teams.parquet

Columnar data file containing cleaned NBA team data.

Includes fields such as:

* team_id
* team_name
* conference
* division

Used for:

* Portable storage
* Fast analytics workflows
* Alternative loading into BI tools / Python

---

## games.parquet

Columnar data file containing cleaned NBA game-level data.

Includes fields such as:

* game_id
* season
* date
* home_team
* away_team
* home_score
* away_score

Used for:

* Analytical processing
* Large dataset portability
* Fast loading into pandas / DuckDB / BI tools

---

## screenshots/

Contains dashboard preview images for quick review of the visualization.

---

## README.md

Project documentation containing:

* Project Overview
* Data Source
* Tools & Technologies Used
* Project Folder Structure
* File Descriptions
* How to Run This Project
* Data Assumptions
* Data Quality Checks Included
* Bonus Visualization Preview
* Notes

--


# How to Run This Project

## Step 1: Install Dependencies

```bash
pip install pandas time requests duckdb streamlit plotly
```

---

## Step 2: Load / Refresh Data

Run:

```bash
python load_data.py
```

This will:

* Connect to NBA API
* Download fresh data
* Rebuild DuckDB tables
* Recreate Parquet files

Outputs:

* nba_data.duckdb
* teams.parquet
* games.parquet

---

## Step 3: Review SQL Logic (Optional)

Open:

End_to end data engineering project_SQL.sql

This file contains solutions for all required SQL tasks.

---

## Step 4: Execute SQL via Python

Run:

```bash
python run_sql.py
```

This will:

* Connect to nba_data.duckdb
* Load the SQL assessment file
* Execute all SQL tasks
* Validate games and teams row counts
* Confirm successful execution

Note: DuckDB or any SQL editor can be used to execute sql assessment or run queries 
Note2: Queries in sql (End_to end data engineering project_SQL.sql) can be run manually as well.

---

## Step 5: Launch Bonus Dashboard

Run:

```bash
streamlit run nba_interactive.py
```

A browser page will open automatically with the interactive dashboard.

---

# Data Assumptions

* Only NBA franchise teams were included
* Only standard NBA league records were used
* Games data retrieved for selected seasons
* Team names are assumed consistent between tables
* Seasons interpreted as NBA season year values
* It was assumed that last decade = period between year 2016 to year 2025

---

# Data Quality Checks Included

* Duplicate game IDs
* Missing scores
* Teams in games table not found in teams table

---

# Bonus Visualization Preview

Screenshots are included inside:

```text
/screenshots
```

---

# Notes

* SQL queries were written with readability and business logic in mind.
* Python scripts were commented clearly to explain methodology.
* DuckDB was selected for lightweight local analytics performance.
* Parquet outputs were included for portability and scalability.
* Bonus dashboard demonstrates ability to communicate insights visually.

---

# Thank You

Thank you for reviewing my submission.
I appreciate the opportunity to complete this assessment.
