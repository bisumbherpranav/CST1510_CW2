"""
fetch_data.py - Week 8: get data from an API and save it as DATA/raw.csv.

Run it:  python fetch_data.py
"""

from pathlib import Path

import pandas as pd
import requests

# ---- Settings: the only part you change for your own data ----------------

# API to the covid-19 data
URL = "https://disease.sh/v3/covid-19/countries"
# get all countries, no filter
PARAMS = {}
# the label that holds the list of items (None because the website already gives a plain list)
RECORDS_KEY = None

RENAME = {}  # rename ugly/messy column name to shorter ones
# the exact columns to keep from the website, e.g. ["country", "continent", "cases",...]
KEEP = [
    "country",
    "continent",
    "cases",
    "deaths",
    "recovered",
    "tests",
    "population",
    "active",
]
# drop any row that is empty in these columns
MUST_HAVE = ["cases", "continent"]

# create the file path where the final csv will be saved, inside a "DATA" folder
RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


# ---- The functions ----------------------------------------------------------
def get_data(url, params):
    """Ask the API for data. Returns the JSON reply, or None if something went wrong."""
    try:
        # send the request, but give up if it takes more than 15 seconds
        response = requests.get(url, params=params, timeout=15)
        # stop and trigger an error if the website failed to load
        response.raise_for_status()  # for e.g. turns 404, 500 ... into an error
        return response.json()
    except requests.RequestException as error:
        # prints a message for an error instead of crashing
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    """Turn the JSON reply into a pandas table."""
    # find the main list of items inside the data
    records = data[records_key] if records_key else data
    # turn nested data into flat columns, e.g. {"a": {"b": 1}} becomes column a_b
    return pd.json_normalize(records, sep="_")


def tidy_data(df):
    """Rename, keep and clean the columns."""
    # change messy column names to cleaner ones using the RENAME list
    df = df.rename(columns=RENAME)
    # keep only the columns that were listed in KEEP
    df = df[KEEP]
    # delete any rows that are missing important info listed in MUST_HAVE
    df = df.dropna(subset=MUST_HAVE)
    return df


def save_data(df, path):
    """Save the table as a CSV file."""
    # create the "DATA" folder automatically if it doesn't exist yet
    path.parent.mkdir(exist_ok=True)
    # save the table to the file (index=False stops pandas from adding extra row numbers)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


# this block only runs when this file is ran direcly
if __name__ == "__main__":
    # download the data
    data = get_data(URL, PARAMS)
    # if the download worked, turn it into a table, clean it, and save it
    if data is not None:
        table = make_table(data, RECORDS_KEY)
        table = tidy_data(table)
        # show the first 5 rows in the terminal
        print(table.head())
        save_data(table, RAW_FILE)
