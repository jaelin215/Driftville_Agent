import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.src.agents import Agent
from app.src.orpda_runner import run_orpda_cycle, build_agent
from app.config.config import USE_DRIFT

# -------------------------
# CONFIG & PATHS
# -------------------------

ROOT = Path.cwd()
DEFAULT_START = datetime(2023, 2, 13, 14, 0)

DRIFTVILLE_PERSONA_PATH = ROOT / "app/src/driftville_personas.json"
SMALLVILLE_PERSONA_PATH = ROOT / "app/src/smallville_personas.json"


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
prefix = "session_orpda" if USE_DRIFT else "session_orpa"

SESSION_LOG_PATH = ROOT / f"app/logs/{prefix}_{timestamp}.log"
MEMORY_STREAM_PATH = ROOT / f"app/logs/memory_streams_{prefix}_{timestamp}.log"


# -------------------------
# LOAD RAW PERSONAS
# -------------------------

try:
    _smallville_persona_data = json.loads(SMALLVILLE_PERSONA_PATH.read_text())
    RAW_PERSONAS = {
        p.get("name"): p.get("raw_persona", "") for p in _smallville_persona_data
    }
except Exception:
    RAW_PERSONAS = {}


# -------------------------
# LOAD AGENT
# -------------------------


def load_agent(agent_name: str, start_time=None):
    try:
        data = json.loads(DRIFTVILLE_PERSONA_PATH.read_text())
    except Exception as e:
        print("Failed to load JSON:", e)
        return None

    for entry in data:
        persona = entry.get("persona", {})
        name = persona.get("name")

        if name != agent_name:
            continue

        schedule = []
        for slot in entry.get("schedule", []):
            schedule.append(
                {
                    "datetime_start": slot.get("datetime_start"),
                    "duration_min": int(slot.get("duration_min", 0)),
                    "location": slot.get("location", "home"),
                    "action": slot.get("action", "idle"),
                    "environment_description": slot.get("environment_description", ""),
                    "notes": slot.get("notes", ""),
                }
            )

        # Determine start time
        if start_time:
            if isinstance(start_time, str):
                start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            else:
                start_dt = start_time
            current_time = start_dt.strftime("%Y-%m-%d %H:%M")
        else:
            current_time = DEFAULT_START.strftime("%Y-%m-%d %H:%M")

        current_location = schedule[0]["location"] if schedule else "unknown"
        current_action = schedule[0]["action"] if schedule else "idle"

        return Agent(
            name=name,
            personality=persona,
            daily_schedule=schedule,
            current_time=current_time,
            current_location=current_location,
            current_action=current_action,
        )

    return None


# -------------------------
# MEMORY STREAM LOGGING
# -------------------------


def log_memory_stream(agent_name: str, summary: str, sim_ts: str):
    MEMORY_STREAM_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts_created": datetime.now().astimezone().isoformat(),
        "sim_time": sim_ts,
        "agent": agent_name,
        "summary": summary,
    }
    with MEMORY_STREAM_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# -------------------------
# SUMMARY BUILDER
# -------------------------


def summarize_orpda(agent_name: str, orpda: dict) -> str:
    obs = orpda.get("observation", {}) or {}
    ref = orpda.get("reflection", {}) or {}
    plan = orpda.get("plan", {}) or {}
    drift = orpda.get("drift_decision", {}) or {}
    action = orpda.get("action_result", {}) or {}

    location = action.get("location") or obs.get("location", "")
    action_name = action.get("action") or obs.get("action", "doing something")
    topic = action.get("topic") or plan.get("topic")
    drift_type = drift.get("drift_type")
    drift_topic = drift.get("drift_topic")
    emotional = ref.get("state_summary", "")
    state_summary = action.get("state_summary") or obs.get("state_summary", "")

    parts = [f"{agent_name} is at {location} doing {action_name}"]

    if topic:
        parts.append(f"about {topic}")

    if drift_type and drift_type != "none":
        if drift_topic:
            parts.append(f"; while drifting ({drift_type}) toward {drift_topic}")
        else:
            parts.append(f"; while drifting ({drift_type})")

    if emotional:
        parts.append(f"; ({emotional})")

    if state_summary:
        parts.append(f"; {state_summary}")

    return " ".join(parts).strip()


# -------------------------
# SINGLE-AGENT SIMULATION LOOP
# -------------------------


async def run_simulation(agent, steps=1):
    print(f"Running single-agent simulation for: {agent.name}")

    MINUTES_PER_STEP = 15
    current_time = datetime.strptime(agent.current_time, "%Y-%m-%d %H:%M")

    last_action_result = None

    # 🔥 NEW: Natural-language working memory
    memory_cache = []

    for tick in range(steps):
        sim_ts = current_time.strftime("%Y-%m-%d %H:%M")
        print(f"\n--- Tick {tick} at {sim_ts} ---")

        ctx = {
            "raw_persona": RAW_PERSONAS.get(agent.name, ""),
            "persona": agent.personality,
            "schedule": agent.daily_schedule,
            "last_action_result": last_action_result,
            "recent_history": memory_cache[-5:],  # ONLY NL summaries
            "current_datetime": sim_ts,
        }

        # Run ORPDA
        orpda_out = await run_orpda_cycle(ctx)

        # Fix nested LLM formatting
        if "action" in orpda_out and isinstance(orpda_out["action"], dict):
            if "action_result" in orpda_out["action"]:
                orpda_out["action_result"] = orpda_out["action"]["action_result"]

        obs = orpda_out.get("observation", {}) or {}
        ref = orpda_out.get("reflection", {}) or {}
        plan = orpda_out.get("plan", {}) or {}
        drift = orpda_out.get("drift_decision", {}) or {}
        action_result = orpda_out.get("action_result", {}) or {}

        # # Ablation toggle
        # if not USE_DRIFT:
        #     drift = {
        #         "should_drift": False,
        #         "drift_type": "none",
        #         "drift_topic": None,
        #         "drift_intensity": 0.0,
        #         "drift_action": "continue",
        #         "justification": "Drift disabled by ablation flag.",
        #     }
        #     orpda_out["drift_decision"] = drift

        # Cleanup next_datetime hallucinations
        for block in (obs, ref, plan, drift, action_result):
            if isinstance(block, dict):
                block.pop("next_datetime", None)

        # Authoritative timestamps
        for block in (obs, plan, drift, action_result):
            if isinstance(block, dict):
                block["datetime_start"] = sim_ts
                block["duration_min"] = MINUTES_PER_STEP

        # Drift propagation
        if "drift_type" in drift:
            action_result["drift_type"] = drift.get("drift_type")
            action_result["drift_topic"] = drift.get("drift_topic")

        # Compute next tick
        action_result["next_datetime"] = (
            current_time + timedelta(minutes=MINUTES_PER_STEP)
        ).strftime("%Y-%m-%d %H:%M")

        last_action_result = action_result

        # Update agent state
        agent.current_action = {
            "sim_datetime": sim_ts,
            "action": action_result.get("action", plan.get("action", "idle")),
            "location": action_result.get("location", plan.get("location", "home")),
            "drift_type": action_result.get("drift_type", drift.get("drift_type")),
            "topic": action_result.get("topic", plan.get("topic")),
        }

        # Memory Stream Summary
        summary = summarize_orpda(agent.name, orpda_out)

        # save to file + memory cache
        log_memory_stream(agent.name, summary, sim_ts)
        memory_cache.append({"sim_time": sim_ts, "summary": summary})

        # Session Log
        with SESSION_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts_created": datetime.now().astimezone().isoformat(),
                        "tick": tick,
                        "sim_time": sim_ts,
                        "agent": agent.name,
                        "use_drift": USE_DRIFT,
                        "orpda": orpda_out,
                    }
                )
                + "\n"
            )

        # Advance simulated time
        await asyncio.sleep(0.5)
        current_time += timedelta(minutes=MINUTES_PER_STEP)


# -------------------------
# ENTRY
# -------------------------
ROOT = Path(__file__).resolve().parent
YAML_DIR = ROOT / "yaml"
# Build root agent (ONLY one used in Option A)
cfg_path = "orpda_sequence.yaml" if USE_DRIFT else "orpa_sequence.yaml"
root_agent = build_agent(YAML_DIR / cfg_path)


if __name__ == "__main__":
    steps = 60  # 60 ticks = 06:00 → 21:00
    print(
        f"USE_DRIFT = {USE_DRIFT}  (ORPDA enabled)"
        if USE_DRIFT
        else f"USE_DRIFT = {USE_DRIFT}  (ORPA baseline mode)"
    )
    print(f"Simulating {steps} timestamps (15‑minute ticks)")

    agent = load_agent("Eddy Lin", start_time="2023-02-13 06:00")
    if not agent:
        raise SystemExit("Failed to load agent.")

    asyncio.run(run_simulation(agent, steps=steps))
