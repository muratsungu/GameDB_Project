# RAWG Games Data Pipeline

Clean, modular data pipeline: **RAWG API → MinIO → ETL → Dremio**

## Architecture

```
RAWG API → MinIO (raw parquet) → ETL → Iceberg Tables → Dremio
```

## Project Structure

```
/ingestion          # Fetch data from RAWG API
  - rawg_fetcher.py       # API client with CDC
  - ingest_pipeline.py    # Ingestion orchestrator

/storage            # MinIO operations
  - minio_client.py       # S3 client wrapper

/etl                # Transform raw → dimensional model
  - dimensions.py         # Dimension table builders
  - bridges.py            # Bridge table builders
  - fact.py               # Fact table builder
  - iceberg_catalog.py    # Catalog manager
  - iceberg_schemas.py    # Schema definitions
  - iceberg_writer.py     # Write to Iceberg
  - pipeline.py           # ETL orchestrator

/utils              # Shared utilities
  - config.py             # Configuration

/tests              # Test suite
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start services:**
   ```bash
   # MinIO
   docker run -d -p 9000:9000 -p 9001:9001 \
     -e MINIO_ROOT_USER=admin \
     -e MINIO_ROOT_PASSWORD=password \
     minio/minio server /data --console-address ':9001'

   # Nessie (Iceberg catalog)
   docker run -d -p 19120:19120 projectnessie/nessie
   ```

## Usage

### 1. Ingest Data (RAWG → MinIO)

```bash
python -m ingestion.ingest_pipeline
```

Fetches games from RAWG API (2024-2025), saves as parquet, uploads to MinIO.

### 2. Run ETL (MinIO → Iceberg)

```bash
python -m etl.pipeline
```

Transforms raw data into dimensional model and writes to Iceberg tables.

### 3. Query in Dremio

Connect Dremio to Nessie catalog and query the `rawg_warehouse` namespace.

## Configuration

Environment variables (`.env`):

```bash
# RAWG API
RAWG_API_KEY=your_api_key

# MinIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password
MINIO_BUCKET=games

# Iceberg
ICEBERG_CATALOG_URI=http://localhost:19120/api/v1
ICEBERG_WAREHOUSE_PATH=s3://games/warehouse
ICEBERG_NAMESPACE=rawg_warehouse
```

## Data Model

**Dimensions:**
- `dim_platform` - Gaming platforms
- `dim_store` - Digital stores
- `dim_genre` - Game genres
- `dim_tag` - Game tags
- `dim_esrb_rating` - ESRB ratings
- `dim_date` - Date dimension

**Bridges (many-to-many):**
- `bridge_game_platform`
- `bridge_game_store`
- `bridge_game_genre`
- `bridge_game_tag`

**Fact:**
- `fact_games` - Game metrics and attributes

## Development

Run tests:
```bash
pytest tests/
```

Check services:
```bash
python utils/check_services.py
```
