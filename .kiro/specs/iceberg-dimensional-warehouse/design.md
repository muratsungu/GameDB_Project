# Design Document: Iceberg Dimensional Warehouse

## Overview

This document describes the design for a Python-based ETL pipeline that transforms raw RAWG game data from Parquet files into a dimensional data warehouse using Apache Iceberg table format. The system implements a star schema optimized for analytical queries with fact and dimension tables stored in MinIO and managed by an Iceberg catalog.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Raw Parquet   │
│   Files (MinIO) │
│   raw/*.parquet │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   ETL Pipeline (Python Script)      │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  1. Raw Data Reader          │  │
│  │     - Read from MinIO        │  │
│  │     - Parse nested structures│  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  2. Dimension Builder        │  │
│  │     - Extract unique entities│  │
│  │     - Assign surrogate keys  │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  3. Fact Builder             │  │
│  │     - Create fact records    │  │
│  │     - Map to dimension keys  │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  4. Iceberg Writer           │  │
│  │     - Register tables        │  │
│  │     - Write to warehouse     │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Iceberg Catalog                   │
│   (REST or SQL)                     │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Iceberg Tables (MinIO)            │
│   warehouse/rawg_warehouse/*        │
│                                     │
│   - dim_platform                    │
│   - dim_store                       │
│   - dim_genre                       │
│   - dim_tag                         │
│   - dim_esrb_rating                 │
│   - dim_date                        │
│   - fact_games                      │
│   - bridge_game_platform            │
│   - bridge_game_store               │
│   - bridge_game_genre               │
│   - bridge_game_tag                 │
└─────────────────────────────────────┘
```

### Component Interaction Flow

1. **Raw Data Reader** reads Parquet files from MinIO and loads into pandas DataFrames
2. **Dimension Builder** extracts unique entities, assigns surrogate keys, creates dimension DataFrames
3. **Fact Builder** creates fact records with metrics and foreign key references
4. **Iceberg Writer** converts DataFrames to PyArrow tables and writes to Iceberg catalog

## Components and Interfaces

### 1. Configuration Module

**Purpose**: Centralize all configuration parameters

**Class**: `WarehouseConfig`

```python
class WarehouseConfig:
    # MinIO Configuration
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    raw_prefix: str = "raw/"
    
    # Iceberg Configuration
    catalog_type: str  # "rest" (for Nessie/generic REST) or "sql"
    catalog_uri: str  # Nessie: http://localhost:19120/api/v1
    warehouse_path: str
    namespace: str = "rawg_warehouse"
    
    # Nessie-specific (optional)
    nessie_auth_token: Optional[str] = None
    nessie_ref: str = "main"  # Nessie branch/tag
    
    # Processing Configuration
    state_file: Path
    batch_size: int = 10000
```

**Methods**:
- `from_env()`: Load configuration from environment variables
- `from_file(path)`: Load configuration from YAML/JSON file
- `validate()`: Validate all required parameters are set

### 2. Raw Data Reader Module

**Purpose**: Read and parse raw Parquet files from MinIO

**Class**: `RawDataReader`

```python
class RawDataReader:
    def __init__(self, config: WarehouseConfig, s3_client)
    
    def list_raw_files(self) -> List[str]
    def read_parquet_from_s3(self, object_key: str) -> pd.DataFrame
    def get_unprocessed_files(self, processed_files: Set[str]) -> List[str]
    def load_all_raw_data(self) -> pd.DataFrame
```

**Key Logic**:
- List all objects in MinIO with 'raw/' prefix
- Download Parquet files to memory using boto3
- Read into pandas DataFrame using `pd.read_parquet(BytesIO(data))`
- Concatenate multiple files into single DataFrame
- Deduplicate based on game 'id' field

### 3. Dimension Builder Module

**Purpose**: Extract and build dimension tables with surrogate keys

**Class**: `DimensionBuilder`

```python
class DimensionBuilder:
    def __init__(self, raw_df: pd.DataFrame)
    
    def build_dim_platform(self) -> pd.DataFrame
    def build_dim_store(self) -> pd.DataFrame
    def build_dim_genre(self) -> pd.DataFrame
    def build_dim_tag(self) -> pd.DataFrame
    def build_dim_esrb_rating(self) -> pd.DataFrame
    def build_dim_date(self, start_year: int, end_year: int) -> pd.DataFrame
    def build_all_dimensions(self) -> Dict[str, pd.DataFrame]
```

**Dimension Extraction Logic**:

For each dimension (platform, store, genre, tag):
1. Iterate through raw DataFrame rows
2. Extract nested array field (e.g., `platforms`)
3. Parse each element to get natural key (e.g., platform id, name, slug)
4. Collect unique entities in a set
5. Convert to DataFrame with surrogate key (auto-increment starting from 1)
6. Return dimension DataFrame

**Example for dim_platform**:
```python
def build_dim_platform(self) -> pd.DataFrame:
    platforms = []
    for idx, row in self.raw_df.iterrows():
        if pd.notna(row['platforms']):
            for p in row['platforms']:
                platform_data = p.get('platform', {})
                platforms.append({
                    'platform_key': platform_data.get('id'),
                    'name': platform_data.get('name'),
                    'slug': platform_data.get('slug')
                })
    
    # Deduplicate and assign surrogate keys
    df = pd.DataFrame(platforms).drop_duplicates(subset=['platform_key'])
    df.insert(0, 'platform_id', range(1, len(df) + 1))
    return df
```

**dim_date Logic**:
- Generate all dates from start_year to end_year
- Extract year, quarter, month, day, day_of_week
- Use date string as natural key (YYYY-MM-DD)
- Assign surrogate key (date_id)

### 4. Bridge Table Builder Module

**Purpose**: Create bridge tables for many-to-many relationships

**Class**: `BridgeTableBuilder`

```python
class BridgeTableBuilder:
    def __init__(self, raw_df: pd.DataFrame, dimensions: Dict[str, pd.DataFrame])
    
    def build_bridge_game_platform(self) -> pd.DataFrame
    def build_bridge_game_store(self) -> pd.DataFrame
    def build_bridge_game_genre(self) -> pd.DataFrame
    def build_bridge_game_tag(self) -> pd.DataFrame
    def build_all_bridges(self) -> Dict[str, pd.DataFrame]
```

**Bridge Table Logic**:

For each game and its associated dimension entities:
1. Get game_id from raw data
2. Extract nested array (e.g., platforms)
3. For each entity in array, lookup surrogate key from dimension table
4. Create bridge record: (game_id, dimension_surrogate_key)
5. Deduplicate bridge records

**Example for bridge_game_platform**:
```python
def build_bridge_game_platform(self) -> pd.DataFrame:
    dim_platform = self.dimensions['dim_platform']
    platform_lookup = dict(zip(dim_platform['platform_key'], 
                               dim_platform['platform_id']))
    
    bridges = []
    for idx, row in self.raw_df.iterrows():
        game_id = row['id']
        if pd.notna(row['platforms']):
            for p in row['platforms']:
                platform_key = p.get('platform', {}).get('id')
                platform_id = platform_lookup.get(platform_key)
                if platform_id:
                    bridges.append({
                        'game_id': game_id,
                        'platform_id': platform_id
                    })
    
    return pd.DataFrame(bridges).drop_duplicates()
```

### 5. Fact Table Builder Module

**Purpose**: Create fact table with metrics and foreign keys

**Class**: `FactTableBuilder`

```python
class FactTableBuilder:
    def __init__(self, raw_df: pd.DataFrame, dimensions: Dict[str, pd.DataFrame])
    
    def build_fact_games(self) -> pd.DataFrame
    def _lookup_date_key(self, date_str: str) -> Optional[int]
    def _lookup_esrb_key(self, esrb_data: dict) -> Optional[int]
```

**Fact Table Schema**:
```
fact_games:
  - game_id (PK)
  - date_id (FK to dim_date, based on 'released' field)
  - esrb_id (FK to dim_esrb_rating)
  
  # Degenerate Dimensions
  - slug
  - name
  - released
  - updated
  - background_image
  - tba
  
  # Additive Metrics
  - playtime
  - ratings_count
  - reviews_count
  - reviews_text_count
  - added
  - suggestions_count
  
  # Semi-Additive Metrics
  - rating
  - rating_top
  - metacritic
  - community_rating
  
  # Additional Attributes
  - saturated_color
  - dominant_color
```

**Fact Building Logic**:
1. Iterate through raw DataFrame
2. Extract game_id as primary key
3. Lookup date_id from dim_date using 'released' field
4. Lookup esrb_id from dim_esrb_rating using 'esrb_rating' field
5. Extract all metrics and degenerate dimensions
6. Handle null values appropriately
7. Return fact DataFrame

### 6. Iceberg Catalog Manager Module

**Purpose**: Manage Iceberg catalog connection and table registration

**Class**: `IcebergCatalogManager`

```python
class IcebergCatalogManager:
    def __init__(self, config: WarehouseConfig)
    
    def connect(self) -> Catalog
    def create_namespace(self, namespace: str)
    def table_exists(self, table_name: str) -> bool
    def create_table(self, table_name: str, schema: Schema, 
                     partition_spec: Optional[PartitionSpec] = None) -> Table
    def load_table(self, table_name: str) -> Table
```

**Catalog Connection Logic**:

For Nessie catalog (used with Dremio):
```python
catalog_config = {
    'type': 'rest',
    'uri': self.config.catalog_uri,  # Nessie REST endpoint
    'warehouse': self.config.warehouse_path,
    's3.endpoint': self.config.minio_endpoint,
    's3.access-key-id': self.config.minio_access_key,
    's3.secret-access-key': self.config.minio_secret_key,
    's3.path-style-access': 'true',
    's3.region': 'us-east-1',
}

# Optional: Nessie authentication
if self.config.nessie_auth_token:
    catalog_config['token'] = self.config.nessie_auth_token

catalog = load_catalog('nessie_catalog', **catalog_config)
```

For generic REST catalog:
```python
catalog_config = {
    'type': 'rest',
    'uri': self.config.catalog_uri,
    's3.endpoint': self.config.minio_endpoint,
    's3.access-key-id': self.config.minio_access_key,
    's3.secret-access-key': self.config.minio_secret_key,
    's3.path-style-access': 'true',
}
catalog = load_catalog('warehouse_catalog', **catalog_config)
```

For SQL catalog:
```python
catalog_config = {
    'type': 'sql',
    'uri': self.config.catalog_uri,  # e.g., postgresql://...
    'warehouse': self.config.warehouse_path,
    's3.endpoint': self.config.minio_endpoint,
    's3.access-key-id': self.config.minio_access_key,
    's3.secret-access-key': self.config.minio_secret_key,
}
catalog = load_catalog('warehouse_catalog', **catalog_config)
```

**Note on Dremio Integration**:
- Dremio uses Nessie as its catalog backend
- Tables created via PyIceberg will be visible in Dremio's UI
- Dremio can query the Iceberg tables directly from MinIO
- Ensure Dremio has a source configured pointing to the same MinIO bucket
- The warehouse path should match between PyIceberg and Dremio configuration

### 7. Iceberg Schema Definitions Module

**Purpose**: Define Iceberg schemas for all tables

**Class**: `SchemaDefinitions`

```python
class SchemaDefinitions:
    @staticmethod
    def dim_platform_schema() -> Schema
    
    @staticmethod
    def dim_store_schema() -> Schema
    
    @staticmethod
    def dim_genre_schema() -> Schema
    
    @staticmethod
    def dim_tag_schema() -> Schema
    
    @staticmethod
    def dim_esrb_rating_schema() -> Schema
    
    @staticmethod
    def dim_date_schema() -> Schema
    
    @staticmethod
    def fact_games_schema() -> Schema
    
    @staticmethod
    def bridge_schema(game_fk: str, dim_fk: str) -> Schema
```

**Example Schema Definitions**:

```python
@staticmethod
def dim_platform_schema() -> Schema:
    return Schema(
        NestedField(1, "platform_id", IntegerType(), required=True),
        NestedField(2, "platform_key", IntegerType(), required=False),
        NestedField(3, "name", StringType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
    )

@staticmethod
def fact_games_schema() -> Schema:
    return Schema(
        NestedField(1, "game_id", IntegerType(), required=True),
        NestedField(2, "date_id", IntegerType(), required=False),
        NestedField(3, "esrb_id", IntegerType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
        NestedField(5, "name", StringType(), required=False),
        NestedField(6, "released", StringType(), required=False),
        NestedField(7, "updated", StringType(), required=False),
        NestedField(8, "playtime", IntegerType(), required=False),
        NestedField(9, "rating", FloatType(), required=False),
        NestedField(10, "rating_top", IntegerType(), required=False),
        NestedField(11, "ratings_count", IntegerType(), required=False),
        NestedField(12, "reviews_count", IntegerType(), required=False),
        NestedField(13, "reviews_text_count", IntegerType(), required=False),
        NestedField(14, "added", IntegerType(), required=False),
        NestedField(15, "metacritic", IntegerType(), required=False),
        NestedField(16, "suggestions_count", IntegerType(), required=False),
        NestedField(17, "community_rating", FloatType(), required=False),
        NestedField(18, "background_image", StringType(), required=False),
        NestedField(19, "tba", BooleanType(), required=False),
        NestedField(20, "saturated_color", StringType(), required=False),
        NestedField(21, "dominant_color", StringType(), required=False),
    )
```

### 8. Iceberg Table Writer Module

**Purpose**: Write DataFrames to Iceberg tables

**Class**: `IcebergTableWriter`

```python
class IcebergTableWriter:
    def __init__(self, catalog_manager: IcebergCatalogManager)
    
    def write_dimension(self, dim_name: str, df: pd.DataFrame, 
                        schema: Schema, mode: str = 'overwrite')
    def write_fact(self, df: pd.DataFrame, schema: Schema, 
                   partition_spec: PartitionSpec, mode: str = 'overwrite')
    def write_bridge(self, bridge_name: str, df: pd.DataFrame, 
                     schema: Schema, mode: str = 'overwrite')
    def write_all_tables(self, dimensions: Dict[str, pd.DataFrame],
                         bridges: Dict[str, pd.DataFrame],
                         fact: pd.DataFrame)
```

**Write Logic**:

1. Convert pandas DataFrame to PyArrow Table
2. Check if Iceberg table exists
3. If not exists, create table with schema
4. If exists and mode='overwrite', truncate and append
5. If exists and mode='append', append new data
6. Write PyArrow table to Iceberg table

```python
def write_dimension(self, dim_name: str, df: pd.DataFrame, 
                    schema: Schema, mode: str = 'overwrite'):
    table_name = f"{self.catalog_manager.config.namespace}.{dim_name}"
    
    # Convert to PyArrow
    arrow_table = pa.Table.from_pandas(df, schema=schema.as_arrow())
    
    # Create or load table
    if not self.catalog_manager.table_exists(dim_name):
        table = self.catalog_manager.create_table(dim_name, schema)
    else:
        table = self.catalog_manager.load_table(dim_name)
        if mode == 'overwrite':
            table.delete(delete_filter=AlwaysTrue())
    
    # Write data
    table.append(arrow_table)
    print(f"Written {len(df)} rows to {table_name}")
```

**Partitioning for fact_games**:
```python
# Partition by release year
partition_spec = PartitionSpec(
    PartitionField(
        source_id=6,  # 'released' field
        field_id=1000,
        transform=year,
        name="released_year"
    )
)
```

### 9. Processing State Manager Module

**Purpose**: Track processed files for incremental processing

**Class**: `ProcessingStateManager`

```python
class ProcessingStateManager:
    def __init__(self, state_file: Path)
    
    def load_state(self) -> Dict
    def save_state(self, state: Dict)
    def mark_file_processed(self, file_key: str)
    def get_processed_files(self) -> Set[str]
    def is_file_processed(self, file_key: str) -> bool
```

**State File Format** (JSON):
```json
{
  "processed_files": [
    "raw/rawg_games_20251117_133216.parquet",
    "raw/rawg_games_20251117_133751.parquet"
  ],
  "last_run": "2025-11-24T10:30:00",
  "total_games_processed": 15000,
  "tables_created": [
    "dim_platform",
    "dim_store",
    "dim_genre",
    "dim_tag",
    "dim_esrb_rating",
    "dim_date",
    "fact_games",
    "bridge_game_platform",
    "bridge_game_store",
    "bridge_game_genre",
    "bridge_game_tag"
  ]
}
```

### 10. Main Orchestrator Module

**Purpose**: Orchestrate the entire ETL pipeline

**Class**: `WarehouseETL`

```python
class WarehouseETL:
    def __init__(self, config: WarehouseConfig)
    
    def run(self, incremental: bool = True)
    def _initialize_components(self)
    def _read_raw_data(self) -> pd.DataFrame
    def _build_dimensions(self, raw_df: pd.DataFrame) -> Dict[str, pd.DataFrame]
    def _build_bridges(self, raw_df: pd.DataFrame, 
                       dimensions: Dict) -> Dict[str, pd.DataFrame]
    def _build_fact(self, raw_df: pd.DataFrame, 
                    dimensions: Dict) -> pd.DataFrame
    def _write_to_iceberg(self, dimensions: Dict, bridges: Dict, fact: pd.DataFrame)
    def _generate_summary_report(self)
```

**Execution Flow**:
```python
def run(self, incremental: bool = True):
    print("=== Starting Warehouse ETL ===")
    start_time = datetime.now()
    
    # 1. Initialize
    self._initialize_components()
    
    # 2. Read raw data
    print("\n[1/5] Reading raw data from MinIO...")
    raw_df = self._read_raw_data()
    print(f"Loaded {len(raw_df)} games")
    
    # 3. Build dimensions
    print("\n[2/5] Building dimension tables...")
    dimensions = self._build_dimensions(raw_df)
    
    # 4. Build bridges
    print("\n[3/5] Building bridge tables...")
    bridges = self._build_bridges(raw_df, dimensions)
    
    # 5. Build fact
    print("\n[4/5] Building fact table...")
    fact = self._build_fact(raw_df, dimensions)
    
    # 6. Write to Iceberg
    print("\n[5/5] Writing to Iceberg warehouse...")
    self._write_to_iceberg(dimensions, bridges, fact)
    
    # 7. Update state
    if incremental:
        self.state_manager.save_state({...})
    
    # 8. Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    self._generate_summary_report(duration)
```

## Data Models

### Star Schema Diagram

```
                    ┌─────────────────┐
                    │   dim_platform  │
                    ├─────────────────┤
                    │ platform_id (PK)│
                    │ platform_key    │
                    │ name            │
                    │ slug            │
                    └────────┬────────┘
                             │
                             │ bridge_game_platform
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴────────┐  ┌────────┴────────┐  ┌───────┴────────┐
│   dim_store    │  │   fact_games    │  │   dim_genre    │
├────────────────┤  ├─────────────────┤  ├────────────────┤
│ store_id (PK)  │  │ game_id (PK)    │  │ genre_id (PK)  │
│ store_key      │  │ date_id (FK)    │  │ genre_key      │
│ name           │  │ esrb_id (FK)    │  │ name           │
│ slug           │  │ slug            │  │ slug           │
└────────┬───────┘  │ name            │  └────────┬───────┘
         │          │ released        │           │
         │          │ updated         │           │
         │          │ playtime        │           │
         │          │ rating          │           │
         │          │ ratings_count   │           │
         │          │ reviews_count   │           │
         │          │ metacritic      │           │
         │          │ ...             │           │
         │          └────────┬────────┘           │
         │                   │                    │
         │ bridge_game_store │ bridge_game_genre  │
         │                   │                    │
         └───────────────────┼────────────────────┘
                             │
                    ┌────────┴────────┐
                    │    dim_tag      │
                    ├─────────────────┤
                    │ tag_id (PK)     │
                    │ tag_key         │
                    │ name            │
                    │ slug            │
                    │ games_count     │
                    └─────────────────┘
                             │
                             │ bridge_game_tag
                             │
                    ┌────────┴────────┐
                    │ dim_esrb_rating │
                    ├─────────────────┤
                    │ esrb_id (PK)    │
                    │ esrb_key        │
                    │ name            │
                    │ slug            │
                    └─────────────────┘
                             │
                    ┌────────┴────────┐
                    │    dim_date     │
                    ├─────────────────┤
                    │ date_id (PK)    │
                    │ full_date       │
                    │ year            │
                    │ quarter         │
                    │ month           │
                    │ day             │
                    │ day_of_week     │
                    └─────────────────┘
```

### Table Relationships

- **fact_games** has many-to-one relationship with **dim_date** (via date_id)
- **fact_games** has many-to-one relationship with **dim_esrb_rating** (via esrb_id)
- **fact_games** has many-to-many relationship with **dim_platform** (via bridge_game_platform)
- **fact_games** has many-to-many relationship with **dim_store** (via bridge_game_store)
- **fact_games** has many-to-many relationship with **dim_genre** (via bridge_game_genre)
- **fact_games** has many-to-many relationship with **dim_tag** (via bridge_game_tag)

## Error Handling

### Error Categories

1. **Connection Errors**: MinIO or Iceberg catalog unavailable
   - Retry with exponential backoff (3 attempts)
   - Log error and exit gracefully

2. **Data Quality Errors**: Missing required fields, invalid data types
   - Log warning with row identifier
   - Skip problematic records
   - Continue processing

3. **Schema Errors**: Iceberg schema mismatch
   - Attempt schema evolution if supported
   - Otherwise, log error and exit

4. **Write Errors**: Failed to write to Iceberg table
   - Retry once
   - If fails, rollback transaction (if supported)
   - Log error and exit

### Error Handling Strategy

```python
try:
    # Main ETL logic
    etl.run()
except ConnectionError as e:
    logger.error(f"Failed to connect: {e}")
    sys.exit(1)
except DataQualityError as e:
    logger.warning(f"Data quality issue: {e}")
    # Continue with valid records
except SchemaError as e:
    logger.error(f"Schema mismatch: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
```

## Testing Strategy

### Unit Tests

1. **DimensionBuilder Tests**
   - Test extraction of unique platforms from nested arrays
   - Test surrogate key assignment
   - Test handling of null/missing values
   - Test deduplication logic

2. **FactTableBuilder Tests**
   - Test foreign key lookup
   - Test metric extraction
   - Test handling of missing dimensions

3. **BridgeTableBuilder Tests**
   - Test many-to-many relationship creation
   - Test deduplication of bridge records

4. **SchemaDefinitions Tests**
   - Test schema creation for all tables
   - Test data type mappings

### Integration Tests

1. **End-to-End Test**
   - Use sample Parquet file with known data
   - Run full ETL pipeline
   - Verify all tables created with correct row counts
   - Verify data integrity (foreign keys valid)

2. **Incremental Processing Test**
   - Run ETL with initial data
   - Add new Parquet file
   - Run ETL again in incremental mode
   - Verify only new data processed

3. **Iceberg Integration Test**
   - Verify tables registered in catalog
   - Verify data queryable via PyIceberg
   - Verify partitioning works correctly

### Test Data

Create synthetic test data with:
- 100 games
- 5 platforms
- 3 stores
- 10 genres
- 20 tags
- 3 ESRB ratings
- Date range: 2020-2025

## Performance Considerations

### Optimization Strategies

1. **Batch Processing**: Process data in batches of 10,000 records to manage memory
2. **Parallel Dimension Building**: Build dimensions concurrently using ThreadPoolExecutor
3. **Efficient Lookups**: Use dictionaries for dimension key lookups instead of DataFrame merges
4. **PyArrow Optimization**: Use PyArrow for efficient data serialization
5. **Partitioning**: Partition fact table by year for query performance

### Memory Management

- Stream large Parquet files instead of loading all at once
- Delete intermediate DataFrames after use
- Use generators for dimension extraction where possible

### Expected Performance

- Processing 100,000 games: ~5-10 minutes
- Dimension tables: < 1 minute
- Bridge tables: ~2-3 minutes
- Fact table: ~2-3 minutes
- Iceberg writes: ~2-3 minutes

## Deployment

### Prerequisites

1. MinIO server running and accessible
2. Nessie catalog server running (e.g., `docker run -p 19120:19120 projectnessie/nessie`)
3. Dremio connected to Nessie catalog and MinIO storage
4. Python 3.9+ with required packages installed

**Nessie + Dremio Setup**:
- Nessie provides version control for Iceberg tables
- Dremio uses Nessie as its catalog backend
- Configure Dremio Arctic source pointing to Nessie endpoint
- Configure Dremio S3 source pointing to MinIO bucket
- Tables created via PyIceberg will appear in Dremio automatically

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create `.env` file or set environment variables:

**For Nessie + Dremio setup**:
```
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password
MINIO_BUCKET=games

ICEBERG_CATALOG_TYPE=rest
ICEBERG_CATALOG_URI=http://localhost:19120/api/v1
ICEBERG_WAREHOUSE_PATH=s3://games/warehouse
ICEBERG_NAMESPACE=rawg_warehouse
NESSIE_REF=main
# NESSIE_AUTH_TOKEN=<token>  # Optional, if authentication enabled
```

**For generic REST catalog**:
```
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password
MINIO_BUCKET=games

ICEBERG_CATALOG_TYPE=rest
ICEBERG_CATALOG_URI=http://localhost:8181
ICEBERG_WAREHOUSE_PATH=s3://games/warehouse
ICEBERG_NAMESPACE=rawg_warehouse
```

### Execution

```bash
# Full processing (overwrite mode)
python warehouse_etl.py --mode full

# Incremental processing
python warehouse_etl.py --mode incremental

# With custom config
python warehouse_etl.py --config config.yaml
```

## Future Enhancements

1. **SCD Type 2 for Dimensions**: Track historical changes in dimension attributes
2. **Data Quality Dashboard**: Web UI showing data quality metrics
3. **Airflow Integration**: Schedule ETL as DAG
4. **Delta Processing**: Process only changed records using CDC from ingestion
5. **Aggregate Tables**: Pre-compute common aggregations for performance
6. **Data Lineage**: Track data flow from raw to warehouse tables
