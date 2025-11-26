# Implementation Plan

- [x] 1. Set up project structure and configuration management





  - Create `warehouse_etl.py` as main entry point
  - Create `config.py` module with `WarehouseConfig` class to load configuration from environment variables
  - Add configuration validation method
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2. Implement raw data reader module





  - Create `raw_data_reader.py` with `RawDataReader` class
  - Implement MinIO connection using boto3
  - Implement method to list all Parquet files in 'raw/' prefix
  - Implement method to read Parquet files from MinIO into pandas DataFrame
  - Implement deduplication logic based on game ID
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Implement dimension builder module








  - Create `dimension_builder.py` with `DimensionBuilder` class
  - Implement `build_dim_platform()` to extract unique platforms with surrogate keys
  - Implement `build_dim_store()` to extract unique stores with surrogate keys
  - Implement `build_dim_genre()` to extract unique genres with surrogate keys
  - Implement `build_dim_tag()` to extract unique tags with surrogate keys
  - Implement `build_dim_esrb_rating()` to extract unique ESRB ratings with surrogate keys
  - Implement `build_dim_date()` to generate date dimension for 2015-2025
  - Implement `build_all_dimensions()` orchestrator method
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 4. Implement bridge table builder module





  - Create `bridge_builder.py` with `BridgeTableBuilder` class
  - Implement `build_bridge_game_platform()` for game-platform many-to-many relationships
  - Implement `build_bridge_game_store()` for game-store many-to-many relationships
  - Implement `build_bridge_game_genre()` for game-genre many-to-many relationships
  - Implement `build_bridge_game_tag()` for game-tag many-to-many relationships
  - Implement deduplication logic for bridge records
  - Implement `build_all_bridges()` orchestrator method
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 5. Implement fact table builder module





  - Create `fact_builder.py` with `FactTableBuilder` class
  - Implement foreign key lookup methods for date and ESRB dimensions
  - Implement `build_fact_games()` to create fact records with all metrics
  - Handle null values appropriately for optional fields
  - Extract degenerate dimensions (slug, name, released, updated, etc.)
  - Extract additive metrics (playtime, ratings_count, reviews_count, etc.)
  - Extract semi-additive metrics (rating, metacritic, etc.)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6. Implement Iceberg schema definitions module





  - Create `iceberg_schemas.py` with `SchemaDefinitions` class
  - Define `dim_platform_schema()` with appropriate Iceberg field types
  - Define `dim_store_schema()` with appropriate Iceberg field types
  - Define `dim_genre_schema()` with appropriate Iceberg field types
  - Define `dim_tag_schema()` with appropriate Iceberg field types
  - Define `dim_esrb_rating_schema()` with appropriate Iceberg field types
  - Define `dim_date_schema()` with appropriate Iceberg field types
  - Define `fact_games_schema()` with all metrics and foreign keys
  - Define `bridge_schema()` generic method for bridge tables
  - _Requirements: 5.3, 5.4_

- [x] 7. Implement Iceberg catalog manager module





  - Create `iceberg_catalog.py` with `IcebergCatalogManager` class
  - Implement `connect()` method supporting Nessie REST catalog
  - Implement `create_namespace()` method to create Iceberg namespace
  - Implement `table_exists()` method to check if table exists in catalog
  - Implement `create_table()` method with schema and optional partition spec
  - Implement `load_table()` method to load existing Iceberg table
  - Handle connection errors with retry logic
  - _Requirements: 5.1, 5.2_

- [x] 8. Implement Iceberg table writer module





  - Create `iceberg_writer.py` with `IcebergTableWriter` class
  - Implement pandas to PyArrow conversion logic
  - Implement `write_dimension()` method for dimension tables
  - Implement `write_bridge()` method for bridge tables
  - Implement `write_fact()` method with partitioning by release year
  - Implement overwrite and append modes
  - Implement `write_all_tables()` orchestrator method
  - _Requirements: 5.5, 5.6, 5.7_

- [x] 9. Implement processing state manager module





  - Create `state_manager.py` with `ProcessingStateManager` class
  - Implement `load_state()` to read state from JSON file
  - Implement `save_state()` to write state to JSON file
  - Implement `mark_file_processed()` to track processed files
  - Implement `get_processed_files()` to retrieve processed file list
  - Implement `is_file_processed()` to check if file already processed
  - _Requirements: 7.1, 7.2, 7.5_

- [x] 10. Implement data quality validation module





  - Create `data_quality.py` with validation functions
  - Implement foreign key validation for fact table
  - Implement null value checking for required fields
  - Implement date format validation
  - Implement record count reporting
  - Implement error logging with descriptive messages
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 11. Implement main ETL orchestrator





  - Create main `WarehouseETL` class in `warehouse_etl.py`
  - Implement `_initialize_components()` to set up all modules
  - Implement `_read_raw_data()` to load raw Parquet files
  - Implement `_build_dimensions()` to create all dimension tables
  - Implement `_build_bridges()` to create all bridge tables
  - Implement `_build_fact()` to create fact table
  - Implement `_write_to_iceberg()` to write all tables to warehouse
  - Implement `_generate_summary_report()` to display execution summary
  - Implement `run()` method orchestrating full ETL pipeline
  - Add command-line argument parsing for full vs incremental mode
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 12. Implement incremental processing logic





  - Integrate `ProcessingStateManager` into main ETL flow
  - Filter out already processed files before reading
  - Implement upsert logic for fact table based on game_id
  - Implement append logic for new dimension records
  - Update state file after successful processing
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 13. Add logging and monitoring





  - Configure Python logging with appropriate levels
  - Add start/end time logging for each phase
  - Add progress indicators during processing
  - Add row count reporting for each table
  - Add error logging with context
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 14. Create requirements file and documentation





  - Update `requirements.txt` with all dependencies (pyiceberg, pandas, pyarrow, boto3, etc.)
  - Create `README_WAREHOUSE.md` with setup and usage instructions
  - Document Nessie + Dremio connection configuration
  - Add example `.env` file template
  - Document command-line usage examples
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 15. Integration testing and validation





  - Run ETL pipeline against sample data
  - Verify all tables created in Nessie catalog
  - Verify tables visible in Dremio UI
  - Query fact and dimension tables via Dremio to validate data
  - Verify foreign key relationships are correct
  - Verify partitioning works correctly for fact table
  - Test incremental processing with new data
  - _Requirements: 8.1, 8.2, 8.3, 8.4_
