import requests
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =======================
# CONFIG
# =======================
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "IR")

RADAR_BASE_URL = "https://api.cloudflare.com/client/v4/radar"

HEADERS = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Accept": "application/json",
}

# =======================
# TIME WINDOW (LAST 5 MIN)
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
    Netflows = traffic volume (normalized)
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
    
    # Debug: print response if error
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}")
    
    r.raise_for_status()

    data = r.json()
    result = data["result"]
    
    # Print structure for debugging (remove after fixing)
    # print("Netflows response structure:", result.keys())
    
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
    
    # Debug: print response if error
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}")
    
    r.raise_for_status()

    data = r.json()
    result = data["result"]
    
    # Get the series data
    if "serie_0" in result:
        series = result["serie_0"]
        if series.get("values"):
            return float(series["values"][-1])
    
    return 0.0


# =======================
# MAIN
# =======================
if __name__ == "__main__":
    start, end = last_5_min_window()

    volume = fetch_traffic_volume(start, end)
    trend = fetch_traffic_trend(start, end)

    print("========== Cloudflare Radar ==========")
    print(f"Country        : IR (Iran)")
    print(f"Time window    : {start}  →  {end}")
    print("-------------------------------------")
    print(f"Traffic volume : {volume}")
    print(f"Traffic trend  : {trend}")
    print("-------------------------------------")
    print("SQL example:")
    print(
        f"""INSERT INTO traffic (timestamp, traffic_volume, traffic_trend)
VALUES ('{end}', {volume}, {trend});"""
    )

