# %% [markdown]
# ## 0. Import
from pathlib import Path
from pprint import pprint
from random import random
from warnings import filterwarnings

import pandas as pd

filterwarnings("ignore")

ROOT = Path.cwd()
print(ROOT)
LOGS_PATH = Path(ROOT, "app/logs/")

# %%
#########################################
# >> UPDATE INPUT
# Option 1 - old runs
n = 1
FOLDER_PATH = Path(LOGS_PATH, "v3_complete_waking_hours")
path = Path(FOLDER_PATH)
print(f"Path: {path}")
print(f"Exists: {path.exists()}")
mode = "orpda"  # "orpda", "orpa", None

# Option 2 - current runs
# path = Path(LOGS_PATH, "")  # folder name of log files
# mode = None
#########################################

# Extract log file names
all_files = sorted(
    [f.name for f in path.glob("*.log") if "memory" not in f.name],
    key=lambda x: Path(path / x).stat().st_birthtime,
    reverse=True,
)

if mode == "orpa":
    sessions = [f for f in all_files if "orpa" in f]
elif mode == "orpda":
    sessions = [f for f in all_files if "orpda" in f]
else:
    sessions = all_files
    if sessions:
        mode = (
            "orpda"
            if "orpda" in sessions[0]
            else "orpa" if "orpa" in sessions[0] else None
        )

# Select the latest file
if len(sessions) > 0:
    session_path = (
        Path(path, sessions[n]) if n < len(sessions) else Path(path, sessions[0])
    )
else:
    print(f"ERROR: No .log sessions found in {path}")
    session_path = None

print(f"Selected: {session_path}")


if mode:
    print("\n", "=" * 10, mode.upper(), "=" * 10)
print(len(sessions), "logs")
pprint(sessions)
print("\n", "=" * 10, "Selected File", "=" * 10)
print(session_path)


# %%
def load_session_log(f_path):
    df = pd.read_json(f_path, lines=True)
    df = df.convert_dtypes()

    # Extract the action summary of the Action layer
    df["sim_time"] = df["sim_time"].astype(str).str.extract(r"(\d{2}:\d{2})")
    df["llm_temperature"] = df["llm_temperature"].astype(float).round(1).astype(str)
    df.rename(columns={"llm_temperature": "temp"}, inplace=True)
    df.drop(columns=["ts_created"], inplace=True)
    print(df.head(3))

    # print keys from jsonl
    keys = df["orpda"][0].keys()
    print(keys)
    df_final = pd.concat(
        [df.drop("orpda", axis=1), df["orpda"].apply(pd.Series)], axis=1
    )
    return df_final


df_session = load_session_log(session_path).dropna(subset=["llm_model"])
df_session.tail()
df_session.shape


# %%
def get_df_name(df):
    for name, obj in globals().items():
        if obj is df:
            return name
    return None


# %% [markdown]
# ## 3. Convert JSONL content to Series

# %%
# df_session["location_plan"] = df_session["plan"].apply(lambda x: x["location"])
# df_session["location_action"] = df_session["action_result"].apply(lambda x: x["location"])

# Extract ORPDA layer to each dataframe
df_observe = df_session["observation"].apply(pd.Series)
df_observe.head(2)

df_plan = df_session["plan"].apply(pd.Series)
df_plan.head(2)

if mode == "orpda":
    df_drift = df_session["drift_decision"].apply(pd.Series)
    df_drift.head(2)

df_act = df_session["action_result"].apply(pd.Series)
df_act.head(2)

df_reflect = df_session["reflection"].apply(pd.Series)
df_reflect.head(2)


# %%
# check for alignment
cols_to_check = ["datetime_start", "location", "action"]
print("Mismatch count")

# Selct comparison
key1 = df_observe
key2 = df_plan
print("=" * 20)
print(f"{get_df_name(key1)} vs {get_df_name(key2)} (#rows: {len(df_observe)})")
print("=" * 20)
# Count mismatch
for col in cols_to_check:
    print(f"{col}: ", (key1[col] != key2[col]).sum())

# Selct comparison
key1 = df_observe
key2 = df_act
print("=" * 20)
print(f"{get_df_name(key1)} vs {get_df_name(key2)} (#rows: {len(df_observe)})")
print("=" * 20)
# Count mismatch
for col in cols_to_check:
    print(f"{col}: ", (key1[col] != key2[col]).sum())

# Selct comparison
key1 = df_plan
key2 = df_act
print("=" * 20)
print(f"{get_df_name(key1)} vs {get_df_name(key2)} (#rows: {len(df_observe)})")
print("=" * 20)
# Count mismatch
for col in cols_to_check:
    print(f"{col}: ", (key1[col] != key2[col]).sum())


# %% [markdown]
# ## 4. Filter ORPDA columns

# %%

# O
o_df = df_observe[
    ["datetime_start", "location", "action", "state_summary", "environment_description"]
]
o_df.columns = o_df.columns + "_o"
# o_df.rename(columns={"datetime_start_o": "datetime_start"}, inplace=True)

# P
p_df = df_plan[["datetime_start", "location", "action", "topic", "state_summary"]]
p_df.columns = p_df.columns + "_p"
# p_df.rename(columns={"datetime_start_p": "datetime_start"}, inplace=True)

# D
if mode == "orpda":
    d_df = df_drift.drop(columns=["duration_min", "drift_intensity"])
    d_df = d_df[
        [
            "datetime_start",
            "should_drift",
            "drift_type",
            "drift_topic",
            "drift_action",
            "potential_recovery",
            "justification",
        ]
    ]
    d_df.columns = d_df.columns + "_d"
    # d_df.rename(columns={"datetime_start_d": "datetime_start"}, inplace=True)

# A
a_df = df_act[
    [
        "datetime_start",
        "location",
        "action",
        "topic",
        "drift_type",
        "drift_topic",
        "state_summary",
    ]
]
a_df.columns = a_df.columns + "_a"
# a_df.rename(columns={"datetime_start_a": "datetime_start"}, inplace=True)


# R
df_reflect["datetime_start"] = a_df["datetime_start_a"].copy()
r_df = df_reflect[
    [
        "datetime_start",
        "rumination_theme",
        "emerging_thought_pattern",
        "executive_insight",
        "state_summary",
        "reasoning",
        "meta_rule",
    ]
]

r_df.columns = r_df.columns + "_r"
# r_df.rename(columns={"datetime_start_r": "datetime_start"}, inplace=True)


# print DF
print("Observe:")
# print(o_df.columns)
print(o_df.tail())
print("Reflect:")
print(r_df.tail())
print("Plan:")
print(p_df.tail())
if mode == "orpda":
    print("Drift:")
    print(d_df.tail())
    print("Act:")
print(a_df.tail())


# %% [markdown]
# ## 5. Merge ORPDA with selected columns

# %%
# # Merge
# tmp = pd.merge(o_df, r_df, on="datetime_start", how="outer")
# tmp = pd.merge(tmp, p_df, on="datetime_start", how="outer")
# if mode == "orpda":
#     tmp = pd.merge(tmp, d_df, on="datetime_start", how="outer")
# tmp = pd.merge(tmp, a_df, on="datetime_start", how="outer")
# tmp2 = pd.concat([df_session[['llm_model','temp','agent']], tmp], axis=1)

# Merge
tmp = o_df.join(r_df, how="outer", lsuffix="_o", rsuffix="_r")
tmp = tmp.join(p_df, how="outer", lsuffix="", rsuffix="_p")
if mode == "orpda":
    tmp = tmp.join(d_df, how="outer", lsuffix="", rsuffix="_d")
tmp = tmp.join(a_df, how="outer", lsuffix="", rsuffix="_a")

tmp2 = pd.concat([df_session[["llm_model", "temp", "agent"]], tmp], axis=1)

# %%
# # Check for missing or mismatching datetime_start value
# if mode == "orpda":
#     result = (tmp2["datetime_start_o"] == tmp2["datetime_start_r"]).all() and \
#             (tmp2["datetime_start_r"] == tmp2["datetime_start_p"]).all() and \
#             (tmp2["datetime_start_p"] == tmp2["datetime_start_d"]).all() and \
#             (tmp2["datetime_start_d"] == tmp2["datetime_start_a"]).all()
# elif mode == "orpa":
#     result = (tmp2["datetime_start_o"] == tmp2["datetime_start_r"]).all() and \
#             (tmp2["datetime_start_r"] == tmp2["datetime_start_p"]).all() and \
#             (tmp2["datetime_start_p"] == tmp2["datetime_start_a"]).all()

# if result:
#     print("All datetime_start columns are the same")
# else:
#     print("Some datetime_start columns differ")


if mode == "orpda":
    cols = [
        "datetime_start_o",
        "datetime_start_r",
        "datetime_start_p",
        "datetime_start_d",
        "datetime_start_a",
    ]
elif mode == "orpa":
    cols = [
        "datetime_start_o",
        "datetime_start_r",
        "datetime_start_p",
        "datetime_start_a",
    ]


all_same = all((tmp2[cols[0]] == tmp2[col]).all() for col in cols[1:])

if all_same:
    print("All datetime_start columns are identical")
else:
    print("Differences found:")
    for col in cols[1:]:
        mismatches = tmp2[tmp2[cols[0]] != tmp2[col]]
        if len(mismatches) > 0:
            print(f"\n  {cols[0]} vs {col}: {len(mismatches)} mismatches")
            print(mismatches[[cols[0], col]])


# %%
# Reset datetime column
# Find the datetime column with least NaN values
datetime_cols = [col for col in tmp2.columns if col.startswith("datetime_start")]
datetime_col_counts = {col: tmp2[col].notna().sum() for col in datetime_cols}
best_col = max(datetime_col_counts, key=datetime_col_counts.get)

# Get first valid datetime from the best column
first_datetime = tmp2[best_col].dropna().iloc[0]

# Convert to datetime if string
try:
    first_datetime = pd.to_datetime(first_datetime, format="%Y-%m-%d %H:%M")
except (ValueError, TypeError):
    first_datetime = pd.to_datetime(first_datetime)

# Handle NaT
if pd.isna(first_datetime):
    first_datetime = pd.Timestamp("2024-01-01 00:00:00")
    print(f"No valid datetime found, using default time: {first_datetime}")

# Generate datetime range
datetime_range = pd.date_range(start=first_datetime, periods=len(tmp2), freq="15min")

# Update all datetime columns
for col in datetime_cols:
    tmp2[col] = datetime_range

print(f"Updated {len(datetime_cols)} datetime columns starting from {first_datetime}")


# %% [markdown]
# ## 6. Export to CSV

# %%
# Export CSV
filename = session_path.name.replace(".log", ".csv")
output_path = Path(ROOT, "app/logs/cleaned", f"cleaned_{filename}")
output_path.parent.mkdir(parents=True, exist_ok=True)
tmp2.to_csv(str(output_path), index=False)
print(f"CSV saved to {output_path}!")
tmp2.tail(2).T

# %% [markdown]
# ## 7. Filter Columns

# %% [markdown]
# Note:
#
# - observation layer has t-1 value as it's retrieving what happened in the past up to t-1 timestamp.

# %%
# tmp.filter(regex="(location|action)(?!.*_r)).head(3)
locations = tmp2.filter(regex="(time|location)")
actions = tmp2.filter(regex="(time|action)")
if mode == "orpda":
    drifts = tmp2.filter(regex="(time|_d)")


random.seed(42)
seed = random.randint(0, 10000)

indices = o_df.sample(3, random_state=seed).index

print(o_df.loc[indices])
print(r_df.loc[indices])
print(p_df.loc[indices])
if mode == "orpda":
    print(d_df.loc[indices])
print(a_df.loc[indices])


# %%
if mode == "orpda":
    cols = [
        "llm_model",
        "temp",
        "agent",
        "datetime_start_a",
        "meta_rule_r",
        "should_drift_d",
        "drift_topic_a",
        "state_summary_r",
        "state_summary_p",
        "drift_action_d",
        "state_summary_a",
        "action_p",
        "action_a",
        "location_p",
        "location_a",
    ]
    filtered = tmp2.filter(
        regex="(llm_model|temp|agent|time|_a|should|drift_type|topic|drft_action|meta|action_p|location_p|summary)"
    ).sort_values(by="datetime_start_a")[cols]
    print(filtered.tail())
elif mode == "orpa":
    cols = [
        "llm_model",
        "temp",
        "agent",
        "datetime_start_a",
        "meta_rule_r",
        "state_summary_r",
        "state_summary_p",
        "state_summary_a",
        "action_p",
        "action_a",
        "location_p",
        "location_a",
    ]
    filtered = tmp2.filter(
        regex="(llm_model|temp|agent|time|_a|topic|meta|action_p|location_p|summary)"
    ).sort_values(by="datetime_start_a")[cols]
    print(filtered.tail())

print(
    mode.upper(), "--", filtered.loc[0, "llm_model"], "(", filtered.loc[0, "temp"], ")"
)
print(session_path)

# %% [markdown]
# **Observations:**
#
# ORPA:
# - Drift layer `should_drift` value determines Act layer `drift_type`, `drift_topic`, `staet_summary_a` values.
# - gemma3:27b-cloud (temp 1.0) -- is `state_summary_r` at t reflecting `state_summary_a` at t-1 correctly?
#
# ORPDA:
# - gpt-oss:20b-cloud (temp 0.0) -- Plan and Action matches

# %%


# %%


# %%
