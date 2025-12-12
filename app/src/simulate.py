# app/src/simulate.py
# --------------------------------------
# Author: Jaelin Lee
# Description: ORPDA simulation loop, persona loading, logging, and memory streaming.
# --------------------------------------
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import tools.langfuse_setup as langfuse_setup  # This imports and runs the initialization
from app.config.config import NUM_TICKS, PERSONA_NAME, SIM_START_TIME, USE_DRIFT
from app.src.agents import Agent
from app.src.orpda_runner import build_agent, run_orpda_cycle

# -------------------------
# CONFIG & PATHS
# -------------------------

ROOT = Path.cwd()
DEFAULT_START = datetime(2023, 2, 13, 14, 0)

DRIFTVILLE_PERSONA_PATH = ROOT / "app/src/driftville_personas.json"
SMALLVILLE_PERSONA_PATH = ROOT / "app/src/smallville_personas.json"
DATE_FMT = "%Y-%m-%d %H:%M"


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
    """Load a persona and schedule by name and seed current time/location."""
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
    """Append a natural-language memory summary for the agent at a timestamp."""
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
    """Condense ORPDA block outputs into a single human-readable summary."""
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


def slot_at(schedule, dt: datetime):
    """Return the active schedule slot for a datetime."""
    for slot in schedule:
        try:
            start = datetime.strptime(slot.get("datetime_start"), DATE_FMT)
        except Exception:
            continue
        dur = int(slot.get("duration_min", 0))
        end = start + timedelta(minutes=dur)
        if start <= dt < end:
            return slot, start, end
    return None, None, None


def next_slot(schedule, dt: datetime):
    """Return the next schedule slot starting after dt."""
    future = []
    for slot in schedule:
        try:
            start = datetime.strptime(slot.get("datetime_start"), DATE_FMT)
        except Exception:
            continue
        if start > dt:
            future.append((start, slot))
    if not future:
        return None, None, None
    start, slot = sorted(future, key=lambda x: x[0])[0]
    dur = int(slot.get("duration_min", 0))
    end = start + timedelta(minutes=dur)
    return slot, start, end


# -------------------------
# SINGLE-AGENT SIMULATION LOOP
# -------------------------


async def run_simulation(agent, steps=1):
    """Run the ORPDA loop for a given agent over a number of 15-minute ticks."""
    print(f"Running single-agent simulation for: {agent.name}")

    MINUTES_PER_STEP = 15
    current_time = datetime.strptime(agent.current_time, "%Y-%m-%d %H:%M")

    last_action_result = None

    # 🔥 NEW: Natural-language working memory
    memory_cache = []

    for tick in range(steps):
        sim_ts = current_time.strftime("%Y-%m-%d %H:%M")
        print(f"\n--- Tick {tick} at {sim_ts} ---")

        cur_slot, cur_start, cur_end = slot_at(agent.daily_schedule, current_time)
        nxt_slot, nxt_start, nxt_end = next_slot(agent.daily_schedule, current_time)

        ctx = {
            # Minimal context for observer: persona + time + last 5 memories + last action state + nearby schedule slots
            "persona": agent.personality,
            "current_datetime": sim_ts,
            "recent_history": memory_cache[-5:],  # last 5 memory stream summaries
            "last_action_result": last_action_result,
            "current_slot": cur_slot,
            "next_slot": nxt_slot,
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

        # Cleanup next_datetime hallucinations
        for block in (obs, ref, plan, drift, action_result):
            if isinstance(block, dict):
                block.pop("next_datetime", None)

        # Normalize drift when it is effectively off
        should_drift = bool(drift.get("should_drift"))
        intensity = float(drift.get("drift_intensity") or 0)
        if (not should_drift) or intensity <= 0:
            drift["should_drift"] = False
            drift["drift_type"] = "none"
            drift["drift_topic"] = ""
            drift["drift_intensity"] = 0
            drift["drift_action"] = drift.get("drift_action") or "continue"
            drift["potential_recovery"] = ""
            drift["justification"] = ""
            action_result["drift_type"] = "none"
            action_result.pop("drift_topic", None)

        # Authoritative timestamps
        for block in (obs, plan, drift, action_result):
            if isinstance(block, dict):
                block["datetime_start"] = sim_ts
                block["duration_min"] = MINUTES_PER_STEP

        # Drift propagation
        if "drift_type" in drift:
            action_result["drift_type"] = drift.get("drift_type")
            action_result["drift_topic"] = drift.get("drift_topic")

        # On first tick (no prior action), force alignment to current schedule slot
        if last_action_result is None and cur_slot:
            slot = cur_slot
            slot_topic = slot.get("notes") or slot.get("action")
            for block in (obs, plan, action_result):
                if isinstance(block, dict):
                    block["location"] = slot.get("location", block.get("location"))
                    block["action"] = slot.get("action", block.get("action"))
                    block["topic"] = slot_topic or block.get("topic")

        # Align to schedule unless we are already drifting
        drift_type = drift.get("drift_type", "none")
        slot, slot_start, slot_end = cur_slot, cur_start, cur_end
        if slot and drift_type in ("none", None, "internal", "attentional_leak"):
            # stay in-slot until its end; do not advance early
            if current_time < slot_end:
                action_result["location"] = slot.get(
                    "location", action_result.get("location")
                )
                action_result["action"] = slot.get(
                    "action", action_result.get("action")
                )
                action_result["topic"] = (
                    slot.get("notes")
                    or slot.get("action")
                    or action_result.get("topic")
                )
                plan["location"] = action_result["location"]
                plan["action"] = action_result["action"]
                plan["topic"] = action_result["topic"]
        # If no slot was found, keep LLM outputs as-is

        # Ensure non-behavioral drift keeps the planned location/action
        if drift_type in ("none", "internal", "attentional_leak"):
            if plan.get("location"):
                action_result["location"] = plan["location"]
            if plan.get("action"):
                action_result["action"] = plan["action"]
            if plan.get("topic"):
                action_result.setdefault("topic", plan["topic"])
        if drift.get("drift_type") == "none":
            action_result["state_summary"] = (
                plan.get("state_summary")
                or obs.get("state_summary")
                or action_result.get("state_summary", "")
            )

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
    steps = NUM_TICKS  # 60 ticks = 06:00 → 21:00
    print(
        f"USE_DRIFT = {USE_DRIFT}  (ORPDA enabled)"
        if USE_DRIFT
        else f"USE_DRIFT = {USE_DRIFT}  (ORPA baseline mode)"
    )
    print(f"Simulating {steps} timestamps (15‑minute ticks)")

    agent = load_agent(PERSONA_NAME, start_time=SIM_START_TIME)
    if not agent:
        raise SystemExit("Failed to load agent.")

    asyncio.run(run_simulation(agent, steps=steps))
