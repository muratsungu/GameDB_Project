# Requirements Document

## Introduction

This document defines the requirements for transforming raw RAWG game data from Parquet files into a dimensional data warehouse using Apache Iceberg table format. The system will process nested JSON-like structures from the RAWG API and create a star schema with Fact and Dimension tables optimized for analytical queries.

## Glossary

- **Data Warehouse System**: The Python-based ETL pipeline that transforms raw RAWG game data into dimensional tables
- **Iceberg Catalog**: Apache Iceberg REST or SQL catalog service that manages table metadata
- **MinIO Storage**: S3-compatible object storage containing raw Parquet files and Iceberg warehouse data
- **Fact Table**: Central table containing measurable game metrics and foreign keys to dimension tables
- **Dimension Table**: Reference tables containing descriptive attributes for analysis
- **SCD Type 2**: Slowly Changing Dimension Type 2 - tracks historical changes with effective dates
- **Raw Data**: Unprocessed Parquet files in MinIO bucket under 'raw/' prefix
- **Warehouse Data**: Processed Iceberg tables in MinIO bucket under 'warehouse/' prefix

## Requirements

### Requirement 1: Dimensional Model Design

**User Story:** As a data analyst, I want a well-designed star schema, so that I can efficiently query and analyze game data across multiple dimensions.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL create a fact table named "fact_games" containing game metrics and dimension foreign keys
2. THE Data Warehouse System SHALL create dimension tables for platforms, stores, genres, tags, and ESRB ratings
3. THE Data Warehouse System SHALL create a date dimension table for temporal analysis
4. THE Data Warehouse System SHALL use surrogate keys for all dimension tables
5. THE Data Warehouse System SHALL maintain referential integrity between fact and dimension tables

### Requirement 2: Raw Data Processing

**User Story:** As a data engineer, I want to read and process raw Parquet files from MinIO, so that I can transform nested structures into normalized tables.

#### Acceptance Criteria

1. WHEN raw Parquet files exist in MinIO, THE Data Warehouse System SHALL read all files from the 'raw/' prefix
2. THE Data Warehouse System SHALL parse nested array fields including platforms, stores, genres, tags, and parent_platforms
3. THE Data Warehouse System SHALL handle missing or null values in optional fields
4. THE Data Warehouse System SHALL extract and flatten nested JSON structures into relational format
5. THE Data Warehouse System SHALL deduplicate records based on game ID before processing

### Requirement 3: Dimension Table Creation

**User Story:** As a data engineer, I want to create and populate dimension tables with unique entities, so that I can enable dimensional analysis.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL create dim_platform table with platform_id, platform_key, name, and slug fields
2. THE Data Warehouse System SHALL create dim_store table with store_id, store_key, name, and slug fields
3. THE Data Warehouse System SHALL create dim_genre table with genre_id, genre_key, name, and slug fields
4. THE Data Warehouse System SHALL create dim_tag table with tag_id, tag_key, name, slug, and games_count fields
5. THE Data Warehouse System SHALL create dim_esrb_rating table with esrb_id, esrb_key, name, and slug fields
6. THE Data Warehouse System SHALL create dim_date table with date_key, full_date, year, quarter, month, and day fields
7. THE Data Warehouse System SHALL assign unique surrogate keys to each dimension record
8. THE Data Warehouse System SHALL prevent duplicate dimension records based on natural keys

### Requirement 4: Fact Table Creation

**User Story:** As a data engineer, I want to create a fact table with game metrics and dimension references, so that I can support analytical queries.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL create fact_games table with game_id as primary key
2. THE Data Warehouse System SHALL include foreign keys to all dimension tables in fact_games
3. THE Data Warehouse System SHALL include additive metrics: playtime, ratings_count, reviews_count, added, suggestions_count
4. THE Data Warehouse System SHALL include semi-additive metrics: rating, rating_top, metacritic score
5. THE Data Warehouse System SHALL include degenerate dimensions: slug, name, released date, updated timestamp
6. THE Data Warehouse System SHALL create bridge tables for many-to-many relationships between games and dimensions

### Requirement 5: Iceberg Table Registration

**User Story:** As a data engineer, I want to register all tables in Apache Iceberg catalog, so that I can leverage Iceberg features like time travel and schema evolution.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL connect to Iceberg REST catalog or SQL catalog
2. THE Data Warehouse System SHALL create namespace "rawg_warehouse" if it does not exist
3. WHEN creating dimension tables, THE Data Warehouse System SHALL define appropriate Iceberg schemas with correct data types
4. WHEN creating fact table, THE Data Warehouse System SHALL define Iceberg schema with all metrics and foreign keys
5. THE Data Warehouse System SHALL write dimension data to Iceberg tables using PyArrow format
6. THE Data Warehouse System SHALL write fact data to Iceberg tables using PyArrow format
7. THE Data Warehouse System SHALL partition fact_games table by release year for query optimization

### Requirement 6: Bridge Table Management

**User Story:** As a data engineer, I want bridge tables for many-to-many relationships, so that I can accurately represent games with multiple platforms, genres, stores, and tags.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL create bridge_game_platform table linking game_id to platform_id
2. THE Data Warehouse System SHALL create bridge_game_store table linking game_id to store_id
3. THE Data Warehouse System SHALL create bridge_game_genre table linking game_id to genre_id
4. THE Data Warehouse System SHALL create bridge_game_tag table linking game_id to tag_id
5. THE Data Warehouse System SHALL prevent duplicate bridge table records for the same game-dimension combination

### Requirement 7: Incremental Processing

**User Story:** As a data engineer, I want incremental processing capability, so that I can efficiently update the warehouse with new data without full reprocessing.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL track processed raw files to avoid reprocessing
2. WHEN new raw Parquet files are detected, THE Data Warehouse System SHALL process only new files
3. THE Data Warehouse System SHALL append new dimension records without duplicating existing ones
4. THE Data Warehouse System SHALL upsert fact records based on game_id
5. THE Data Warehouse System SHALL maintain processing state in a metadata file

### Requirement 8: Data Quality and Validation

**User Story:** As a data engineer, I want data quality checks during processing, so that I can ensure warehouse data integrity.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL validate that all foreign keys in fact table reference existing dimension records
2. THE Data Warehouse System SHALL log warnings when encountering null values in required fields
3. THE Data Warehouse System SHALL validate date formats before inserting into dim_date table
4. THE Data Warehouse System SHALL count and report the number of records processed for each table
5. THE Data Warehouse System SHALL fail gracefully with descriptive error messages when data quality issues are detected

### Requirement 9: Configuration Management

**User Story:** As a data engineer, I want configurable parameters for catalog and storage connections, so that I can deploy the system in different environments.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL read MinIO connection parameters from environment variables or configuration file
2. THE Data Warehouse System SHALL read Iceberg catalog connection parameters from environment variables or configuration file
3. THE Data Warehouse System SHALL support both REST and SQL catalog types through configuration
4. THE Data Warehouse System SHALL allow configuration of warehouse namespace and table names
5. THE Data Warehouse System SHALL provide default values for all configuration parameters

### Requirement 10: Execution and Monitoring

**User Story:** As a data engineer, I want clear execution feedback and logging, so that I can monitor the ETL process and troubleshoot issues.

#### Acceptance Criteria

1. THE Data Warehouse System SHALL log the start and end time of each processing phase
2. THE Data Warehouse System SHALL display progress indicators during dimension and fact table creation
3. THE Data Warehouse System SHALL report row counts for each table after processing
4. THE Data Warehouse System SHALL log errors with sufficient context for debugging
5. THE Data Warehouse System SHALL provide a summary report at the end of execution showing all tables created and record counts
