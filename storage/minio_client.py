"""MinIO client for S3 operations."""
from io import BytesIO
from pathlib import Path
from typing import List

import boto3
import pandas as pd
from botocore.client import Config


class MinIOClient:
    """Simplified MinIO client for file operations."""

    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except:
            self.client.create_bucket(Bucket=self.bucket)

    def upload_file(self, local_path: Path, object_key: str):
        """Upload a file to MinIO."""
        self.client.upload_file(str(local_path), self.bucket, object_key)

    def list_files(self, prefix: str = "raw/") -> List[str]:
        """List files with given prefix."""
        files = []
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            if "Contents" in page:
                files.extend([obj["Key"] for obj in page["Contents"] if obj["Key"].endswith(".parquet")])
        return files

    def read_parquet(self, object_key: str) -> pd.DataFrame:
        """Read a parquet file from MinIO."""
        response = self.client.get_object(Bucket=self.bucket, Key=object_key)
        return pd.read_parquet(BytesIO(response["Body"].read()))

    def read_all_parquet(self, prefix: str = "raw/") -> pd.DataFrame:
        """Read and combine all parquet files with given prefix."""
        files = self.list_files(prefix)
        if not files:
            return pd.DataFrame()

        dfs = [self.read_parquet(f) for f in files]
        combined = pd.concat(dfs, ignore_index=True)

        # Deduplicate by game ID
        if "id" in combined.columns:
            if "updated" in combined.columns:
                combined = combined.sort_values("updated", ascending=False)
            combined = combined.drop_duplicates(subset=["id"], keep="first")

        return combined.reset_index(drop=True)
