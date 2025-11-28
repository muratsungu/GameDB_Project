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