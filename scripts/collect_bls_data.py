import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# Load BLS API Key
load_dotenv()
API_KEY = os.getenv("BLS_API_KEY")

# Collecting the right series
SERIES = {
    "CES0000000001": "total_nonfarm_employment",
    "LNS14000000": "unemployment_rate",
    "LNS11000000": "labor_force",
    "LNS12000000": "employment",
    "LNS13000000": "unemployment",
    "CES0500000002": "avg_weekly_hours",
    "CES0500000003": "avg_hourly_earnings", 
}

# Output file path
DATA_PATH = Path("data/bls_data.csv")
DATA_PATH.parent.mkdir(parents = True, exist_ok = True)

# Actually fetching the data from BLS
def fetch_bls_series(series_ids, start_year, end_year):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {"Content-type": "application/json"}

    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }

    # Incldue API key if user provides one
    if API_KEY:
        payload["registrationkey"] = API_KEY

    print(f"Requesting BLS Data for {start_year} - {end_year}.")
    response = requests.post(url, json = payload, headers = headers).json()

    if response.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API request failed:\n{response}")

    rows = []

    for series in response["Results"]["series"]:
        sid = series["seriesID"]
        output_name = SERIES[sid]

        for item in series["data"]:
            if not item["period"].startswith("M"):
                continue
        
            year = int(item["year"])
            month = int(item["period"][1:])
            value = float(item["value"])

            rows.append({
                "series_id": sid,
                "series_name": output_name,
                "date": datetime(year, month, 1),
                "value": value
            })
    
    return pd.DataFrame(rows)

# Loading existing data (if there is some)
def load_existing():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, parse_dates = ["date"])
    return pd.DataFrame()

# Updating the dataset with the new data
def update_dataset():
    existing = load_existing()

    # Determining start year, fetches only new row if dataset exists
    if existing.empty:
        start_year = datetime.now().year - 2
    else:
        last_date = existing["date"].max()
        start_year = last_date.year
    
    end_year = datetime.now().year

    # Pulling the new data
    new_data = fetch_bls_series(list(SERIES.keys()), start_year, end_year)

    combined = pd.concat([existing, new_data], ignore_index = True)
    combined = combined.drop_duplicates(subset = ["series_id", "date"])

    # Pivoting from long to wide
    wide = combined.pivot_table(
        index = "date",
        columns = "series_name",
        values = "value"
    ).reset_index()

    # Sorting chronologically for easy reading and because it makes sense
    wide = wide.sort_values("date")
    
    # Saving to CSV
    wide.to_csv(DATA_PATH, index = False)

    print("Datset updated successfully!")
    print(f"Saved to: {DATA_PATH}")
    print(f"Total rows: {len(wide)}")

# Run it when executed directly
if __name__ == "__main__":
    update_dataset()

