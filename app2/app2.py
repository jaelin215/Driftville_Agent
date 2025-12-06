# app2/app2.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Flask-based UI preview for Driftville personas and schedule viewer.
# --------------------------------------

from flask import Flask, render_template, request, jsonify
import json
from pathlib import Path

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


def load_session_data():
    """Load ORPDA session logs (session_orpda_*.log JSONL) and group entries by agent."""
    if not SESSION_LOGS_DIR.exists():
        return {}
    files = sorted(
        SESSION_LOGS_DIR.glob("session_orpda_*.log"),
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
    return render_template(
        "index.html",
        personas=PERSONAS,
        emoji_map=EMOJI_MAP,
        face_map=FACE_MAP,
        session_data=load_session_data(),
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
    b = (payload or {}).get("agent2")
    if not a or not b or a == b:
        return jsonify(
            {"error": "Provide two different agent names as agent1/agent2"}
        ), 400

    # Stubbed response; replace with your real simulation
    dialogue = [
        {"speaker": a, "text": f"Hey {b}, want to chat about Driftville?"},
        {"speaker": b, "text": f"Sure, {a}! Let's see what's happening in town."},
    ]
    return jsonify({"status": "ok", "agents": [a, b], "dialogue": dialogue})


if __name__ == "__main__":
    APP.run(debug=True)
