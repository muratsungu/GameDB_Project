"""Fact table builder."""
from typing import Dict, Optional

import pandas as pd


class FactBuilder:
    """Build fact_games table with metrics and foreign keys."""

    def __init__(self, raw_df: pd.DataFrame, dimensions: Dict[str, pd.DataFrame]):
        self.raw_df = raw_df
        self.date_lookup = self._create_date_lookup(dimensions.get("dim_date"))
        self.esrb_lookup = self._create_esrb_lookup(dimensions.get("dim_esrb_rating"))

    def _create_date_lookup(self, dim_date: pd.DataFrame) -> Dict[str, int]:
        if dim_date is None or dim_date.empty:
            return {}
        return dict(zip(dim_date["full_date"], dim_date["date_id"]))

    def _create_esrb_lookup(self, dim_esrb: pd.DataFrame) -> Dict[int, int]:
        if dim_esrb is None or dim_esrb.empty:
            return {}
        return dict(zip(dim_esrb["esrb_key"], dim_esrb["esrb_id"]))

    def _safe_int(self, value) -> Optional[int]:
        if pd.isna(value):
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_float(self, value) -> Optional[float]:
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def build(self) -> pd.DataFrame:
        """Build fact_games table."""
        records = []

        for _, row in self.raw_df.iterrows():
            game_id = row.get("id")
            if pd.isna(game_id):
                continue

            # Lookup foreign keys
            released = str(row.get("released", "")).split(" ")[0]
            date_id = self.date_lookup.get(released)

            esrb_data = row.get("esrb_rating")
            esrb_id = None
            if esrb_data and isinstance(esrb_data, dict):
                esrb_id = self.esrb_lookup.get(esrb_data.get("id"))

            records.append({
                "game_id": int(game_id),
                "date_id": int(date_id) if date_id else None,
                "esrb_id": int(esrb_id) if esrb_id else None,
                "slug": row.get("slug"),
                "name": row.get("name"),
                "released": row.get("released"),
                "updated": row.get("updated"),
                "background_image": row.get("background_image"),
                "tba": row.get("tba"),
                "saturated_color": row.get("saturated_color"),
                "dominant_color": row.get("dominant_color"),
                "playtime": self._safe_int(row.get("playtime")),
                "ratings_count": self._safe_int(row.get("ratings_count")),
                "reviews_count": self._safe_int(row.get("reviews_count")),
                "reviews_text_count": self._safe_int(row.get("reviews_text_count")),
                "added": self._safe_int(row.get("added")),
                "suggestions_count": self._safe_int(row.get("suggestions_count")),
                "rating": self._safe_float(row.get("rating")),
                "rating_top": self._safe_int(row.get("rating_top")),
                "metacritic": self._safe_int(row.get("metacritic")),
                "community_rating": self._safe_float(row.get("community_rating")),
            })

        return pd.DataFrame(records)
