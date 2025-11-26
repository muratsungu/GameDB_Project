# Architecture Overview

## Data Flow

```
┌─────────────┐
│  RAWG API   │
└──────┬──────┘
       │ HTTP requests
       │ (with CDC tracking)
       ▼
┌─────────────┐
│  Ingestion  │
│   Module    │
└──────┬──────┘
       │ Parquet files
       ▼
┌─────────────┐
│    MinIO    │ ◄── Raw data storage (S3-compatible)
│   (raw/)    │
└──────┬──────┘
       │ Read parquet
       ▼
┌─────────────┐
│     ETL     │
│   Pipeline  │
└──────┬──────┘
       │ Dimensional model
       ▼
┌─────────────┐
│   Iceberg   │ ◄── Warehouse tables
│   Tables    │     (via Nessie catalog)
└──────┬──────┘
       │ SQL queries
       ▼
┌─────────────┐
│   Dremio    │ ◄── Query engine
└─────────────┘
```

## Module Structure

### `/ingestion` - Data Ingestion
- **rawg_fetcher.py**: RAWG API client with CDC (Change Data Capture)
- **ingest_pipeline.py**: Orchestrates fetching and uploading to MinIO

**Responsibilities:**
- Fetch game data from RAWG API
- Track processed games (CDC) to avoid duplicates
- Save as parquet files
- Upload to MinIO

### `/storage` - Storage Layer
- **minio_client.py**: MinIO S3 client wrapper

**Responsibilities:**
- Upload/download files to/from MinIO
- List files in buckets
- Read parquet files
- Deduplicate data

### `/etl` - ETL Transformations
- **dimensions.py**: Build dimension tables
- **bridges.py**: Build bridge tables (many-to-many)
- **fact.py**: Build fact table
- **iceberg_catalog.py**: Iceberg catalog manager
- **iceberg_schemas.py**: Schema definitions
- **iceberg_writer.py**: Write to Iceberg tables
- **pipeline.py**: ETL orchestrator

**Responsibilities:**
- Transform raw data into dimensional model
- Create surrogate keys
- Build relationships
- Write to Iceberg warehouse

### `/utils` - Utilities
- **config.py**: Configuration management
- **check_services.py**: Service health checks

### `/tests` - Test Suite
- **test_pipeline.py**: Unit tests for ETL components

## Data Model

### Star Schema

```
                    ┌──────────────┐
                    │  dim_date    │
                    └──────┬───────┘
                           │
    ┌──────────────┐       │       ┌──────────────┐
    │ dim_platform │       │       │  dim_store   │
    └──────┬───────┘       │       └──────┬───────┘
           │               │              │
           │               ▼              │
    ┌──────┴───────────────────────────┬─┴────┐
    │                                  │      │
    │         fact_games               │      │
    │  (game_id, metrics, FKs)         │      │
    │                                  │      │
    └──────┬───────────────────────────┬──────┘
           │               │              │
           │               │              │
    ┌──────┴───────┐       │       ┌──────┴───────┐
    │  dim_genre   │       │       │   dim_tag    │
    └──────────────┘       │       └──────────────┘
                           │
                    ┌──────┴───────┐
                    │ dim_esrb_    │
                    │   rating     │
                    └──────────────┘
```

### Bridge Tables (Many-to-Many)

```
fact_games ←→ bridge_game_platform ←→ dim_platform
fact_games ←→ bridge_game_store    ←→ dim_store
fact_games ←→ bridge_game_genre    ←→ dim_genre
fact_games ←→ bridge_game_tag      ←→ dim_tag
```

## Key Design Decisions

### 1. CDC (Change Data Capture)
- Tracks processed games by ID and update timestamp
- Prevents duplicate ingestion
- Enables incremental updates

### 2. Parquet Format
- Columnar storage for efficient queries
- Compression reduces storage costs
- Native support in pandas, PyArrow, Dremio

### 3. Iceberg Tables
- ACID transactions
- Schema evolution
- Time travel capabilities
- Efficient updates/deletes

### 4. Dimensional Model
- Star schema for analytical queries
- Surrogate keys for dimensions
- Bridge tables for many-to-many relationships
- Fact table contains metrics and foreign keys

### 5. Modular Architecture
- Clear separation of concerns
- Easy to test and maintain
- Reusable components
- Simple to extend

## Performance Considerations

### Ingestion
- Parallel fetching by month
- Rate limiting to respect API limits
- CDC to avoid reprocessing

### ETL
- Batch processing with pandas
- Efficient deduplication
- Minimal data movement

### Storage
- Parquet compression
- Partitioning by date (future enhancement)
- S3-compatible object storage

## Scalability

### Current Scale
- Handles ~50K games
- Processes in minutes
- Single-machine deployment

### Future Enhancements
- Spark for larger datasets
- Partitioned Iceberg tables
- Distributed processing
- Incremental ETL with state management
