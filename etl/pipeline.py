"""Main ETL pipeline orchestrator."""
from datetime import datetime

from storage.minio_client import MinIOClient
from etl.dimensions import DimensionBuilder
from etl.bridges import BridgeBuilder
from etl.fact import FactBuilder
from etl.parquet_writer import ParquetWriter
from utils.config import Config


class ETLPipeline:
    """Orchestrate the complete ETL pipeline: MinIO -> Parquet."""

    def __init__(self, config: Config):
        self.config = config
        self.minio = MinIOClient(
            config.minio_endpoint,
            config.minio_access_key,
            config.minio_secret_key,
            config.minio_bucket,
        )
        self.writer = ParquetWriter(self.minio)

    def run(self):
        """Execute the ETL pipeline."""
        start_time = datetime.now()
        print("=" * 70)
        print("ETL PIPELINE: MinIO -> Parquet -> Dremio")
        print("=" * 70)
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

        # Write as parquet to MinIO
        print("\n[5/5] Writing parquet to MinIO...")
        self.writer.write_all(dimensions, bridges, fact)

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print("\n" + "=" * 70)
        print("ETL COMPLETED - Data ready for Dremio!")
        print("=" * 70)
        print(f"Duration: {duration:.2f}s")
        print(f"Games processed: {len(fact):,}")
        print(f"Files written: {len(dimensions) + len(bridges) + 1}")
        print("\nNext steps:")
        print("1. Open Dremio: http://localhost:9047")
        print("2. Run dremio_setup.sql to create tables")
        print("=" * 70)


def main():
    """Entry point for ETL pipeline."""
    config = Config.from_env()
    pipeline = ETLPipeline(config)
    pipeline.run()


if __name__ == "__main__":
    main()
