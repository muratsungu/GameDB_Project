"""RAWG API data fetcher with CDC tracking."""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests


class CDCTracker:
    """Track ingested games to prevent duplicates."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.games: Dict[int, str] = {}
        self.load()

    def load(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                self.games = {int(k): v for k, v in data.get("games", {}).items()}

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(
                {"games": self.games, "last_run": datetime.now().isoformat()},
                f,
                indent=2,
            )

    def is_new_or_updated(self, game: dict) -> bool:
        gid = game["id"]
        updated = game.get("updated") or game.get("released") or ""
        return (gid not in self.games) or (updated > self.games.get(gid, ""))

    def mark(self, game: dict):
        gid = game["id"]
        updated = game.get("updated") or game.get("released") or datetime.now().isoformat()
        self.games[gid] = updated


class RAWGFetcher:
    """Fetch game data from RAWG API."""

    def __init__(self, api_key: str, page_size: int = 40):
        self.api_key = api_key
        self.base_url = "https://api.rawg.io/api/games"
        self.page_size = page_size

    def fetch_page(self, page: int, date_start: str, date_end: str) -> dict:
        """Fetch a single page from RAWG API."""
        params = {
            "key": self.api_key,
            "dates": f"{date_start},{date_end}",
            "page": page,
            "page_size": self.page_size,
            "ordering": "-released",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            if response.status_code == 404:
                return {}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}

    def fetch_range(self, date_start: str, date_end: str, cdc: CDCTracker) -> List[dict]:
        """Fetch all games in a date range with CDC filtering."""
        new_games = []
        page = 1

        while True:
            data = self.fetch_page(page, date_start, date_end)
            results = data.get("results", [])
            if not results:
                break

            for game in results:
                if cdc.is_new_or_updated(game):
                    new_games.append(game)
                    cdc.mark(game)

            if not data.get("next"):
                break

            page += 1
            time.sleep(0.3)

        return new_games
