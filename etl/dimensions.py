"""Dimension table builders."""
from datetime import datetime, timedelta
from typing import Dict

import numpy as np
import pandas as pd


class DimensionBuilder:
    """Build dimension tables from raw data."""

    def __init__(self, raw_df: pd.DataFrame):
        self.raw_df = raw_df

    def build_platform(self) -> pd.DataFrame:
        """Extract unique platforms."""
        platforms = []
        for _, row in self.raw_df.iterrows():
            platform_list = row.get("platforms")
            if platform_list is not None and isinstance(platform_list, (list, np.ndarray)) and len(platform_list) > 0:
                for p in platform_list:
                    if isinstance(p, dict):
                        platform_data = p.get("platform", {})
                        if isinstance(platform_data, dict):
                            platforms.append({
                                "platform_key": platform_data.get("id"),
                                "name": platform_data.get("name"),
                                "slug": platform_data.get("slug"),
                            })

        if not platforms:
            return pd.DataFrame(columns=["platform_id", "platform_key", "name", "slug"])

        df = pd.DataFrame(platforms).drop_duplicates(subset=["platform_key"]).dropna(subset=["platform_key"])
        df.insert(0, "platform_id", range(1, len(df) + 1))
        return df.reset_index(drop=True)

    def build_store(self) -> pd.DataFrame:
        """Extract unique stores."""
        stores = []
        for _, row in self.raw_df.iterrows():
            store_list = row.get("stores")
            if store_list is not None and isinstance(store_list, (list, np.ndarray)) and len(store_list) > 0:
                for s in store_list:
                    if isinstance(s, dict):
                        store_data = s.get("store", {})
                        if isinstance(store_data, dict):
                            stores.append({
                                "store_key": store_data.get("id"),
                                "name": store_data.get("name"),
                                "slug": store_data.get("slug"),
                            })

        if not stores:
            return pd.DataFrame(columns=["store_id", "store_key", "name", "slug"])

        df = pd.DataFrame(stores).drop_duplicates(subset=["store_key"]).dropna(subset=["store_key"])
        df.insert(0, "store_id", range(1, len(df) + 1))
        return df.reset_index(drop=True)

    def build_genre(self) -> pd.DataFrame:
        """Extract unique genres."""
        genres = []
        for _, row in self.raw_df.iterrows():
            genre_list = row.get("genres")
            if genre_list is not None and isinstance(genre_list, (list, np.ndarray)) and len(genre_list) > 0:
                for g in genre_list:
                    if isinstance(g, dict):
                        genres.append({
                            "genre_key": g.get("id"),
                            "name": g.get("name"),
                            "slug": g.get("slug"),
                        })

        if not genres:
            return pd.DataFrame(columns=["genre_id", "genre_key", "name", "slug"])

        df = pd.DataFrame(genres).drop_duplicates(subset=["genre_key"]).dropna(subset=["genre_key"])
        df.insert(0, "genre_id", range(1, len(df) + 1))
        return df.reset_index(drop=True)

    def build_tag(self) -> pd.DataFrame:
        """Extract unique tags."""
        tags = []
        for _, row in self.raw_df.iterrows():
            tag_list = row.get("tags")
            if tag_list is not None and isinstance(tag_list, (list, np.ndarray)) and len(tag_list) > 0:
                for t in tag_list:
                    if isinstance(t, dict):
                        tags.append({
                            "tag_key": t.get("id"),
                            "name": t.get("name"),
                            "slug": t.get("slug"),
                            "games_count": t.get("games_count"),
                        })

        if not tags:
            return pd.DataFrame(columns=["tag_id", "tag_key", "name", "slug", "games_count"])

        df = pd.DataFrame(tags).drop_duplicates(subset=["tag_key"]).dropna(subset=["tag_key"])
        df.insert(0, "tag_id", range(1, len(df) + 1))
        return df.reset_index(drop=True)

    def build_esrb_rating(self) -> pd.DataFrame:
        """Extract unique ESRB ratings."""
        ratings = []
        for _, row in self.raw_df.iterrows():
            esrb_data = row.get("esrb_rating")
            if esrb_data and isinstance(esrb_data, dict):
                ratings.append({
                    "esrb_key": esrb_data.get("id"),
                    "name": esrb_data.get("name"),
                    "slug": esrb_data.get("slug"),
                })

        if not ratings:
            return pd.DataFrame(columns=["esrb_id", "esrb_key", "name", "slug"])

        df = pd.DataFrame(ratings).drop_duplicates(subset=["esrb_key"]).dropna(subset=["esrb_key"])
        df.insert(0, "esrb_id", range(1, len(df) + 1))
        return df.reset_index(drop=True)

    def build_date(self, start_year: int = 2015, end_year: int = 2025) -> pd.DataFrame:
        """Generate date dimension."""
        dates = []
        current = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)

        while current <= end:
            dates.append({
                "full_date": current.strftime("%Y-%m-%d"),
                "year": current.year,
                "quarter": (current.month - 1) // 3 + 1,
                "month": current.month,
                "day": current.day,
                "day_of_week": current.weekday() + 1,
                "month_name": current.strftime("%B"),
                "day_name": current.strftime("%A"),
            })
            current += timedelta(days=1)

        df = pd.DataFrame(dates)
        df.insert(0, "date_id", range(1, len(df) + 1))
        return df

    def build_all(self) -> Dict[str, pd.DataFrame]:
        """Build all dimensions."""
        return {
            "dim_platform": self.build_platform(),
            "dim_store": self.build_store(),
            "dim_genre": self.build_genre(),
            "dim_tag": self.build_tag(),
            "dim_esrb_rating": self.build_esrb_rating(),
            "dim_date": self.build_date(),
        }
