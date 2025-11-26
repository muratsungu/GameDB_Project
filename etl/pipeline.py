"""Main ETL pipeline orchestrator."""
from datetime import datetime

from storage.minio_client import MinIOClient
from etl.dimensions import DimensionBuilder
from etl.bridges import BridgeBuilder
from etl.fact import FactBuilder
from etl.iceberg_catalog import IcebergCatalog
from etl.iceberg_writer import IcebergWriter
from utils.config import Config


class ETLPipeline:
    """Orchestrate the complete ETL pipeline: MinIO → Iceberg."""

    def __init__(self, config: Config):
        self.config = config
        self.minio = MinIOClient(
            config.minio_endpoint,
            config.minio_access_key,
            config.minio_secret_key,
            config.minio_bucket,
        )
        self.catalog = IcebergCatalog(
            config.catalog_uri,
            config.warehouse_path,
            config.minio_endpoint,
            config.minio_access_key,
            config.minio_secret_key,
            config.namespace,
        )
        self.writer = IcebergWriter(self.catalog)

    def run(self, mode: str = "overwrite"):
        """Execute the ETL pipeline."""
        start_time = datetime.now()
        print("=" * 70)
        print("ETL PIPELINE: MinIO → Iceberg")
        print("=" * 70)
        print(f"Mode: {mode}")
        print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Read raw data from MinIO
        print("\n[1/5] Reading raw data from MinIO...")
        raw_df = self.minio.read_all_parquet(self.config.raw_prefix)
        print(f"  Loaded {len(raw_df)} games")

        if raw_df.empty:
            print("No data to process.")
            return

        # Build dimensions
        print("\n[2/5] Building dimension tables...")
        dim_builder = DimensionBuilder(raw_df)
        dimensions = dim_builder.build_all()
        for name, df in dimensions.items():
            print(f"  {name}: {len(df)} records")

        # Build bridges
        print("\n[3/5] Building bridge tables...")
        bridge_builder = BridgeBuilder(raw_df, dimensions)
        bridges = bridge_builder.build_all()
        for name, df in bridges.items():
            print(f"  {name}: {len(df)} relationships")

        # Build fact
        print("\n[4/5] Building fact table...")
        fact_builder = FactBuilder(raw_df, dimensions)
        fact = fact_builder.build()
        print(f"  fact_games: {len(fact)} records")

        # Write to Iceberg
        print("\n[5/5] Writing to Iceberg warehouse...")
        self.writer.write_all(dimensions, bridges, fact, mode=mode)
        print("  All tables written")

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print("\n" + "=" * 70)
        print("ETL PIPELINE COMPLETED")
        print("=" * 70)
        print(f"Duration: {duration:.2f}s")
        print(f"Games processed: {len(fact):,}")
        print(f"Tables created: {len(dimensions) + len(bridges) + 1}")
        print("=" * 70)


def main():
    """Entry point for ETL pipeline."""
    config = Config.from_env()
    pipeline = ETLPipeline(config)
    pipeline.run(mode="overwrite")


if __name__ == "__main__":
    main()
