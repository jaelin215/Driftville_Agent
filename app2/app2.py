# app2/app2.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Flask-based UI preview for Driftville personas and schedule viewer.
# --------------------------------------

import csv
import json
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
APP = Flask(__name__, template_folder=str(TEMPLATE_DIR))
PERSONA_PATH = (
    Path(__file__).resolve().parent.parent / "app/src/driftville_personas.json"
)
RAW_PERSONA_PATH = (
    Path(__file__).resolve().parent.parent / "app/src/smallville_personas.json"
)


def _minutes_from_dt(dt_str: str) -> int:
    try:
        parts = dt_str.split(" ")
        hm = parts[1]
        h, m = hm.split(":")[:2]
        return int(h) * 60 + int(m)
    except Exception:
        return 0


def load_personas():
    """Load personas from driftville_personas.json and normalize schedules, attaching raw bios."""
    with PERSONA_PATH.open() as f:
        raw = json.load(f)

    raw_map = {}
    if RAW_PERSONA_PATH.exists():
        try:
            with RAW_PERSONA_PATH.open() as f:
                raw_src = json.load(f)
                for item in raw_src:
                    raw_map[item.get("name")] = item.get("raw_persona", "")
        except Exception:
            raw_map = {}

    personas = []
    for entry in raw:
        p = entry.get("persona", {})
        name = p.get("name", "Unknown")
        schedule = []
        for slot in entry.get("schedule", []):
            start_min = _minutes_from_dt(slot.get("datetime_start", "00:00"))
            dur = int(slot.get("duration_min", 0))
            schedule.append(
                {
                    "datetime_start": slot.get("datetime_start"),
                    "start_time": start_min,
                    "end_time": start_min + dur,
                    "duration_min": dur,
                    "location": slot.get("location", "home"),
                    "action": slot.get("action", ""),
                    "environment_description": slot.get("environment_description", ""),
                    "notes": slot.get("notes", ""),
                }
            )
        personas.append(
            {
                "name": name,
                "raw_persona": raw_map.get(name, ""),
                "schedule": schedule,
            }
        )
    return personas


PERSONAS = load_personas()
SESSION_LOGS_DIR = Path(__file__).resolve().parent.parent / "app/logs"
EVAL_DIR = Path(__file__).resolve().parent.parent / "app" / "eval"
FEEDBACK_CSV = EVAL_DIR / "layer_feedback.csv"


def load_session_data():
    """Load ORPDA/ORPA session logs and group entries by agent."""

    def load_variant(prefix: str):
        if not SESSION_LOGS_DIR.exists():
            return {}
        files = sorted(
            SESSION_LOGS_DIR.glob(f"session_{prefix}_*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        by_agent = {}
        for path in files:
            try:
                with path.open() as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except Exception:
                            continue
                        agent = entry.get("agent")
                        if not agent:
                            continue
                        by_agent.setdefault(agent, []).append(entry)
            except Exception:
                continue
        return by_agent

    return {"orpda": load_variant("orpda"), "orpa": load_variant("orpa")}


EMOJI_MAP = {
    "Isabella Rodriguez": "☕️",
    "Tom Moreno": "🛒",
    "Giorgio Rossi": "📐",
    "Adam Smith": "📚",
    "Sam Moore": "🪴",
    "Maria Lopez": "🎮",
    "Mei Lin": "🎓",
    "Jennifer Moore": "🎨",
    "Hailey Johnson": "✍️",
    "Eddy Lin": "🎼",
    "John Lin": "💊",
    "Abigail Chen": "🖥️",
}
FACE_MAP = {
    "Isabella Rodriguez": "👩",
    "Tom Moreno": "👨",
    "Giorgio Rossi": "👨",
    "Adam Smith": "👨",
    "Sam Moore": "👨",
    "Maria Lopez": "👩",
    "Mei Lin": "👩",
    "Jennifer Moore": "👩",
    "Hailey Johnson": "👩",
    "Eddy Lin": "👨",
    "John Lin": "👨",
    "Abigail Chen": "👩",
}


@APP.route("/")
def home():
    show_eval = bool(request.args.get("eval"))
    return render_template(
        "index.html",
        personas=PERSONAS,
        emoji_map=EMOJI_MAP,
        face_map=FACE_MAP,
        session_data=load_session_data(),
        show_eval=show_eval,
    )


@APP.post("/simulate_conversation")
def simulate_conversation():
    """
    Handles POST requests to simulate a conversation between two agents.
    Returns a stubbed dialogue between the provided agent names, or an error if input is invalid.
    """
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    a = (payload or {}).get("agent1")
    b = (payload or {}).get("agent2") or a
    if not a:
        return jsonify({"error": "Provide agent1"}), 400

    # Stubbed response; replace with your real simulation
    dialogue = [
        {"speaker": a, "text": f"Hey {b}, want to chat about Driftville?"},
        {"speaker": b, "text": f"Sure, {a}! Let's see what's happening in town."},
    ]
    return jsonify({"status": "ok", "agents": [a, b], "dialogue": dialogue})


@APP.post("/feedback")
def save_feedback():
    """Capture layer-level feedback and append to app/eval/layer_feedback.csv."""
    payload = request.get_json(force=True, silent=True) or {}
    stage = payload.get("stage")
    verdict = payload.get("verdict")
    comment = payload.get("comment") or ""
    personas = payload.get("personas") or []
    minute = payload.get("minute") or ""
    session_date = payload.get("session_date") or ""
    schedule_range = payload.get("schedule_range") or ""
    if not stage or not verdict:
        return jsonify({"error": "stage and verdict are required"}), 400

    try:
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        is_new = not FEEDBACK_CSV.exists()
        with FEEDBACK_CSV.open("a", newline="") as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(
                    [
                        "ts_utc",
                        "stage",
                        "verdict",
                        "comment",
                        "personas",
                        "minute",
                        "session_date",
                        "schedule_range",
                    ]
                )
            writer.writerow(
                [
                    datetime.utcnow().isoformat() + "Z",
                    stage,
                    verdict,
                    comment.replace("\n", " ").strip(),
                    "|".join(personas),
                    minute,
                    session_date,
                    schedule_range,
                ]
            )
    except Exception as exc:  # pragma: no cover - defensive path
        return jsonify({"error": f"Failed to save feedback: {exc}"}), 500

    return jsonify({"status": "ok"})


@APP.get("/eval")
def list_feedback():
    """Return feedback rows as JSON (default) or HTML when requested."""
    if not FEEDBACK_CSV.exists():
        if (
            request.accept_mimetypes.accept_html
            and not request.accept_mimetypes.accept_json
        ):
            return render_template("eval.html", feedback=[])
        return jsonify({"feedback": []})
    rows = []
    try:
        with FEEDBACK_CSV.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["personas"] = (
                    row.get("personas", "").split("|") if row.get("personas") else []
                )
                rows.append(row)
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Failed to read feedback: {exc}"}), 500

    wants_html = request.args.get("format") == "html" or (
        request.accept_mimetypes.accept_html
        and not request.accept_mimetypes.accept_json
    )
    if wants_html:
        return render_template("eval.html", feedback=rows)
    return jsonify({"feedback": rows})


if __name__ == "__main__":
    port_str = os.environ.get("PORT")

    try:
        port = int(port_str)
    except ValueError:
        port = 5000  # or log and exit explicitly

    APP.run(port=port, debug=False, use_reloader=False)
