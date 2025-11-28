"""Configuration management."""
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Pipeline configuration."""

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    raw_prefix: str = "raw/"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            minio_endpoint=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
            minio_access_key=os.getenv("MINIO_ACCESS_KEY", "admin"),
            minio_secret_key=os.getenv("MINIO_SECRET_KEY", "password"),
            minio_bucket=os.getenv("MINIO_BUCKET", "games"),
        )
