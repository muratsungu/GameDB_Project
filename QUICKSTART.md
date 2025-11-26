# Quick Start Guide

## Prerequisites

- Python 3.8+
- Docker (for MinIO and Nessie)

## 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your RAWG API key
```

## 2. Start Services

```bash
# Start MinIO
docker run -d -p 9000:9000 -p 9001:9001 \
  --name minio \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=password \
  minio/minio server /data --console-address ':9001'

# Start Nessie (Iceberg catalog)
docker run -d -p 19120:19120 \
  --name nessie \
  projectnessie/nessie
```

## 3. Check Services

```bash
python utils/check_services.py
```

## 4. Run Pipeline

### Step 1: Ingest Data (RAWG → MinIO)

```bash
python run_ingestion.py
```

This will:
- Fetch games from RAWG API (2024-2025)
- Save as parquet files
- Upload to MinIO bucket

### Step 2: Run ETL (MinIO → Iceberg)

```bash
python run_etl.py
```

This will:
- Read raw parquet from MinIO
- Build dimensional model
- Write to Iceberg tables

## 5. Query in Dremio

1. Open Dremio
2. Add Nessie source:
   - Type: Nessie
   - Endpoint: `http://localhost:19120/api/v1`
   - Authentication: None
3. Browse `rawg_warehouse` namespace
4. Query tables:

```sql
SELECT * FROM rawg_warehouse.fact_games LIMIT 10;

SELECT 
  g.name,
  p.name as platform
FROM rawg_warehouse.fact_games g
JOIN rawg_warehouse.bridge_game_platform b ON g.game_id = b.game_id
JOIN rawg_warehouse.dim_platform p ON b.platform_id = p.platform_id
LIMIT 10;
```

## Troubleshooting

**MinIO not accessible:**
- Check if container is running: `docker ps`
- Access console: http://localhost:9001 (admin/password)

**Nessie not accessible:**
- Check if container is running: `docker ps`
- Test endpoint: `curl http://localhost:19120/api/v1/config`

**No data in MinIO:**
- Run ingestion first: `python run_ingestion.py`
- Check MinIO console for `games` bucket

**ETL fails:**
- Ensure MinIO has data in `raw/` prefix
- Check Nessie is running
- Verify .env configuration
