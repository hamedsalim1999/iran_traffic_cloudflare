import requests
import sqlite3
import schedule
import time
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =======================
# CONFIG
# =======================
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
DB_PATH = os.getenv("DB_PATH", "iran_traffic.db")
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "IR")

RADAR_BASE_URL = "https://api.cloudflare.com/client/v4/radar"

HEADERS = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Accept": "application/json",
}

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =======================
# DATABASE
# =======================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            traffic_volume REAL NOT NULL,
            traffic_trend REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# =======================
# TIME HELPERS
# =======================
def last_5_min_window():
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    # Use a slight lag and 15-minute window to satisfy Radar agg interval
    end = now - timedelta(minutes=15)
    start = end - timedelta(minutes=15)
    # Format as YYYY-mm-ddTHH:MM:ssZ (required by Cloudflare Radar API)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")


# =======================
# API CALLS
# =======================
def fetch_traffic_volume(start, end):
    """
    Netflows = traffic volume (bytes index, normalized)
    """
    url = (
        f"{RADAR_BASE_URL}/netflows/timeseries"
        f"?location={COUNTRY_CODE}"
        f"&aggInterval=15m"
        f"&dateStart={start}"
        f"&dateEnd={end}"
        f"&format=json"
    )

    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    result = r.json()["result"]

    # Get the series data
    if "serie_0" in result:
        series = result["serie_0"]
        if series.get("values"):
            return float(series["values"][-1])
    
    return 0.0


def fetch_traffic_trend(start, end):
    """
    HTTP request trend (normalized)
    """
    url = (
        f"{RADAR_BASE_URL}/http/timeseries"
        f"?location={COUNTRY_CODE}"
        f"&aggInterval=15m"
        f"&dateStart={start}"
        f"&dateEnd={end}"
        f"&format=json"
    )

    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    result = r.json()["result"]

    # Get the series data
    if "serie_0" in result:
        series = result["serie_0"]
        if series.get("values"):
            return float(series["values"][-1])
    
    return 0.0


# =======================
# STORE & CLEANUP
# =======================
def store_data(timestamp, volume, trend):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO traffic (timestamp, traffic_volume, traffic_trend)
        VALUES (?, ?, ?)
    """, (timestamp, volume, trend))

    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=100)).isoformat()
    cur.execute("""
        DELETE FROM traffic WHERE timestamp < ?
    """, (cutoff,))

    conn.commit()
    conn.close()


# =======================
# TELEGRAM
# =======================
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Telegram send error {resp.status_code}: {resp.text}")
    except Exception as ex:
        print(f"Telegram send exception: {ex}")


# =======================
# JOB
# =======================
def job():
    try:
        start, end = last_5_min_window()

        volume = fetch_traffic_volume(start, end)
        trend = fetch_traffic_trend(start, end)

        store_data(end, volume, trend)

        message = f"[{end}] IR traffic | volume={volume:.4f} trend={trend:.4f}"
        print(message)
        if trend > 0:
            send_telegram_message(message)

    except Exception as e:
        print("ERROR:", e)


# =======================
# MAIN
# =======================
if __name__ == "__main__":
    init_db()

    schedule.every(1).minutes.do(job)

    print("🚀 Cloudflare Iran traffic monitor started (every 15 minutes)")
    while True:
        schedule.run_pending()

