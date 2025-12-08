#!/usr/bin/env python3
"""
Analyze drift intensity and type across top-level session logs in app/logs.

Usage:
    python tools/drift_analysis.py
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def main() -> None:
    log_dir = Path("app/logs")
    files = sorted(
        p
        for p in log_dir.iterdir()
        if p.is_file()
        and p.name.startswith("session_orpda_")
        and p.name.endswith(".log")
    )

    # Effective drift threshold (intensity below this is treated as no drift)
    thresholds = [0.5]

    issues = Counter()

    stats = {
        th: {
            "total": 0,
            "drift": 0,
            "by_type": Counter(),
            "intensity_sum": defaultdict(float),
            "intensity_count": defaultdict(int),
            "by_hour_type": defaultdict(Counter),  # hour -> drift_type -> count
            "by_action": defaultdict(lambda: {"total": 0, "drift": 0}),
        }
        for th in thresholds
    }

    for fp in files:
        with fp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ar = (
                    row.get("orpda", {}).get("action_result")
                    or row.get("action_result")
                    or row.get("orpda", {}).get("observation")
                    or {}
                )

                for th in thresholds:
                    stats[th]["total"] += 1
                drift_type = ar.get("drift_type", "none") or "none"
                should_drift = bool(ar.get("should_drift", False))
                intensity = ar.get("drift_intensity")
                if intensity is None or isinstance(intensity, str):
                    try:
                        intensity = float(intensity)
                    except Exception:
                        intensity = None
                action = ar.get("action", "unknown") or "unknown"

                for th in thresholds:
                    effective_type = drift_type
                    if intensity is not None and intensity < th:
                        effective_type = "none"

                    stats[th]["by_action"][action]["total"] += 1
                    if effective_type != "none":
                        stats[th]["drift"] += 1
                        stats[th]["by_type"][effective_type] += 1
                        stats[th]["by_action"][action]["drift"] += 1
                        if intensity is not None:
                            stats[th]["intensity_sum"][effective_type] += intensity
                            stats[th]["intensity_count"][effective_type] += 1

                if should_drift and drift_type == "none":
                    issues["should_drift_true_but_type_none"] += 1
                if (not should_drift) and drift_type != "none":
                    issues["type_non_none_but_should_drift_false"] += 1
                if drift_type == "none" and intensity not in (None, 0, 0.0):
                    issues["none_type_with_intensity"] += 1
                if drift_type != "none" and (
                    intensity is None or math.isnan(intensity)
                ):
                    issues["drift_no_intensity"] += 1

                # hour distribution per threshold
                sim_time = row.get("sim_time")
                if sim_time:
                    try:
                        hour = datetime.strptime(sim_time, "%Y-%m-%d %H:%M").hour
                        for th in thresholds:
                            effective_type = drift_type
                            if intensity is not None and intensity < th:
                                effective_type = "none"
                            stats[th]["by_hour_type"][hour][effective_type] += 1
                    except Exception:
                        pass

    print(f"Scanned session_orpda logs: {len(files)} files.")

    for th in thresholds:
        total = stats[th]["total"]
        drift = stats[th]["drift"]
        by_type = stats[th]["by_type"]
        intensity_sum = stats[th]["intensity_sum"]
        intensity_count = stats[th]["intensity_count"]
        by_hour_type = stats[th]["by_hour_type"]
        by_action = stats[th]["by_action"]

        print(f"\n=== Threshold {th:.1f} ===")
        if total:
            drift_rate = drift / total
            print(f"Drift present: {drift} / {total} ({drift_rate:.1%}).")
        else:
            print("No records.")
            continue

        print("By drift_type (non-none):")
        for t, c in by_type.most_common():
            avg = (
                intensity_sum[t] / intensity_count[t]
                if intensity_count[t]
                else float("nan")
            )
            pct = c / total if total else 0
            print(f"  {t}: {c} entries ({pct:.1%} of all), avg intensity {avg:.2f}")

        print("Hourly pattern (effective drift after threshold):")
        for hour in sorted(by_hour_type):
            counts = by_hour_type[hour]
            total_hour = sum(counts.values())
            if total_hour == 0:
                continue
            drift_only = total_hour - counts.get("none", 0)
            rate = drift_only / total_hour
            detail = ", ".join(f"{k}:{v}" for k, v in counts.items() if v)
            print(f"  {hour:02d}:00 -> drift rate {rate:.1%} ({detail})")

        print("Drift rate by action (effective drift):")
        for action, agg in sorted(by_action.items()):
            if agg["total"] == 0:
                continue
            rate = agg["drift"] / agg["total"]
            print(f"  {action}: {agg['drift']} / {agg['total']} ({rate:.1%})")

    print("\nSanity check issues:")
    if not issues:
        print("  none")
    else:
        for k, v in issues.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
