"""Configuration management."""
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Pipeline configuration."""

    # MinIO (required)
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str

    # Iceberg (required)
    catalog_uri: str
    warehouse_path: str

    # MinIO (optional)
    raw_prefix: str = "raw/"

    # Iceberg (optional)
    namespace: str = "rawg_warehouse"

    # Processing (optional)
    state_file: Path = Path("processing_state.json")

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            minio_endpoint=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
            minio_access_key=os.getenv("MINIO_ACCESS_KEY", "admin"),
            minio_secret_key=os.getenv("MINIO_SECRET_KEY", "password"),
            minio_bucket=os.getenv("MINIO_BUCKET", "games"),
            catalog_uri=os.getenv("ICEBERG_CATALOG_URI", "http://localhost:19120/api/v1"),
            warehouse_path=os.getenv("ICEBERG_WAREHOUSE_PATH", "s3://games/warehouse"),
            namespace=os.getenv("ICEBERG_NAMESPACE", "rawg_warehouse"),
        )
