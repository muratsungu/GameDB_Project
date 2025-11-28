"""Write transformed data as parquet to MinIO for Dremio."""
from typing import Dict
import pandas as pd
from storage.minio_client import MinIOClient
from pathlib import Path
from datetime import datetime


class ParquetWriter:
    """Write dimensional model as parquet files to MinIO."""

    def __init__(self, minio_client: MinIOClient):
        self.minio = minio_client

    def write_all(self, dimensions: Dict[str, pd.DataFrame], bridges: Dict[str, pd.DataFrame], fact: pd.DataFrame):
        """Write all tables as parquet to MinIO."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        local_dir = Path(f"./data/transformed_{timestamp}")
        local_dir.mkdir(parents=True, exist_ok=True)

        print("\nWriting transformed data as parquet...")

        # Write dimensions
        for name, df in dimensions.items():
            local_file = local_dir / f"{name}.parquet"
            df.to_parquet(local_file, index=False)
            self.minio.upload_file(local_file, f"transformed/{name}.parquet")
            print(f"  ✓ {name}: {len(df)} records")

        # Write bridges
        for name, df in bridges.items():
            local_file = local_dir / f"{name}.parquet"
            df.to_parquet(local_file, index=False)
            self.minio.upload_file(local_file, f"transformed/{name}.parquet")
            print(f"  ✓ {name}: {len(df)} relationships")

        # Write fact
        local_file = local_dir / "fact_games.parquet"
        fact.to_parquet(local_file, index=False)
        self.minio.upload_file(local_file, "transformed/fact_games.parquet")
        print(f"  ✓ fact_games: {len(fact)} records")

        print(f"\nAll files uploaded to MinIO: s3://games/transformed/")
        print("\nNext steps:")
        print("1. Open Dremio: http://localhost:9047")
        print("2. Add MinIO source if not already added")
        print("3. Browse to games/transformed/")
        print("4. Create Iceberg tables:")
        print('   CREATE TABLE nessie.rawg_warehouse.dim_platform')
        print('   AS SELECT * FROM minio.games.transformed."dim_platform.parquet";')
