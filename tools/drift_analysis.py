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

# Use a non-interactive backend for image generation
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _threshold_tag(th: float) -> str:
    """Make a filesystem-safe tag for a threshold value."""
    return str(th).replace(".", "_")


def plot_drift_types(by_type, intensity_sum, intensity_count, total, th, out_path: Path):
    """Bar chart of drift counts and average intensity by type."""
    if not by_type:
        return

    labels = []
    counts = []
    avg_intensity = []
    for t, c in by_type.most_common():
        labels.append(t)
        counts.append(c)
        if intensity_count[t]:
            avg_intensity.append(intensity_sum[t] / intensity_count[t])
        else:
            avg_intensity.append(float("nan"))

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    bar_positions = range(len(labels))
    ax1.bar(bar_positions, counts, color="#377eb8", alpha=0.8)
    ax1.set_xticks(bar_positions, labels, rotation=30, ha="right")
    ax1.set_ylabel("Count")
    ax1.set_title(f"Drift by Type (threshold {th})")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # Secondary axis for average intensity
    ax2 = ax1.twinx()
    ax2.plot(bar_positions, avg_intensity, color="#e41a1c", marker="o")
    ax2.set_ylabel("Avg intensity")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_hourly(by_hour_type, th, out_path: Path):
    """Line chart of drift rate by hour of day."""
    hours = list(range(24))
    rates = []
    for hour in hours:
        counts = by_hour_type.get(hour, {})
        total_hour = sum(counts.values())
        if total_hour == 0:
            rates.append(0)
            continue
        drift_only = total_hour - counts.get("none", 0)
        rates.append(drift_only / total_hour)

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(hours, rates, marker="o", color="#4daf4a")
    ax.set_xticks(range(0, 24, 2))
    ax.set_ylim(0, 1)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Drift rate")
    ax.set_title(f"Hourly Drift Rate (threshold {th})")
    ax.grid(True, linestyle="--", alpha=0.4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_action_rates(by_action, th, out_path: Path, top_n: int = 15):
    """Horizontal bar chart of drift rate by action (top N by total count)."""
    if not by_action:
        return

    # Rank by drift rate (high to low), fall back to total count to break ties.
    sorted_actions = sorted(
        by_action.items(),
        key=lambda item: (
            -(item[1]["drift"] / item[1]["total"]) if item[1]["total"] else 0,
            -item[1]["total"],
        ),
    )[:top_n]

    labels = []
    rates = []
    totals = []
    for action, agg in sorted_actions:
        total = agg["total"]
        drift = agg["drift"]
        if total == 0:
            continue
        labels.append(action)
        rates.append(drift / total)
        totals.append(total)

    if not labels:
        return

    fig, ax = plt.subplots(figsize=(8, 0.4 * len(labels) + 1.5))
    y_pos = range(len(labels))
    bars = ax.barh(y_pos, rates, color="#984ea3")
    ax.set_yticks(y_pos, labels)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Drift rate")
    ax.set_title(f"Drift Rate by Action (threshold {th})")
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    # Annotate totals at the end of each bar
    for bar, total in zip(bars, totals):
        ax.text(
            bar.get_width() + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"n={total}",
            va="center",
            ha="left",
            fontsize=8,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


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
    image_dir = Path("app/img")

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

    print(f"\nScanned session_orpda logs: {len(files)} files.")

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

        print("\nBy drift_type (non-none):")
        for t, c in by_type.most_common():
            avg = (
                intensity_sum[t] / intensity_count[t]
                if intensity_count[t]
                else float("nan")
            )
            pct = c / total if total else 0
            print(f"  {t}: {c} entries ({pct:.1%} of all), avg intensity {avg:.2f}")

        print("\nHourly pattern (effective drift after threshold):")
        for hour in sorted(by_hour_type):
            counts = by_hour_type[hour]
            total_hour = sum(counts.values())
            if total_hour == 0:
                continue
            drift_only = total_hour - counts.get("none", 0)
            rate = drift_only / total_hour
            detail = ", ".join(f"{k}:{v}" for k, v in counts.items() if v)
            print(f"  {hour:02d}:00 -> drift rate {rate:.1%} ({detail})")

        print("\nDrift rate by action (effective drift):")
        for action, agg in sorted(by_action.items()):
            if agg["total"] == 0:
                continue
            rate = agg["drift"] / agg["total"]
            print(f"  {action}: {agg['drift']} / {agg['total']} ({rate:.1%})")

        # Save plots
        th_tag = _threshold_tag(th)
        plot_drift_types(
            by_type,
            intensity_sum,
            intensity_count,
            total,
            th,
            image_dir / f"drift_types_th{th_tag}.png",
        )
        plot_hourly(
            by_hour_type,
            th,
            image_dir / f"drift_hourly_th{th_tag}.png",
        )
        plot_action_rates(
            by_action,
            th,
            image_dir / f"drift_actions_th{th_tag}.png",
        )

    print("\n\nSanity check issues:")
    if not issues:
        print("  none")
    else:
        for k, v in issues.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
