# app/src/metrics.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Ablation/metrics utilities comparing ORPDA vs ORPA and drift detection.
# --------------------------------------
"""
Ablation Metrics Module
-----------------------

This module reads explicit drift flags logged by ORPDA/ORPA to compare runs.
Inherent drift detection (semantic/implicit) is handled in the notebook
`app/src/viz_metrics.ipynb`, not here.

Compare two simulation runs:
1. ORPDA (with drift)
2. ORPA  (drift disabled)

Outputs quantitative metrics to metrics.json and metrics_plot.png.

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

import os, sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import math


ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.src.utils.embedding_utils import embed_texts, embed_text

load_dotenv()


# ============================================
# INDEPENDENT DRIFT DETECTOR (WORKS FOR ORPA)
# ============================================


def cosine_sim(a, b):
    """Compute cosine similarity for numpy arrays with zero-safe denom."""
    if a is None or b is None:
        return 0.0
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def text_cosine_sim(text_a: str, text_b: str) -> float:
    """Compute cosine similarity for two text strings via embeddings."""
    texts = [text_a or "", text_b or ""]
    if not any(texts):
        return 0.0
    vecs = embed_texts(texts)
    if len(vecs) != 2:
        return 0.0
    return cosine_sim(vecs[0], vecs[1])


def detect_inherent_drift(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects semantic drift even when drift operator is disabled.
    - Compares PLAN topic vs ACTION topic
    - Compares OBSERVATION summary vs ACTION summary
    - Checks for internal mental wandering in state_summary
    """
    orpda = row.get("orpda", {})

    obs = orpda.get("observation", {}) or {}
    ref = orpda.get("reflection", {}) or {}
    plan = orpda.get("plan", {}) or {}
    drift = orpda.get("drift_decision", {}) or {}
    action = orpda.get("action_result", {}) or {}

    plan_topic = plan.get("topic")
    action_topic = action.get("topic")
    obs_summary = obs.get("state_summary")
    act_summary = action.get("state_summary")

    def _empty_result():
        return {
            "inherent_drift": False,
            "drift_score_inferred": 0.0,
            "drift_type_inferred": "none",
            "sim_plan_action": 0.0,
            "sim_obs_action": 0.0,
        }

    # ------------- Embedding-based semantic drift -------------
    texts = [plan_topic, action_topic, obs_summary, act_summary]
    texts = [t if t else "" for t in texts]

    if all(t == "" for t in texts):
        return _empty_result()

    vecs = embed_texts(texts)
    if len(vecs) != 4:
        return _empty_result()

    v_plan, v_action, v_obs, v_actsum = vecs

    sim_plan_action = cosine_sim(v_plan, v_action)
    sim_obs_act = cosine_sim(v_obs, v_actsum)

    # A drift event is when the action topic deviates from plan
    topic_drift = sim_plan_action < 0.55

    # Mentally wandering
    summary_drift = sim_obs_act < 0.55

    # Additional textual drift detection (internal monologue patterns)
    summary_text = (act_summary or "").lower()
    wandering_markers = [
        "thinking about",
        "mentally",
        "reflecting on",
        "daydream",
        "wandering",
        "exploring",
    ]
    mental_drift = any(w in summary_text for w in wandering_markers)

    # Combine signals
    drift_score = 1.0 - max(sim_plan_action, sim_obs_act)
    is_drift = topic_drift or summary_drift or mental_drift

    # Infer drift type (rough inference)
    if not is_drift:
        drift_type = "none"
    else:
        if mental_drift:
            drift_type = "internal"
        elif topic_drift:
            drift_type = "behavioral"
        else:
            drift_type = "attentional_leak"

    return {
        "inherent_drift": bool(is_drift),
        "drift_score_inferred": float(drift_score),
        "drift_type_inferred": drift_type,
        "sim_plan_action": sim_plan_action,
        "sim_obs_action": sim_obs_act,
    }


def compute_inherent_drift_rate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute drift stats for ORPA (no explicit drift).
    """
    events = [detect_inherent_drift(r) for r in rows]

    drift_flags = [e["inherent_drift"] for e in events]
    drift_scores = [e["drift_score_inferred"] for e in events]

    if len(events) == 0:
        return {"inherent_drift_rate": 0.0, "avg_drift_score_inferred": 0.0}

    return {
        "inherent_drift_rate": sum(drift_flags) / len(events),
        "avg_drift_score_inferred": float(np.mean(drift_scores)),
        "drift_type_distribution": {
            "internal": sum(
                1 for e in events if e["drift_type_inferred"] == "internal"
            ),
            "attentional_leak": sum(
                1 for e in events if e["drift_type_inferred"] == "attentional_leak"
            ),
            "behavioral": sum(
                1 for e in events if e["drift_type_inferred"] == "behavioral"
            ),
            "none": sum(1 for e in events if e["drift_type_inferred"] == "none"),
        },
    }


# ============================
# Utility: Load Session Logs
# ============================


def cosine_similarity(a, b):
    """Compute cosine similarity between two embedding vectors."""
    if not a or not b:
        return 0.0

    if len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def load_log(path: Path) -> List[Dict]:
    """Load a JSONL session log into a list of dict rows."""
    rows = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def get_latest_logs(log_dir: Path) -> Tuple[Path, Path]:
    """Return the newest ORPDA and ORPA session logs."""
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


def infer_step_minutes(rows: List[Dict], default: float = 15.0) -> float:
    """Infer minutes per tick from sim_time strings, fallback to default."""
    if len(rows) < 2:
        return default
    fmt = "%Y-%m-%d %H:%M"
    try:
        t0 = datetime.strptime(rows[0]["sim_time"], fmt)
        t1 = datetime.strptime(rows[1]["sim_time"], fmt)
        delta_min = (t1 - t0).total_seconds() / 60.0
        if delta_min <= 0:
            return default
        return delta_min
    except Exception:
        return default


# ============================
# Plotting
# ============================


def plot_metrics(metrics: Dict, out_path: Path):
    """Render bar/line plots comparing with- and without-drift runs."""
    import matplotlib.gridspec as gridspec

    labels, with_vals, no_vals = [], [], []
    table_rows = []

    for key, sub in metrics.items():
        # Skip non-scalar comparators (like drift_type_distribution blocks) and n_ticks
        if key == "n_ticks":
            continue
        if (
            isinstance(sub, dict)
            and "with_drift" in sub
            and isinstance(sub.get("with_drift"), (int, float))
        ):
            labels.append(key)
            with_vals.append(sub["with_drift"])
            no_vals.append(sub["no_drift"])
            table_rows.append([key, sub.get("definition", "")])

    x = range(len(labels))
    width = 0.35

    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 2])

    ax_bar = fig.add_subplot(gs[0])
    ax_table = fig.add_subplot(gs[1])

    # Bar chart
    ax_bar.bar(
        [i - width / 2 for i in x],
        with_vals,
        width,
        label="With Drift",
    )
    ax_bar.bar(
        [i + width / 2 for i in x],
        no_vals,
        width,
        label="No Drift",
    )

    ax_bar.set_ylabel("Metric Value")
    ax_bar.set_xticks(list(x))
    ax_bar.set_xticklabels(labels, rotation=20, ha="right")
    ax_bar.set_title("Ablation: ORPDA (with drift) vs ORPA (no drift)")
    ax_bar.legend()

    # Table
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

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(0.8)
        cell.PAD = 0.02
        if row == 0:
            cell.set_facecolor("#E8E8E8")
            cell.get_text().set_fontweight("bold")

    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ============================
# Core Drift Statistics
# ============================


def _collect_drift_rows(rows: List[Dict]) -> List[Dict]:
    """Filter rows to only those with should_drift=True."""
    drift_rows = []
    for r in rows:
        drift = r.get("orpda", {}).get("drift_decision", {}) or {}
        if drift.get("should_drift"):
            drift_rows.append({"row": r, "drift": drift})
    return drift_rows


def compute_drift_rate(rows: List[Dict]) -> float:
    """Proportion of ticks where the agent decides to drift."""
    drift_rows = _collect_drift_rows(rows)
    return len(drift_rows) / max(1, len(rows))


def compute_drift_time_fraction(rows: List[Dict]) -> float:
    """
    Fraction of simulated time spent in drift.
    Approximates as: (# drift ticks * step_minutes) / (total_ticks * step_minutes).
    Equivalent to drift_rate, but kept explicit for interpretation.
    """
    step_minutes = infer_step_minutes(rows)
    drift_rows = _collect_drift_rows(rows)
    total_minutes = max(1.0, len(rows) * step_minutes)
    drift_minutes = len(drift_rows) * step_minutes
    return drift_minutes / total_minutes


def compute_intensity_weighted_drift_fraction(rows: List[Dict]) -> float:
    """
    Estimates fraction of mental time-weighted drift:
    mean(drift_intensity) * drift_rate.
    """
    drift_rows = _collect_drift_rows(rows)
    if not drift_rows:
        return 0.0
    intensities = [float(dr["drift"].get("drift_intensity", 0.0)) for dr in drift_rows]
    avg_intensity = sum(intensities) / max(1, len(intensities))
    drift_rate = len(drift_rows) / max(1, len(rows))
    return avg_intensity * drift_rate


def compute_drifts_per_hour_and_day(rows: List[Dict]) -> Dict[str, float]:
    """
    Drifts per simulated hour and extrapolated to a 16-hour waking day.
    """
    if not rows:
        return {"drifts_per_hour": 0.0, "drifts_per_16h_day": 0.0}

    step_minutes = infer_step_minutes(rows)
    total_hours = (len(rows) * step_minutes) / 60.0
    drift_rows = _collect_drift_rows(rows)
    n_drifts = len(drift_rows)
    drifts_per_hour = n_drifts / max(1e-6, total_hours)
    drifts_per_16h = drifts_per_hour * 16.0
    return {
        "drifts_per_hour": drifts_per_hour,
        "drifts_per_16h_day": drifts_per_16h,
    }


# ============================
# Drift Type Distribution
# ============================


def compute_drift_type_distribution(rows: List[Dict]) -> Dict[str, float]:
    """
    Ratio of each drift_type among drift ticks.
    drift_type: "internal" | "attentional_leak" | "behavioral" | other.
    """
    drift_rows = _collect_drift_rows(rows)
    counts = {
        "internal": 0,
        "attentional_leak": 0,
        "behavioral": 0,
        "other": 0,
    }
    for dr in drift_rows:
        t = (dr["drift"].get("drift_type") or "").strip().lower()
        if t in counts:
            counts[t] += 1
        else:
            counts["other"] += 1

    total = max(1, sum(counts.values()))
    return {k: v / total for k, v in counts.items()}


# ============================
# Attention & Stability
# ============================


def compute_attention_stability_ratio(rows: List[Dict]) -> float:
    """
    Proportion of ticks labeled 'stable' in reflection.attention_stability.
    """
    stable = 0
    for r in rows:
        ref = r.get("orpda", {}).get("reflection", {}) or {}
        if ref.get("attention_stability") == "stable":
            stable += 1
    return stable / max(1, len(rows))


# ============================
# Embedding-Based Metrics
# ============================


def _safe_embed(texts: List[str]):
    """Embed only non-empty strings, guarding against bad input."""
    texts = [t for t in texts if isinstance(t, str) and t.strip()]
    if len(texts) == 0:
        return []
    return embed_texts(texts)


def compute_drift_topic_coherence(rows: List[Dict]) -> float:
    """
    Average cosine similarity between consecutive drift topics.
    High = coherent, low = scattered.
    """
    drift_rows = _collect_drift_rows(rows)
    topics = []
    for dr in drift_rows:
        topic = dr["drift"].get("drift_topic")
        if isinstance(topic, str) and topic.strip():
            topics.append(topic.strip())

    if len(topics) < 2:
        return 0.0

    vecs = _safe_embed(topics)
    if len(vecs) < 2:
        return 0.0

    sims = []
    for i in range(len(vecs) - 1):
        sims.append(cosine_similarity(vecs[i], vecs[i + 1]))
    if not sims:
        return 0.0
    return sum(sims) / len(sims)


def compute_justification_consistency(rows: List[Dict]) -> float:
    """
    Average cosine similarity between consecutive drift justifications.
    High = stable reasoning narrative.
    """
    drift_rows = _collect_drift_rows(rows)
    justifications = []
    for dr in drift_rows:
        j = dr["drift"].get("justification")
        if isinstance(j, str) and j.strip():
            justifications.append(j.strip())

    if len(justifications) < 2:
        return 0.0

    vecs = _safe_embed(justifications)
    if len(vecs) < 2:
        return 0.0

    sims = []
    for i in range(len(vecs) - 1):
        sims.append(cosine_similarity(vecs[i], vecs[i + 1]))
    if not sims:
        return 0.0
    return sum(sims) / len(sims)


def compute_semantic_plan_deviation(rows: List[Dict]) -> float:
    """
    Average 1 - cosine_similarity between plan.topic and drift_topic
    on ticks where both exist and should_drift is True.
    High = drift moves far from plan; low = drift stays near plan.
    """
    pairs = []
    for r in rows:
        drift = r.get("orpda", {}).get("drift_decision", {}) or {}
        plan = r.get("orpda", {}).get("plan", {}) or {}
        if not drift.get("should_drift"):
            continue

        drift_topic = drift.get("drift_topic")
        plan_topic = plan.get("topic")
        if (
            isinstance(drift_topic, str)
            and drift_topic.strip()
            and isinstance(plan_topic, str)
            and plan_topic.strip()
        ):
            pairs.append((plan_topic.strip(), drift_topic.strip()))

    if not pairs:
        return 0.0

    # Embed all texts in one shot
    flat_texts = []
    for a, b in pairs:
        flat_texts.append(a)
        flat_texts.append(b)

    vecs = _safe_embed(flat_texts)
    if len(vecs) != len(flat_texts):
        # Fallback: no embeddings computed
        return 0.0

    deviations = []
    for i in range(0, len(vecs), 2):
        v_plan = vecs[i]
        v_drift = vecs[i + 1]
        sim = cosine_similarity(v_plan, v_drift)
        deviations.append(1.0 - sim)

    if not deviations:
        return 0.0
    return sum(deviations) / len(deviations)


# ============================
# Legacy Behavior Metrics (Optional but still useful)
# ============================


def compute_task_switches(rows: List[Dict]) -> int:
    """
    Number of times the agent changes its action between ticks.
    """
    switches = 0
    last_action = None

    for r in rows:
        act = r.get("orpda", {}).get("action_result", {}).get("action")
        if act and last_action and act != last_action:
            switches += 1
        last_action = act

    return switches


def compute_plan_adherence(rows: List[Dict]) -> float:
    """
    Fraction of ticks where executed action matches planned action.
    """
    aligned = 0
    for r in rows:
        plan = r.get("orpda", {}).get("plan", {}).get("action")
        act = r.get("orpda", {}).get("action_result", {}).get("action")
        if plan and act and plan == act:
            aligned += 1
    return aligned / max(1, len(rows))


def compute_action_diversity(rows: List[Dict]) -> float:
    """Count unique actions taken across the run."""
    actions = set()
    for r in rows:
        act = r.get("orpda", {}).get("action_result", {}).get("action")
        if act:
            actions.add(act)
    return float(len(actions))


# ============================
# High-Level Wrapper
# ============================


def compute_metrics(LOG_DIR: Path) -> Dict:
    """Load latest ORPDA/ORPA logs and compute comparison metrics."""
    orpda_path, orpa_path = get_latest_logs(LOG_DIR)

    orpda_rows = load_log(orpda_path)
    orpa_rows = load_log(orpa_path)

    # Core stats for both conditions
    orpda_step_minutes = infer_step_minutes(orpda_rows)
    orpa_step_minutes = infer_step_minutes(orpa_rows)

    orpda_drift_rate = compute_drift_rate(orpda_rows)
    orpa_drift_rate = compute_drift_rate(orpa_rows)

    orpda_drift_time_frac = compute_drift_time_fraction(orpda_rows)
    orpa_drift_time_frac = compute_drift_time_fraction(orpa_rows)

    orpda_intensity_frac = compute_intensity_weighted_drift_fraction(orpda_rows)
    orpa_intensity_frac = compute_intensity_weighted_drift_fraction(orpa_rows)

    orpda_dph = compute_drifts_per_hour_and_day(orpda_rows)
    orpa_dph = compute_drifts_per_hour_and_day(orpa_rows)

    orpda_types = compute_drift_type_distribution(orpda_rows)
    orpa_types = compute_drift_type_distribution(orpa_rows)

    metrics = {
        # Core drift volume
        "drift_rate": {
            "definition": "Proportion of ticks where the agent decides to drift.",
            "with_drift": orpda_drift_rate,
            "no_drift": orpa_drift_rate,
        },
        "drift_time_fraction": {
            "definition": "Fraction of simulated time spent in drift (unweighted).",
            "with_drift": orpda_drift_time_frac,
            "no_drift": orpa_drift_time_frac,
        },
        "intensity_weighted_drift_fraction": {
            "definition": "Estimated mental time in drift: drift_rate × mean drift_intensity.",
            "with_drift": orpda_intensity_frac,
            "no_drift": orpa_intensity_frac,
        },
        "drifts_per_hour": {
            "definition": "Average number of drift events per simulated hour.",
            "with_drift": orpda_dph["drifts_per_hour"],
            "no_drift": orpa_dph["drifts_per_hour"],
        },
        "drifts_per_16h_day": {
            "definition": "Extrapolated drift count over a 16-hour waking day.",
            "with_drift": orpda_dph["drifts_per_16h_day"],
            "no_drift": orpa_dph["drifts_per_16h_day"],
        },
        # Drift types (ratios, not plotted by default but useful in JSON)
        "drift_type_internal_ratio": {
            "definition": "Share of drift events classified as internal (thought/rumination).",
            "with_drift": orpda_types.get("internal", 0.0),
            "no_drift": orpa_types.get("internal", 0.0),
        },
        "drift_type_attentional_leak_ratio": {
            "definition": "Share of drift events classified as attentional leaks (environment, notifications, etc.).",
            "with_drift": orpda_types.get("attentional_leak", 0.0),
            "no_drift": orpa_types.get("attentional_leak", 0.0),
        },
        "drift_type_behavioral_ratio": {
            "definition": "Share of drift events classified as behavioral (changing physical task/behavior).",
            "with_drift": orpda_types.get("behavioral", 0.0),
            "no_drift": orpa_types.get("behavioral", 0.0),
        },
        # Stability + embeddings
        "attention_stability_ratio": {
            "definition": "Proportion of ticks labeled as 'stable' in reflection.attention_stability.",
            "with_drift": compute_attention_stability_ratio(orpda_rows),
            "no_drift": compute_attention_stability_ratio(orpa_rows),
        },
        "drift_topic_coherence": {
            "definition": "Average cosine similarity between consecutive drift topics (1 = highly coherent, 0 = orthogonal).",
            "with_drift": compute_drift_topic_coherence(orpda_rows),
            "no_drift": compute_drift_topic_coherence(orpa_rows),
        },
        "justification_consistency": {
            "definition": "Average cosine similarity between consecutive drift justifications.",
            "with_drift": compute_justification_consistency(orpda_rows),
            "no_drift": compute_justification_consistency(orpa_rows),
        },
        "semantic_plan_deviation": {
            "definition": "Average semantic distance (1 - cosine similarity) between plan.topic and drift_topic on drift ticks.",
            "with_drift": compute_semantic_plan_deviation(orpda_rows),
            "no_drift": compute_semantic_plan_deviation(orpa_rows),
        },
        # Legacy behavioral metrics (still informative)
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
        "action_diversity": {
            "definition": "Number of unique actions taken during the run.",
            "with_drift": compute_action_diversity(orpda_rows),
            "no_drift": compute_action_diversity(orpa_rows),
        },
        # Session size / timing
        "n_ticks": {
            "definition": "Total number of ticks in the session.",
            "with_drift": len(orpda_rows),
            "no_drift": len(orpa_rows),
        },
        "minutes_per_tick": {
            "definition": "Inferred minutes per simulation tick.",
            "with_drift": orpda_step_minutes,
            "no_drift": orpa_step_minutes,
        },
    }

    return metrics


# ============================
# Save to metrics.json
# ============================


def save_metrics(metrics: Dict, out_path: Path):
    """Write computed metrics to JSON on disk."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(metrics, indent=2))


# ============================
# Entry Point
# ============================

if __name__ == "__main__":
    ROOT = Path.cwd()
    print(ROOT)
    LOG_DIR = ROOT / "app/logs"
    print(LOG_DIR)
    out_metrics = LOG_DIR / "metrics.json"
    out_plot = LOG_DIR / "metrics_plot.png"

    metrics = compute_metrics(LOG_DIR)
    save_metrics(metrics, out_metrics)
    plot_metrics(metrics, out_plot)

    print("✓ Metrics computed and saved")
    print(f"- JSON: {out_metrics}")
    print(f"- Plot: {out_plot}")
