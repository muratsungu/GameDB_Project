# rawg_fetcher.py
import requests
import json
import datetime
import time
import os
import logging

# ----------------------------
# CONFIG
# ----------------------------
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
RAWG_URL = "https://api.rawg.io/api/games"
STATE_PATH = "state/state.json"
RAW_DIR = "data/raw"

MAX_RETRIES = 5
PAGE_SIZE = 40  # RAWG default: 20, max: 40

# ----------------------------
# LOGGING
# ----------------------------
logger = logging.getLogger("rawg_fetcher")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '{"time": "%(asctime)s", "level": "%(levelname)s", "msg": "%(message)s"}'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ----------------------------
# STATE MANAGEMENT
# ----------------------------
def read_state():
    if not os.path.exists(STATE_PATH):
        return "1970-01-01T00:00:00Z"
    with open(STATE_PATH) as f:
        return json.load(f)["last_run_iso"]

def write_state(ts_iso):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump({"last_run_iso": ts_iso}, f)

# ----------------------------
# HTTP REQUEST WITH RETRY
# ----------------------------
def request_with_backoff(url, params):
    backoff = 1
    for attempt in range(MAX_RETRIES):
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            logger.warning(f"Rate limit hit. Sleeping {backoff}s before retry")
            time.sleep(backoff)
            backoff *= 2
            continue
        else:
            resp.raise_for_status()
    raise Exception(f"Max retries reached for URL: {url}")

# ----------------------------
# SAVE RAW DATA
# ----------------------------
def save_raw(data):
    os.makedirs(RAW_DIR, exist_ok=True)
    fname = f"{RAW_DIR}/rawg_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump(data, f)
    logger.info(f"Saved raw data to {fname}")

# ----------------------------
# INCREMENTAL FETCH
# ----------------------------
def fetch_incremental():
    last_run = read_state()
    logger.info(f"Starting incremental fetch since {last_run}")

    page = 1
    while True:
        params = {
            "key": RAWG_API_KEY,
            "dates": f"{last_run},{datetime.datetime.utcnow().isoformat()}",
            "page": page,
            "page_size": PAGE_SIZE,
        }

        data = request_with_backoff(RAWG_URL, params)
        if not data.get("results"):
            logger.info("No results found, ending fetch")
            break

        save_raw(data)

        if not data.get("next"):
            break

        page += 1
        time.sleep(0.5)

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    write_state(now_iso)
    logger.info(f"Incremental fetch finished. State updated to {now_iso}")

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    fetch_incremental()
