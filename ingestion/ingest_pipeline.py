"""Main ingestion pipeline: RAWG → MinIO."""
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from ingestion.rawg_fetcher import CDCTracker, RAWGFetcher
from storage.minio_client import MinIOClient


class IngestionPipeline:
    """Orchestrates data ingestion from RAWG to MinIO."""

    def __init__(self, api_key: str, minio_client: MinIOClient, cdc_file: Path):
        self.fetcher = RAWGFetcher(api_key)
        self.minio = minio_client
        self.cdc = CDCTracker(cdc_file)

    def run(self, start_year: int = 2024, end_year: int = 2025):
        """Run ingestion for specified year range."""
        print(f"=== RAWG Ingestion Pipeline ===")
        print(f"Years: {start_year}-{end_year}")

        all_games = []

        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                date_start = f"{year}-{month:02d}-01"
                if month == 12:
                    date_end = f"{year}-12-31"
                else:
                    date_end = f"{year}-{month+1:02d}-01"

                print(f"Fetching {year}-{month:02d}...", end=" ")
                games = self.fetcher.fetch_range(date_start, date_end, self.cdc)
                all_games.extend(games)
                print(f"{len(games)} new")

        if not all_games:
            print("No new games to ingest.")
            return

        # Save to parquet
        df = pd.DataFrame(all_games)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rawg_games_{timestamp}.parquet"
        local_path = Path(f"./data/rawg_games/{filename}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(local_path, index=False)
        print(f"Saved {len(df)} games → {local_path}")

        # Upload to MinIO
        self.minio.upload_file(local_path, f"raw/{filename}")
        print(f"Uploaded → MinIO")

        # Save CDC state
        self.cdc.save()
        print(f"CDC saved: {len(self.cdc.games)} games tracked")


def main():
    """Entry point for ingestion."""
    api_key = os.getenv("RAWG_API_KEY", "dc659b13699c4067b14ea92989c884f2")
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    minio_access = os.getenv("MINIO_ACCESS_KEY", "admin")
    minio_secret = os.getenv("MINIO_SECRET_KEY", "password")
    minio_bucket = os.getenv("MINIO_BUCKET", "games")

    minio_client = MinIOClient(minio_endpoint, minio_access, minio_secret, minio_bucket)
    cdc_file = Path("./data/rawg_games/cdc_state.json")

    pipeline = IngestionPipeline(api_key, minio_client, cdc_file)
    pipeline.run(start_year=2024, end_year=2025)


if __name__ == "__main__":
    main()
