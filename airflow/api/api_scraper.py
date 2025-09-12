import requests
import pandas as pd
import numpy as np
import logging

def scrape_data():
    seasons = np.arange(2012, 2026)
    records = []

    for season in seasons:

        url = f"https://api.jolpi.ca/ergast/f1/{season}/races/"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            
            # Parse qualifying date
            for race in data["MRData"]["RaceTable"]["Races"]:

                quali = race.get("Qualifying", {})
                quali_date = quali.get("date")

                records.append({
                    "season": int(race["season"]),
                    "round": int(race["round"]),
                    "quali_date": quali_date,
                })

        else:
            logging.debug("Failed to retrieve data:", response.status_code)

    df_qualifying = pd.DataFrame(records)

    # Add quali_date_id, an integer representation of quali_date
    df_qualifying['quali_date'] = pd.to_datetime(df_qualifying['quali_date']) # has to be type datetime
    df_qualifying['quali_date_id'] = df_qualifying['quali_date'].dt.strftime('%Y%m%d').astype(int)

    # Save to staging
    df_qualifying.to_parquet("/opt/airflow/data/staging/qualifying.parquet")