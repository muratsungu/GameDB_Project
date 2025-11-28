# TODO Roadmap for GameDB_Project

## Week 1 — Incremental Ingestion + Error Handling
- [ ] Create `state/state.json` to store last run timestamp
- [ ] Update ingestion logic to fetch only updated/changed records
- [ ] Add retry mechanism with exponential backoff for RAWG API
- [ ] Handle 429 (rate limit) responses
- [ ] Add structured JSON logging
- [ ] Update README with incremental ingestion details

## Week 2 — Data Lake Restructure + Partitioning
- [ ] Reorganize raw zone → `/raw/year=YYYY/month=MM/day=DD/`
- [ ] Implement partitioned write for processed zone
- [ ] Add Parquet optimizations (dictionary encoding, snappy compression)
- [ ] Update Dremio datasets to benefit from partition pruning
- [ ] Document partitioning strategy in README

## Week 3 — Docker Compose + Environment Setup
- [ ] Create `docker-compose.yaml` for MinIO + Dremio (+ optional Spark)
- [ ] Add `.env.development` and `.env.production`
- [ ] Implement config loader using Pydantic
- [ ] Update README with setup instructions

## Week 4 — Data Quality (DQ) + Testing
- [ ] Add Great Expectations or custom DQ framework
- [ ] Create DQ tests: null checks, duplicate checks, PK/FK checks
- [ ] Add unit tests for ingestion and ETL steps via pytest
- [ ] Add CI test step (GitHub Actions optional)
- [ ] Document data quality checks in README

## Week 5 — Pipeline Orchestration (Prefect)
- [ ] Build Prefect flow: ingestion → dq → etl → load
- [ ] Add scheduling (daily)
- [ ] Add logging/monitoring via Prefect UI
- [ ] Document orchestration layer in README

## Week 6 — Iceberg Integration (Optional but Strong)
- [ ] Configure MinIO-backed Iceberg catalog
- [ ] Convert processed Parquet tables to Iceberg tables
- [ ] Update ETL to write directly to Iceberg
- [ ] Configure Dremio Iceberg reflections
- [ ] Test time travel queries
- [ ] Document Iceberg upgrade in README

## Finalization
- [ ] Add architecture diagram (PNG)
- [ ] Add data model ERD
- [ ] Add sample Dremio queries
- [ ] Clean README and prepare portfolio version