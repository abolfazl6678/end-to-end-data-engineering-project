-- ********************************************************************
-- Hadrian Business Analyst SQL Assessment
-- Name: Abolfazl Zolfaghari
-- Database: DuckDB
-- Source Files: games.parquet, teams.parquet
--
-- Assumptions:
-- 1. Last decade (10 years) = A decade of data from year 2016 to 2025
-- 2. NBA games do not end in ties
-- 3. Team names are consistent across tables
-- 4. Assumes games and teams tables already exist in nba_data.duckdb
-- 
-- Execution Instructions
-- Open nba_data.duckdb in DuckDB
-- Then run this script.
--
-- Required Tables:
-- games
-- teams


-- ********************************************************************
-- Pre-Analysis: Data Quality Validation
-- ********************************************************************
-- Purpose:
-- Validate source data integrity before performing analytical tasks.
-- This helps ensure results are accurate and trustworthy.


-- Check for duplicate game records
SELECT
    game_id,
    COUNT(*) AS row_count
FROM games
GROUP BY game_id
HAVING COUNT(*) > 1;


-- Check for missing score values
SELECT
    COUNT(*) AS missing_scores
FROM games
WHERE home_score IS NULL
   OR away_score IS NULL;


-- Check for team names in games table that do not exist
-- in the teams reference table
SELECT DISTINCT home_team AS unmatched_team
FROM games
WHERE home_team NOT IN (SELECT team_name FROM teams)

UNION

SELECT DISTINCT away_team
FROM games
WHERE away_team NOT IN (SELECT team_name FROM teams);


-- ********************************************************************
-- Task 1- Basic Data Extraction: Top 10 highest-scoring games in the last decade
-- ********************************************************************
-- Purpose:
-- Identify the highest-scoring NBA games over the most recent
-- 10-season period (year 2016 to year 2025).
-- This helps analyze offensive trends, unusually high-output games,
-- and periods where league scoring increased.


SELECT
    game_id,
    season,
    date,
    home_team,
    away_team,
    home_score,
    away_score,

    -- Calculate combined points scored in the game.
    -- This metric is used to rank the highest-scoring games.    

    home_score + away_score AS total_score
FROM games
-- Filter to only include games from the last decade (year 2016 to year 2025).
WHERE season BETWEEN 2016 AND 2025
-- Sort results from highest total score to lowest.
ORDER BY total_score DESC
-- Return only the top 10 highest-scoring games.
LIMIT 10;


-- ********************************************************************
-- Task 2- Win-Loss Records: Win-Loss Record for Each Team (Last Decade)
-- ********************************************************************

-- Purpose:
-- Calculate total wins and losses for every NBA team over the
-- last decade (year 2016 to year 2025).
-- Since each game contains both a home team and an away team,
-- we transform the data so that each team receives its own row.

WITH team_games AS (

    -- Home Team Results:
    -- For each game, assign one row to the home team.
    -- If home score > away score => win
    -- If home score < away score => loss

    SELECT
        home_team AS team,
        CASE
            WHEN home_score > away_score THEN 1
            ELSE 0
        END AS wins,

        CASE
            WHEN home_score < away_score THEN 1
            ELSE 0
        END AS losses
    FROM games
    
    -- Limit analysis to the last decade (year 2016 to year 2025)
    WHERE season BETWEEN 2016 AND 2025

    UNION ALL

    -- Away Team Results:
    -- Repeat the same logic for away teams.
    -- If away score > home score => win
    -- If away score < home score => loss

    SELECT
        away_team AS team,
        CASE 
            WHEN away_score > home_score THEN 1
            ELSE 0
        END,

        CASE 
            WHEN away_score < home_score THEN 1
            ELSE 0
        END

    FROM games

    -- Limit analysis to the last decade (year 2016 to year 2025)   
    WHERE season BETWEEN 2016 AND 2025

)

-- Final Aggregation:
-- Combine all home and away rows, then total wins
-- and losses for each team.

SELECT
    team,
    SUM(wins) AS total_wins,
    SUM(losses) AS total_losses
FROM team_games
GROUP BY team
-- Rank teams by most wins
ORDER BY total_wins DESC;


-- ********************************************************************
-- Task 3- Team Performance by Season: Average Points Scored by Team per Season
-- ********************************************************************

-- Purpose:
-- Measure offensive performance by calculating the average number
-- of points each team scores per game in each season over the
-- last decade (year 2016 to year 2025).
-- This helps compare teams across seasons and identify scoring trends.

WITH team_points AS (

    -- Home Team Scoring Records:
    -- Each game contributes one row for the home team,
    -- using the points scored at home.

    SELECT
        season,
        home_team AS team,
        home_score AS points

    FROM games

    -- limit analysis to the last decade (year 2016 to year 2025)
    WHERE season BETWEEN 2016 AND 2025

    UNION ALL

    -- Away Team Scoring Records:
    -- Each game also contributes one row for the away team,
    -- using the points scored on the road.

    SELECT
        season,
        away_team AS team,
        away_score AS points

    FROM games

    -- Limit analysis to the last decade (year 2016 to year 2025)
    WHERE season BETWEEN 2016 AND 2025

)

-- Final Aggregation:
-- Combine home and away scoring rows, then calculate 
-- average points scored per game for each team by season.

SELECT
    season,
    team,
    -- Rounded to 2 decimal places for cleaner reporting
    ROUND(AVG(points), 2) AS avg_points_scored
FROM team_points
GROUP BY
    season,
    team
-- Sort results alphabetically by team, then chronologically by season.
ORDER BY
    team,
    season;


-- ********************************************************************
-- Task 4- Conference Analysis: Conference with Most Wins
-- ********************************************************************

-- Purpose:
-- Determine whether the Eastern or Western Conference has recorded
-- the most total wins over the last decade (year 2016 to year 2025).
-- Since every game has exactly one winner, we first identify the
-- winning team for each game, then map that team to its conference
-- using the teams reference table.

WITH winners AS (

    -- Identify Winning Team for Each Game
    -- Compare final scores:
    -- If home score is higher, home team wins.
    -- Otherwise, away team wins.

    SELECT
        CASE
            WHEN home_score > away_score
                THEN home_team
            ELSE away_team
        END AS winning_team
    FROM games

    -- Limit analysis to games played in the last 10 seasons (year 2016 to year 2025).
    WHERE season BETWEEN 2016 AND 2025

)

-- Final Aggregation by Conference:
-- Join winning team names to the teams table in order
-- to retrieve conference membership (East / West),
-- then count total wins by conference.

SELECT
    t.conference,
    COUNT(*) AS total_wins
FROM winners w
JOIN teams t
    ON w.winning_team = t.team_name

-- Group results at conference level
GROUP BY t.conference

-- Rank conference with most wins first
ORDER BY total_wins DESC;


-- ********************************************************************
-- Task 5- Detailed Game Analysis: Highest Average Margin of Victory
-- ********************************************************************

-- Purpose:
-- Identify the team that wins games by the largest average margin
-- over the last decade.
-- Margin of victory = points scored by winning team
--                     minus points scored by losing team.
--
-- This metric helps measure how dominant a team is when it wins,
-- rather than only counting total wins.

WITH margins AS (

    -- Home Team Wins:
    -- If the home team wins, calculate the winning margin:
    -- home_score - away_score
    -- If the home team does not win, margin remains NULL.

    SELECT
        home_team AS team,
        CASE
            WHEN home_score > away_score
                THEN home_score - away_score
        END AS margin
    FROM games

    -- Limit analysis to the last decade (year 2016 to year 2025)
    WHERE season BETWEEN 2016 AND 2025

    UNION ALL

    -- Away Team Wins:
    -- If the away team wins, calculate the winning margin:
    -- away_score - home_score
    -- If the away team does not win, margin remains NULL.

    SELECT
        away_team AS team,
        CASE
            WHEN away_score > home_score
                THEN away_score - home_score
        END
    FROM games

    -- Limit analysis to the last 10 seasons (year 2016 to year 2025)
    WHERE season BETWEEN 2016 AND 2025

)

-- Final Aggregation:
-- Remove NULL rows (games not won by that side),
-- then calculate each team's average winning margin.

SELECT
    team,
    -- Rounded for cleaner reporting
    ROUND(AVG(margin), 2) AS avg_margin_of_victory
FROM margins
-- Keep only rows where a win occurred
WHERE margin IS NOT NULL
-- Aggregate at team level
GROUP BY team
-- Rank highest average margin first
ORDER BY avg_margin_of_victory DESC
-- Return the top-performing team only
LIMIT 1;


-- ********************************************************************
-- Task 6- Analyzing Team Performance Over Multiple Seasons:
-- Avg Points Scored and Allowed Per Season
-- ********************************************************************

-- Purpose:
-- Analyze team performance trends over the last decade (year 2016 to year 2025) by measuring:
-- 1. Average points scored per game
-- 2. Average points allowed per game
-- These two metrics help evaluate both offensive efficiency
-- and defensive performance by season.
-- CTEs are used to separate:
-- Step 1 -> Data preparation
-- Step 2 -> Aggregation and final reporting

WITH base_games AS (

    -- Home Team Perspective:
    -- Convert each game into a team-level row for the home team.
    -- points_scored  = points scored by home team
    -- points_allowed = points conceded to away team

    SELECT
        season,
        home_team AS team,
        home_score AS points_scored,
        away_score AS points_allowed
    FROM games

    -- Limit analysis to the last 10 seasons (year 2016 to year 2025)
    WHERE season BETWEEN 2016 AND 2025

    UNION ALL

    -- Away Team Perspective:
    -- Create a second row for the away team from the same game.
    -- points_scored  = away team points
    -- points_allowed = home team points

    SELECT
        season,
        away_team AS team,
        away_score AS points_scored,
        home_score AS points_allowed
    FROM games

    -- Limit analysis to the last 10 seasons (year 2016 to year 2025)
    WHERE season BETWEEN 2016 AND 2025

),


season_stats AS (

    -- Aggregate by Team and Season:
    -- Calculate average offensive and defensive metrics
    -- for each team in each season.

    SELECT
        team,
        season,
        AVG(points_scored) AS avg_points_scored,
        AVG(points_allowed) AS avg_points_allowed
    FROM base_games

    GROUP BY
        team,
        season

)


-- Final Output:
-- Present clean season-by-season team metrics.

SELECT
    team,
    season,
    -- Limit for cleaner reporting
    ROUND(avg_points_scored, 2) AS avg_points_scored,
    ROUND(avg_points_allowed, 2) AS avg_points_allowed
FROM season_stats

-- Sort alphabetically by team,
-- then chronologically by season.
ORDER BY
    team,
    season;