"""
Ablation Metrics Module
-----------------------

Compare two simulation runs:
1. ORPDA (with drift)
2. ORPA  (drift disabled)

Outputs quantitative metrics to metrics.log.

Each run is a JSON-lines log file where each line is:
{
    "sim_time": "...",
    "tick": int,
    "orpda": {
        "observation": {...},
        "reflection": {...},
        "plan": {...},
        "drift_decision": {...},
        "action_result": {...}
    }
}
"""

import json
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt


# ============================
# Utility: Load Session Logs
# ============================


def load_log(path: Path) -> List[Dict]:
    rows = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def get_latest_logs(log_dir: Path):
    orpda_logs = sorted(
        log_dir.glob("session_orpda_*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    orpa_logs = sorted(
        log_dir.glob("session_orpa_*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not orpda_logs or not orpa_logs:
        raise RuntimeError("Need at least one ORPDA and one ORPA log.")

    return orpda_logs[0], orpa_logs[0]


def plot_metrics(metrics: Dict, out_path: Path):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    # --- Prepare data ---
    labels, with_vals, no_vals = [], [], []
    table_rows = []

    for key, sub in metrics.items():
        if key == "n_ticks":
            continue
        if isinstance(sub, dict) and "with_drift" in sub:
            labels.append(key)
            with_vals.append(sub["with_drift"])
            no_vals.append(sub["no_drift"])
            table_rows.append([key, sub.get("definition", "")])

    x = range(len(labels))
    width = 0.35

    # --- Create figure ---
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 2])

    ax_bar = fig.add_subplot(gs[0])
    ax_table = fig.add_subplot(gs[1])

    # --- Bar chart ---
    ax_bar.bar(
        [i - width / 2 for i in x],
        with_vals,
        width,
        label="With Drift",
        color="#4CAF50",
    )
    ax_bar.bar(
        [i + width / 2 for i in x], no_vals, width, label="No Drift", color="#B0B0B0"
    )

    ax_bar.set_ylabel("Metric Value")
    ax_bar.set_xticks(list(x))
    ax_bar.set_xticklabels(labels, rotation=20, ha="right")
    ax_bar.set_title("Ablation: ORPDA (with drift) vs ORPA (no drift)")
    ax_bar.legend()

    # --- Table ---
    ax_table.axis("off")

    col_labels = ["Metric", "Definition"]

    table = ax_table.table(
        cellText=table_rows,
        colLabels=col_labels,
        colWidths=[0.25, 0.75],
        loc="center",
        cellLoc="left",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)

    # Style cells
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(0.8)
        cell.PAD = 0.02

        # Header row (row = 0)
        if row == 0:
            cell.set_facecolor("#E8E8E8")
            cell.get_text().set_fontweight("bold")

    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ============================
# Metric 1: Drift Frequency
# ============================


def compute_drift_frequency(rows: List[Dict]) -> float:
    count = 0
    for r in rows:
        drift = r.get("orpda", {}).get("drift_decision", {})
        if drift.get("should_drift") is True:
            count += 1
    return count / max(1, len(rows))


# ============================
# Metric 2: Drift Intensity (avg)
# ============================


def compute_avg_drift_intensity(rows: List[Dict]) -> float:
    intensities = []
    for r in rows:
        drift = r.get("orpda", {}).get("drift_decision", {})
        if drift.get("should_drift"):
            intensities.append(float(drift.get("drift_intensity", 0)))
    return sum(intensities) / max(1, len(intensities))


# ============================
# Metric 3: Task Switching Cost
# ============================


def compute_task_switches(rows: List[Dict]) -> int:
    switches = 0
    last_action = None

    for r in rows:
        act = r.get("orpda", {}).get("action_result", {}).get("action")
        if act and last_action and act != last_action:
            switches += 1
        last_action = act

    return switches


# ============================
# Metric 4: Plan Adherence Score
# ============================
# proportion of ticks where action == plan


def compute_plan_adherence(rows: List[Dict]) -> float:
    aligned = 0

    for r in rows:
        plan = r.get("orpda", {}).get("plan", {}).get("action")
        act = r.get("orpda", {}).get("action_result", {}).get("action")
        if plan and act and plan == act:
            aligned += 1

    return aligned / max(1, len(rows))


# ============================
# Metric 5: Attention Stability
# ============================


def compute_attention_stability(rows: List[Dict]) -> float:
    score = 0
    for r in rows:
        ref = r.get("orpda", {}).get("reflection", {})
        if ref.get("attention_stability") == "stable":
            score += 1
    return score / max(1, len(rows))


# ============================
# Metric 6: Action Diversity
# ============================


def compute_action_diversity(rows: List[Dict]) -> float:
    actions = set()
    for r in rows:
        act = r.get("orpda", {}).get("action_result", {}).get("action")
        if act:
            actions.add(act)
    return len(actions)


# ============================
# High-Level Wrapper
# ============================


def compute_metrics(LOG_DIR) -> Dict:
    orpda_path, orpa_path = get_latest_logs(LOG_DIR)

    # Load logs into structured rows
    orpda_rows = load_log(orpda_path)
    orpa_rows = load_log(orpa_path)

    metrics = {
        "drift_frequency": {
            "definition": "Proportion of ticks where the agent decides to drift.",
            "with_drift": compute_drift_frequency(orpda_rows),
            "no_drift": compute_drift_frequency(orpa_rows),
        },
        "avg_drift_intensity": {
            "definition": "Average magnitude of drift when drifting occurs (0–1).",
            "with_drift": compute_avg_drift_intensity(orpda_rows),
            "no_drift": compute_avg_drift_intensity(orpa_rows),
        },
        "task_switch_cost": {
            "definition": "Number of times the agent changes its action between ticks.",
            "with_drift": compute_task_switches(orpda_rows),
            "no_drift": compute_task_switches(orpa_rows),
        },
        "plan_adherence": {
            "definition": "Fraction of ticks where executed action matches planned action.",
            "with_drift": compute_plan_adherence(orpda_rows),
            "no_drift": compute_plan_adherence(orpa_rows),
        },
        "attention_stability": {
            "definition": "Proportion of ticks marked as 'stable' attention in reflection.",
            "with_drift": compute_attention_stability(orpda_rows),
            "no_drift": compute_attention_stability(orpa_rows),
        },
        "action_diversity": {
            "definition": "Number of unique actions taken during the run.",
            "with_drift": compute_action_diversity(orpda_rows),
            "no_drift": compute_action_diversity(orpa_rows),
        },
        "n_ticks": {
            "definition": "Total number of ticks in the session.",
            "with_drift": len(orpda_rows),
            "no_drift": len(orpa_rows),
        },
    }

    return metrics


# ============================
# Save to metrics.log
# ============================


def save_metrics(metrics: Dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(metrics, indent=2))


# ============================
# Entry Point
# ============================

if __name__ == "__main__":
    ROOT = Path.cwd()
    LOG_DIR = ROOT / "app/logs"
    out_metrics = LOG_DIR / "metrics.json"
    out_plot = LOG_DIR / "metrics_plot.png"

    metrics = compute_metrics(LOG_DIR)
    save_metrics(metrics, out_metrics)
    plot_metrics(metrics, out_plot)

    print("✓ Metrics computed and saved")
    print(f"- JSON: {out_metrics}")
    print(f"- Plot: {out_plot}")
