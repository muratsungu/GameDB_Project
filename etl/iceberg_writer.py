"""Iceberg table writer."""
from typing import Dict

import pandas as pd
import pyarrow as pa
from pyiceberg.schema import Schema

from etl.iceberg_catalog import IcebergCatalog
from etl import iceberg_schemas


class IcebergWriter:
    """Write DataFrames to Iceberg tables."""

    def __init__(self, catalog: IcebergCatalog):
        self.catalog = catalog

    def _to_arrow(self, df: pd.DataFrame, schema: Schema) -> pa.Table:
        """Convert DataFrame to PyArrow table."""
        return pa.Table.from_pandas(df, schema=schema.as_arrow())

    def write_dimension(self, name: str, df: pd.DataFrame, schema: Schema, mode: str = "overwrite"):
        """Write dimension table."""
        if not self.catalog.table_exists(name):
            table = self.catalog.create_table(name, schema)
            table.append(self._to_arrow(df, schema))
        else:
            table = self.catalog.load_table(name)
            if mode == "overwrite":
                table.overwrite(self._to_arrow(df, schema))
            else:
                table.append(self._to_arrow(df, schema))

    def write_bridge(self, name: str, df: pd.DataFrame, mode: str = "overwrite"):
        """Write bridge table."""
        schema = iceberg_schemas.bridge_schema()
        if not self.catalog.table_exists(name):
            table = self.catalog.create_table(name, schema)
            table.append(self._to_arrow(df, schema))
        else:
            table = self.catalog.load_table(name)
            if mode == "overwrite":
                table.overwrite(self._to_arrow(df, schema))
            else:
                table.append(self._to_arrow(df, schema))

    def write_fact(self, df: pd.DataFrame, mode: str = "overwrite"):
        """Write fact table."""
        schema = iceberg_schemas.fact_games_schema()
        name = "fact_games"

        if not self.catalog.table_exists(name):
            table = self.catalog.create_table(name, schema)
            table.append(self._to_arrow(df, schema))
        else:
            table = self.catalog.load_table(name)
            if mode == "overwrite":
                table.overwrite(self._to_arrow(df, schema))
            else:
                table.append(self._to_arrow(df, schema))

    def write_all(self, dimensions: Dict[str, pd.DataFrame], bridges: Dict[str, pd.DataFrame],
                  fact: pd.DataFrame, mode: str = "overwrite"):
        """Write all tables."""
        # Dimensions
        self.write_dimension("dim_platform", dimensions["dim_platform"], iceberg_schemas.dim_platform_schema(), mode)
        self.write_dimension("dim_store", dimensions["dim_store"], iceberg_schemas.dim_store_schema(), mode)
        self.write_dimension("dim_genre", dimensions["dim_genre"], iceberg_schemas.dim_genre_schema(), mode)
        self.write_dimension("dim_tag", dimensions["dim_tag"], iceberg_schemas.dim_tag_schema(), mode)
        self.write_dimension("dim_esrb_rating", dimensions["dim_esrb_rating"], iceberg_schemas.dim_esrb_rating_schema(), mode)
        self.write_dimension("dim_date", dimensions["dim_date"], iceberg_schemas.dim_date_schema(), mode)

        # Bridges
        for bridge_name, bridge_df in bridges.items():
            self.write_bridge(bridge_name, bridge_df, mode)

        # Fact
        self.write_fact(fact, mode)
