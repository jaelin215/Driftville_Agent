###########################################################
# Author: Jaelin Lee
# Date: Feb 7, 2026
# Description: Creates cleaned session logs and saves to app/logs/cleaned folder
# input: FOLDER_PATH
# output: `app/logs/cleaned` folder as .csv
###########################################################

import os
from pathlib import Path
from pprint import pprint

import pandas as pd
from warnings import filterwarnings

filterwarnings("ignore")


def load_session_log(f_path):
    df = pd.read_json(f_path, lines=True)
    df = df.convert_dtypes()

    df["sim_time"] = df["sim_time"].astype(str).str.extract(r"(\d{2}:\d{2})")
    df["llm_temperature"] = df["llm_temperature"].astype(float).round(1).astype(str)
    df.rename(columns={"llm_temperature": "temp"}, inplace=True)
    df.drop(columns=["ts_created"], inplace=True)

    keys = df["orpda"][0].keys()
    df_final = pd.concat(
        [df.drop("orpda", axis=1), df["orpda"].apply(pd.Series)], axis=1
    )
    return df_final


def get_df_name(df):
    for name, obj in globals().items():
        if obj is df:
            return name
    return None


###########################################################
ROOT = Path.cwd()
LOGS_PATH = Path(ROOT, "app/logs/")
FOLDER_PATH = Path(LOGS_PATH, "v3_complete_waking_hours")
###########################################################

# Process all log files
log_files = sorted(
    [f for f in FOLDER_PATH.glob("*.log") if "memory_streams" not in f.name],
    key=lambda x: x.stat().st_birthtime,
    reverse=True,
)

print(f"Found {len(log_files)} logs")

# Process each file
for session_path in log_files:
    print(f"\nProcessing: {session_path.name}")

    # Detect mode from filename
    if "orpda" in session_path.name:
        mode = "orpda"
    elif "orpa" in session_path.name:
        mode = "orpa"
    else:
        mode = None

    print(f"  Mode: {mode}")

    try:
        df_session = load_session_log(session_path).dropna(subset=["llm_model"])
        print(f"  ✓ Loaded {len(df_session)} rows")

        # ... rest of processing code

    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n✓ Processed all {len(log_files)} files")
