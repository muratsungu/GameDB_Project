-- Dremio SQL Setup Script
-- Run these commands in Dremio after connecting MinIO source

-- ============================================
-- Step 1: Verify MinIO Connection
-- ============================================
-- Browse to your MinIO source in Dremio UI
-- Should see: minio > games > transformed

-- ============================================
-- Step 2: Query Transformed Parquet Files
-- ============================================

-- Test dimension tables
SELECT * FROM minio.games.transformed."dim_platform.parquet" LIMIT 10;
SELECT * FROM minio.games.transformed."dim_store.parquet" LIMIT 10;
SELECT * FROM minio.games.transformed."dim_genre.parquet" LIMIT 10;
SELECT * FROM minio.games.transformed."dim_tag.parquet" LIMIT 10;
SELECT * FROM minio.games.transformed."dim_esrb_rating.parquet" LIMIT 10;
SELECT * FROM minio.games.transformed."dim_date.parquet" LIMIT 10;

-- Test fact table
SELECT * FROM minio.games.transformed."fact_games.parquet" LIMIT 10;

-- ============================================
-- Step 3: Create Iceberg Tables in Nessie
-- ============================================

-- Create namespace (if needed)
-- CREATE NAMESPACE nessie.rawg_warehouse;

-- Dimension Tables
CREATE TABLE nessie.rawg_warehouse.dim_platform
AS SELECT * FROM minio.games.transformed."dim_platform.parquet";

CREATE TABLE nessie.rawg_warehouse.dim_store
AS SELECT * FROM minio.games.transformed."dim_store.parquet";

CREATE TABLE nessie.rawg_warehouse.dim_genre
AS SELECT * FROM minio.games.transformed."dim_genre.parquet";

CREATE TABLE nessie.rawg_warehouse.dim_tag
AS SELECT * FROM minio.games.transformed."dim_tag.parquet";

CREATE TABLE nessie.rawg_warehouse.dim_esrb_rating
AS SELECT * FROM minio.games.transformed."dim_esrb_rating.parquet";

CREATE TABLE nessie.rawg_warehouse.dim_date
AS SELECT * FROM minio.games.transformed."dim_date.parquet";

-- Bridge Tables
CREATE TABLE nessie.rawg_warehouse.bridge_game_platform
AS SELECT * FROM minio.games.transformed."bridge_game_platform.parquet";

CREATE TABLE nessie.rawg_warehouse.bridge_game_store
AS SELECT * FROM minio.games.transformed."bridge_game_store.parquet";

CREATE TABLE nessie.rawg_warehouse.bridge_game_genre
AS SELECT * FROM minio.games.transformed."bridge_game_genre.parquet";

CREATE TABLE nessie.rawg_warehouse.bridge_game_tag
AS SELECT * FROM minio.games.transformed."bridge_game_tag.parquet";

-- Fact Table
CREATE TABLE nessie.rawg_warehouse.fact_games
AS SELECT * FROM minio.games.transformed."fact_games.parquet";

-- ============================================
-- Step 4: Verify Iceberg Tables
-- ============================================

SELECT COUNT(*) as total_games FROM nessie.rawg_warehouse.fact_games;
SELECT COUNT(*) as total_platforms FROM nessie.rawg_warehouse.dim_platform;
SELECT COUNT(*) as total_genres FROM nessie.rawg_warehouse.dim_genre;

-- ============================================
-- Step 5: Example Analytical Queries
-- ============================================

-- Games by platform
SELECT 
    p.name as platform,
    COUNT(DISTINCT b.game_id) as game_count
FROM nessie.rawg_warehouse.bridge_game_platform b
JOIN nessie.rawg_warehouse.dim_platform p ON b.platform_id = p.platform_id
GROUP BY p.name
ORDER BY game_count DESC;

-- Top rated games
SELECT 
    name,
    rating,
    ratings_count,
    released
FROM nessie.rawg_warehouse.fact_games
WHERE rating IS NOT NULL
ORDER BY rating DESC, ratings_count DESC
LIMIT 20;

-- Games by genre
SELECT 
    g.name as genre,
    COUNT(DISTINCT b.game_id) as game_count,
    AVG(f.rating) as avg_rating
FROM nessie.rawg_warehouse.bridge_game_genre b
JOIN nessie.rawg_warehouse.dim_genre g ON b.genre_id = g.genre_id
JOIN nessie.rawg_warehouse.fact_games f ON b.game_id = f.game_id
WHERE f.rating IS NOT NULL
GROUP BY g.name
ORDER BY game_count DESC;

-- Games released by year
SELECT 
    d.year,
    COUNT(*) as games_released,
    AVG(f.rating) as avg_rating
FROM nessie.rawg_warehouse.fact_games f
JOIN nessie.rawg_warehouse.dim_date d ON f.date_id = d.date_id
GROUP BY d.year
ORDER BY d.year DESC;
