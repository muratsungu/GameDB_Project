# RAWG Games Data Pipeline

**Clean pipeline: RAWG API → MinIO → ETL → Parquet → Dremio**

## Overview

This pipeline fetches game data from RAWG API, transforms it into a dimensional model, and prepares it for analytics in Dremio.

## Architecture

```
RAWG API → Ingestion → MinIO (raw parquet)
                          ↓
                        ETL (Python)
                          ↓
                    MinIO (transformed parquet)
                          ↓
                    Dremio (SQL queries)
```

## Project Structure

```
/ingestion/          # Fetch from RAWG API
/storage/            # MinIO operations
/etl/                # Transform to dimensional model
/utils/              # Configuration
/tests/              # Test suite
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your RAWG API key
```

### 3. Start Services
```bash
# MinIO
docker run -d -p 9000:9000 -p 9001:9001 \
  --name minio \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=password \
  minio/minio server /data --console-address ':9001'

# Dremio
docker run -d -p 9047:9047 -p 31010:31010 -p 45678:45678 \
  --name dremio \
  dremio/dremio-oss
```

### 4. Run Pipeline

**Step 1: Ingest data from RAWG**
```bash
python run_ingestion.py
```
Fetches games from RAWG API (2024-2025) and stores in MinIO.

**Step 2: Transform to dimensional model**
```bash
python run_etl_parquet.py
```
Transforms raw data into dimensions, bridges, and fact tables.

### 5. Query in Dremio

**Configure Dremio:**
1. Open http://localhost:9047
2. Add MinIO source:
   - Type: Amazon S3
   - Access Key: `admin`
   - Secret Key: `password`
   - Advanced Options:
     - `fs.s3a.endpoint = localhost:9000`
     - `fs.s3a.path.style.access = true`
     - `fs.s3a.connection.ssl.enabled = false`

**Create tables:**
```sql
-- Example: Create dimension table
CREATE TABLE dim_platform
AS SELECT * FROM minio.games.transformed."dim_platform.parquet";

-- See dremio_setup.sql for all tables
```

**Query:**
```sql
SELECT name, rating, ratings_count
FROM fact_games
WHERE rating > 4.5
ORDER BY ratings_count DESC
LIMIT 20;
```

## Data Model

**Dimensions:**
- `dim_platform` - Gaming platforms
- `dim_store` - Digital stores
- `dim_genre` - Game genres
- `dim_tag` - Game tags
- `dim_esrb_rating` - Age ratings
- `dim_date` - Date dimension

**Bridges (many-to-many):**
- `bridge_game_platform`
- `bridge_game_store`
- `bridge_game_genre`
- `bridge_game_tag`

**Fact:**
- `fact_games` - Game metrics and attributes

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
```

## Development

**Run tests:**
```bash
pytest tests/
```

**Check services:**
```bash
python utils/check_services.py
```

## Files

- `run_ingestion.py` - Fetch data from RAWG API
- `run_etl_parquet.py` - Transform to dimensional model
- `dremio_setup.sql` - SQL to create tables in Dremio
- `.env.example` - Configuration template

## Troubleshooting

**MinIO not accessible:**
```bash
docker ps  # Check if running
docker logs minio  # Check logs
```

**No data in MinIO:**
```bash
# Run ingestion first
python run_ingestion.py
```

**Dremio can't connect to MinIO:**
- Verify endpoint: `localhost:9000`
- Check connection properties in Dremio source config
- Ensure `path.style.access = true`

## License

MIT
