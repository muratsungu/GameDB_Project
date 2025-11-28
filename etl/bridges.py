"""Bridge table builders for many-to-many relationships."""
from typing import Dict

import numpy as np
import pandas as pd


class BridgeBuilder:
    """Build bridge tables linking games to dimensions."""

    def __init__(self, raw_df: pd.DataFrame, dimensions: Dict[str, pd.DataFrame]):
        self.raw_df = raw_df
        self.dimensions = dimensions

    def build_game_platform(self) -> pd.DataFrame:
        """Link games to platforms."""
        dim_platform = self.dimensions.get("dim_platform")
        if dim_platform is None or dim_platform.empty:
            return pd.DataFrame(columns=["game_id", "platform_id"])

        platform_lookup = dict(zip(dim_platform["platform_key"], dim_platform["platform_id"]))
        bridges = []

        for _, row in self.raw_df.iterrows():
            game_id = row.get("id")
            if pd.isna(game_id):
                continue

            platform_list = row.get("platforms")
            if platform_list is not None and isinstance(platform_list, (list, np.ndarray)) and len(platform_list) > 0:
                for p in platform_list:
                    if isinstance(p, dict):
                        platform_data = p.get("platform", {})
                        if isinstance(platform_data, dict):
                            platform_key = platform_data.get("id")
                            platform_id = platform_lookup.get(platform_key)
                            if platform_id:
                                bridges.append({"game_id": int(game_id), "platform_id": int(platform_id)})

        if not bridges:
            return pd.DataFrame(columns=["game_id", "platform_id"])

        return pd.DataFrame(bridges).drop_duplicates()

    def build_game_store(self) -> pd.DataFrame:
        """Link games to stores."""
        dim_store = self.dimensions.get("dim_store")
        if dim_store is None or dim_store.empty:
            return pd.DataFrame(columns=["game_id", "store_id"])

        store_lookup = dict(zip(dim_store["store_key"], dim_store["store_id"]))
        bridges = []

        for _, row in self.raw_df.iterrows():
            game_id = row.get("id")
            if pd.isna(game_id):
                continue

            store_list = row.get("stores")
            if store_list is not None and isinstance(store_list, (list, np.ndarray)) and len(store_list) > 0:
                for s in store_list:
                    if isinstance(s, dict):
                        store_data = s.get("store", {})
                        if isinstance(store_data, dict):
                            store_key = store_data.get("id")
                            store_id = store_lookup.get(store_key)
                            if store_id:
                                bridges.append({"game_id": int(game_id), "store_id": int(store_id)})

        if not bridges:
            return pd.DataFrame(columns=["game_id", "store_id"])

        return pd.DataFrame(bridges).drop_duplicates()

    def build_game_genre(self) -> pd.DataFrame:
        """Link games to genres."""
        dim_genre = self.dimensions.get("dim_genre")
        if dim_genre is None or dim_genre.empty:
            return pd.DataFrame(columns=["game_id", "genre_id"])

        genre_lookup = dict(zip(dim_genre["genre_key"], dim_genre["genre_id"]))
        bridges = []

        for _, row in self.raw_df.iterrows():
            game_id = row.get("id")
            if pd.isna(game_id):
                continue

            genre_list = row.get("genres")
            if genre_list is not None and isinstance(genre_list, (list, np.ndarray)) and len(genre_list) > 0:
                for g in genre_list:
                    if isinstance(g, dict):
                        genre_key = g.get("id")
                        genre_id = genre_lookup.get(genre_key)
                        if genre_id:
                            bridges.append({"game_id": int(game_id), "genre_id": int(genre_id)})

        if not bridges:
            return pd.DataFrame(columns=["game_id", "genre_id"])

        return pd.DataFrame(bridges).drop_duplicates()

    def build_game_tag(self) -> pd.DataFrame:
        """Link games to tags."""
        dim_tag = self.dimensions.get("dim_tag")
        if dim_tag is None or dim_tag.empty:
            return pd.DataFrame(columns=["game_id", "tag_id"])

        tag_lookup = dict(zip(dim_tag["tag_key"], dim_tag["tag_id"]))
        bridges = []

        for _, row in self.raw_df.iterrows():
            game_id = row.get("id")
            if pd.isna(game_id):
                continue

            tag_list = row.get("tags")
            if tag_list is not None and isinstance(tag_list, (list, np.ndarray)) and len(tag_list) > 0:
                for t in tag_list:
                    if isinstance(t, dict):
                        tag_key = t.get("id")
                        tag_id = tag_lookup.get(tag_key)
                        if tag_id:
                            bridges.append({"game_id": int(game_id), "tag_id": int(tag_id)})

        if not bridges:
            return pd.DataFrame(columns=["game_id", "tag_id"])

        return pd.DataFrame(bridges).drop_duplicates()

    def build_all(self) -> Dict[str, pd.DataFrame]:
        """Build all bridge tables."""
        return {
            "bridge_game_platform": self.build_game_platform(),
            "bridge_game_store": self.build_game_store(),
            "bridge_game_genre": self.build_game_genre(),
            "bridge_game_tag": self.build_game_tag(),
        }
