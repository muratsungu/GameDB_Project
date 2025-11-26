"""Iceberg catalog manager."""
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.partitioning import PartitionSpec


class IcebergCatalog:
    """Manage Iceberg catalog connections and operations."""

    def __init__(self, catalog_uri: str, warehouse_path: str, minio_endpoint: str, 
                 minio_access: str, minio_secret: str, namespace: str = "rawg_warehouse"):
        self.namespace = namespace
        self.catalog = load_catalog(
            "nessie",
            type="rest",
            uri=catalog_uri,
            warehouse=warehouse_path,
            **{
                "s3.endpoint": minio_endpoint,
                "s3.access-key-id": minio_access,
                "s3.secret-access-key": minio_secret,
                "s3.path-style-access": "true",
                "s3.region": "us-east-1",
            }
        )
        self._ensure_namespace()

    def _ensure_namespace(self):
        """Create namespace if it doesn't exist."""
        try:
            self.catalog.create_namespace(self.namespace)
        except:
            pass

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        try:
            self.catalog.load_table(f"{self.namespace}.{table_name}")
            return True
        except:
            return False

    def create_table(self, table_name: str, schema: Schema, partition_spec: PartitionSpec = None):
        """Create a new table."""
        location = f"{self.catalog.properties['warehouse']}/{self.namespace}/{table_name}"
        return self.catalog.create_table(
            identifier=f"{self.namespace}.{table_name}",
            schema=schema,
            location=location,
            partition_spec=partition_spec or PartitionSpec(),
        )

    def load_table(self, table_name: str):
        """Load an existing table."""
        return self.catalog.load_table(f"{self.namespace}.{table_name}")
