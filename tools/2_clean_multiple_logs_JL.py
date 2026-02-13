###########################################################
# Author: Jaelin Lee
# Date: Feb 7, 2026
# Description: Creates cleaned session logs and saves to app/logs/cleaned folder
# input: FOLDER_PATH
# output: `app/logs/cleaned` folder as .csv
###########################################################

from pathlib import Path
from warnings import filterwarnings

import pandas as pd

filterwarnings("ignore")
audit_log = []
processed_files = []  # Add this line
failed_files = []  # Add this line


def load_session_log(f_path):
    df = pd.read_json(f_path, lines=True)
    df = df.convert_dtypes()

    df["sim_time"] = df["sim_time"].astype(str).str.extract(r"(\d{2}:\d{2})")
    df["llm_temperature"] = df["llm_temperature"].astype(float).round(1).astype(str)
    df.rename(columns={"llm_temperature": "temp"}, inplace=True)
    df.drop(columns=["ts_created"], inplace=True)

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
all_filenames = [f.name for f in log_files]

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
        processed_files.append(session_path.name)  # Add this line
        print(f"Loaded {len(df_session)} rows")

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

        # # check for alignment
        # cols_to_check = ["datetime_start", "location", "action"]
        # print("Mismatch count")

        # # Selct comparison
        # key1 = df_observe
        # key2 = df_plan
        # print("=" * 20)
        # print(f"{get_df_name(key1)} vs {get_df_name(key2)} (#rows: {len(df_observe)})")
        # print("=" * 20)
        # # Count mismatch
        # for col in cols_to_check:
        #     print(f"{col}: ", (key1[col] != key2[col]).sum())

        # # Selct comparison
        # key1 = df_observe
        # key2 = df_act
        # print("=" * 20)
        # print(f"{get_df_name(key1)} vs {get_df_name(key2)} (#rows: {len(df_observe)})")
        # print("=" * 20)
        # # Count mismatch
        # for col in cols_to_check:
        #     print(f"{col}: ", (key1[col] != key2[col]).sum())

        # # Selct comparison
        # key1 = df_plan
        # key2 = df_act
        # print("=" * 20)
        # print(f"{get_df_name(key1)} vs {get_df_name(key2)} (#rows: {len(df_observe)})")
        # print("=" * 20)
        # # Count mismatch
        # for col in cols_to_check:
        #     print(f"{col}: ", (key1[col] != key2[col]).sum())

        # 4. Filter ORPDA columns
        # O
        o_df = df_observe[
            [
                "datetime_start",
                "location",
                "action",
                "state_summary",
                "environment_description",
            ]
        ]
        o_df.columns = o_df.columns + "_o"
        # o_df.rename(columns={"datetime_start_o": "datetime_start"}, inplace=True)

        # P
        p_df = df_plan[
            ["datetime_start", "location", "action", "topic", "state_summary"]
        ]
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
        # print("Observe:")
        # # print(o_df.columns)
        # print(o_df.tail())
        # print("Reflect:")
        # print(r_df.tail())
        # print("Plan:")
        # print(p_df.tail())
        # if mode == "orpda":
        #     print("Drift:")
        #     print(d_df.tail())
        #     print("Act:")
        # print(a_df.tail())

        # 5. Merge ORPDA with selected columns

        # Merge
        tmp = o_df.join(r_df, how="outer", lsuffix="_o", rsuffix="_r")
        tmp = tmp.join(p_df, how="outer", lsuffix="", rsuffix="_p")
        if mode == "orpda":
            tmp = tmp.join(d_df, how="outer", lsuffix="", rsuffix="_d")
        tmp = tmp.join(a_df, how="outer", lsuffix="", rsuffix="_a")

        tmp2 = pd.concat([df_session[["llm_model", "temp", "agent"]], tmp], axis=1)

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
            print("✗ Differences found:")
            for col in cols[1:]:
                mismatches = tmp2[tmp2[cols[0]] != tmp2[col]]
                if len(mismatches) > 0:
                    print(f"\n  {cols[0]} vs {col}: {len(mismatches)} mismatches")
                    print(mismatches[[cols[0], col]])

        # Track datetime mismatches for audit
        datetime_cols = [
            col for col in tmp2.columns if col.startswith("datetime_start")
        ]
        mismatch_count = 0
        mismatch_details = []

        for i in range(len(datetime_cols)):
            for j in range(i + 1, len(datetime_cols)):
                col1, col2 = datetime_cols[i], datetime_cols[j]
                mismatches = (tmp2[col1] != tmp2[col2]).sum()
                mismatch_count += mismatches
                if mismatches > 0:
                    mismatch_details.append(f"{col1} vs {col2}: {mismatches}")

        # Fix datetime columns (outside audit loop)
        datetime_col_counts = {col: tmp2[col].notna().sum() for col in datetime_cols}
        best_col = max(datetime_col_counts, key=datetime_col_counts.get)
        first_datetime = tmp2[best_col].dropna().iloc[0]

        try:
            first_datetime = pd.to_datetime(first_datetime, format="%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            first_datetime = pd.to_datetime(first_datetime)

        if pd.isna(first_datetime):
            first_datetime = pd.Timestamp("2024-01-01 00:00:00")

        datetime_range = pd.date_range(
            start=first_datetime, periods=len(tmp2), freq="15min"
        )

        # Apply fix to ALL datetime columns at once
        for col in datetime_cols:
            tmp2[col] = datetime_range

        print(
            f"Updated {len(datetime_cols)} datetime columns starting from {first_datetime}"
        )

        # Add SINGLE audit entry per file (only once, not in loop)
        audit_log.append(
            {
                "filename": session_path.name,
                "mode": mode,
                "rows_loaded": len(df_session),
                "datetime_mismatches": mismatch_count,
                "mismatch_details": "; ".join(mismatch_details),
                "status": "success",
            }
        )

        # 6. Export to CSV
        filename = session_path.name.replace(".log", ".csv")
        output_path = Path(ROOT, "app/logs/cleaned", f"cleaned_{filename}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp2.to_csv(str(output_path), index=False)
        print(f"CSV saved to {output_path}!")

        # 7. Filter Columns
        locations = tmp2.filter(regex="(time|location)")
        actions = tmp2.filter(regex="(time|action)")
        if mode == "orpda":
            drifts = tmp2.filter(regex="(time|_d)")

        import random

        random.seed(42)
        seed = random.randint(0, 10000)

        indices = o_df.sample(3, random_state=seed).index

        # print(o_df.loc[indices])
        # print(r_df.loc[indices])
        # print(p_df.loc[indices])
        # if mode == "orpda":
        #     print(d_df.loc[indices])
        # print(a_df.loc[indices])

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
            # print(filtered.tail())
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
            # print(filtered.tail())

        # print(
        #     mode.upper(),
        #     "--",
        #     filtered.loc[0, "llm_model"],
        #     "(",
        #     filtered.loc[0, "temp"],
        #     ")",
        # )
        # print(session_path)
    except (KeyError, ValueError, FileNotFoundError) as e:
        print("ERROR processing", session_path.name, ":", e)
        failed_files.append(session_path.name)  # Add this line
        continue

# create audit report
audit_df = pd.DataFrame(audit_log)
audit_path = Path(ROOT, "app/logs/cleaned", "audit_cleaning.csv")
audit_df.to_csv(str(audit_path), index=False)

print(f"\nProcessed {len(audit_log)} files")
print(f"Audit report saved to {audit_path}")
print("\nAudit Summary:")
print(audit_df[["filename", "rows_loaded", "datetime_mismatches", "status"]])

# status
print(f"\nProcessed {len(processed_files)} files successfully")
print(f"Failed {len(failed_files)} files")
if failed_files:
    print("\nFailed files:")
    for f in failed_files:
        print(f"  - {f}")
