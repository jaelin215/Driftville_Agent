# simulate.py
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import json as _json
import argparse
import sys
import uuid
import time

from app.src.agents import Agent
from app.src.conversation_manager import ConversationManager, with_backoff
from app.src.orpda_runner import run_orpda_cycle
from app.config.config import MODEL_NAME


ROOT = Path.cwd()
OBSERVATION_PATH = ROOT / "app/logs/observations.json"
TRACE_LOG_PATH = ROOT / "app/logs/trace.log"
MEMORY_STREAM_PATH = ROOT / "app/logs/memory_streams.log"
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
SESSION_LOG_PATH = ROOT / f"app/logs/session_{stamp}.log"
EVENTS_LOG_PATH = ROOT / "app/logs/events.log"
SMALLVILLE_PERSONA_PATH = ROOT / "app/src/smallville_personas.json"  # raw bios
DRIFTVILLE_PERSONA_PATH = (
    ROOT / "app/src/driftville_personas.json"
)  # structured schedule+persona

# Load raw persona blurbs for persona_injector
try:
    _smallville_persona_data = _json.loads(SMALLVILLE_PERSONA_PATH.read_text())
    RAW_PERSONAS = {
        p.get("name"): p.get("raw_persona", "") for p in _smallville_persona_data
    }
except Exception:
    RAW_PERSONAS = {}


def _minutes_from_dt(dt_str: str) -> int:
    try:
        parts = dt_str.split(" ")
        hm = parts[1]
        h, m = hm.split(":")[:2]
        return int(h) * 60 + int(m)
    except Exception:
        return 0


def load_agents():
    """Create Agent instances from driftville_personas.json."""
    agents = {}
    try:
        data = json.loads(DRIFTVILLE_PERSONA_PATH.read_text())
    except Exception:
        return agents

    for entry in data:
        p = entry.get("persona", {})
        name = p.get("name", "Unknown")
        sched = []
        for slot in entry.get("schedule", []):
            start_min = _minutes_from_dt(slot.get("datetime_start", "00:00"))
            dur = int(slot.get("duration_min", 0))
            sched.append(
                {
                    "action": slot.get("action", "idle"),
                    "start_time": start_min,
                    "end_time": start_min + dur,
                    "location": slot.get("location", "home"),
                }
            )
        agent = Agent(
            name=name,
            personality={"raw_persona": RAW_PERSONAS.get(name, "")},
            daily_schedule=sched,
        )
        agents[name] = agent
    return agents


AGENTS = load_agents()
ACTIVE_AGENTS = AGENTS


class TeeStdout:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.filepath.open("a", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)

    def flush(self):
        self.stdout.flush()
        self.file.flush()


def _summarize_entry(agent: str, entry_type: str, payload: dict) -> str:
    """Create a short natural-language summary from known payload fields."""
    if not isinstance(payload, dict):
        return str(payload)
    p = {}
    # unwrap if wrapped
    if entry_type in payload:
        p = payload.get(entry_type) or {}
    else:
        p = payload

    if entry_type == "observation":
        act = p.get("action") or ""
        loc = p.get("location") or ""
        dt = p.get("datetime_start") or ""
        summary = p.get("state_summary") or ""
        return f"{agent} observed: {act} at {loc} starting {dt}. {summary}".strip()
    if entry_type == "reflection":
        state = p.get("state_summary") or ""
        reason = p.get("reasoning") or ""
        return f"{agent} reflection: {state} {reason}".strip()
    if entry_type == "plan":
        act = p.get("action") or ""
        loc = p.get("location") or ""
        dt = p.get("datetime_start") or ""
        dur = p.get("duration_min")
        topic = p.get("topic") or ""
        summary = p.get("state_summary") or ""
        return f"{agent} plans {act} at {loc} from {dt} for {dur} min. {topic} {summary}".strip()
    if entry_type == "drift_decision":
        drift_type = p.get("drift_type") or ""
        drift_topic = p.get("drift_topic") or ""
        drift_act = p.get("drift_action") or ""
        just = p.get("justification") or ""
        return f"{agent} drift decision: {drift_type} {drift_topic} {drift_act}. {just}".strip()
    if entry_type == "action_result":
        act = p.get("action") or ""
        loc = p.get("location") or ""
        dt = p.get("datetime_start") or ""
        nxt = p.get("next_datetime") or ""
        drift_type = p.get("drift_type") or ""
        topic = p.get("topic") or ""
        summary = p.get("state_summary") or ""
        return f"{agent} {act} at {loc} from {dt} to {nxt}. Drift:{drift_type} Topic:{topic}. {summary}".strip()
    return str(payload)


def _write_state_snapshot(sim_time):
    """Disabled: no observation snapshot logging."""
    return


def _log_memory_stream(
    agent_name: str,
    action_result: dict,
    tick_idx: int,
    sim_ts: str,
    entry_type: str = "action_result",
    real_ts: str | None = None,
):
    try:
        MEMORY_STREAM_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts_created": real_ts or sim_ts,
            "ts_last_accessed": real_ts or sim_ts,
            "agent": agent_name,
            "tick": tick_idx,
            "type": entry_type,
            "payload": action_result,
        }
        with MEMORY_STREAM_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def _log_trace(entry: dict):
    """Disabled: no trace logging."""
    return


def _log_event(
    agent_name: str, step_type: str, payload: dict, tick_idx: int, sim_ts: str
):
    """Disabled: no events logging."""
    return


DEFAULT_START = datetime(2023, 2, 13, 14, 0)


async def run_simulation(num_days=1, start_time: datetime | None = None):
    """Run ORPDA simulation; conversation only when two agents present."""

    agent_names = list(ACTIVE_AGENTS.keys())
    if len(agent_names) == 0:
        raise SystemExit("No agents loaded from driftville_personas.json")
    cm = None
    if len(agent_names) >= 2:
        cm = ConversationManager(
            ACTIVE_AGENTS[agent_names[0]], ACTIVE_AGENTS[agent_names[1]]
        )

    MINUTES_PER_STEP = 15  # Drift loop runs per 15 minutes
    MAX_TURNS = 2
    START_TIME = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    MAX_STEPS = 1  # only simulate one time step for quick test

    agent_states = {
        name: {"last_action_result": None, "history": []} for name in ACTIVE_AGENTS
    }
    current_time = start_time or DEFAULT_START

    for day in range(num_days):
        print(f"\n=== DAY {day + 1} ===\n")

        step_count = 0
        while step_count < MAX_STEPS:
            sim_minutes = current_time.hour * 60 + current_time.minute
            _write_state_snapshot(sim_minutes)
            print(f"Time: {current_time.strftime('%H:%M')}")

            # Run ORPDA loop for each agent to update their current_action (+drift fields)
            for agent in ACTIVE_AGENTS.values():
                ctx = {
                    "raw_persona": RAW_PERSONAS.get(agent.name, ""),
                    "persona": agent.personality,
                    "schedule": agent.daily_schedule,
                    "last_action_result": agent_states[agent.name][
                        "last_action_result"
                    ],
                    "recent_history": agent_states[agent.name]["history"][-5:],
                    "current_datetime": current_time.strftime("%Y-%m-%d %H:%M"),
                }
                orpda_out = await run_orpda_cycle(ctx)
                observation = orpda_out.get("observation") or {}
                action_result = orpda_out.get("action_result") or {}
                drift_decision = orpda_out.get("drift_decision") or {}
                plan = orpda_out.get("plan") or {}
                reflection = orpda_out.get("reflection") or {}

                # Clamp datetime and duration to the current tick to enforce chronological steps
                tick_start = current_time.strftime("%Y-%m-%d %H:%M")
                loop_entry = {
                    "sim_datetime": tick_start,  # e.g., "2023-02-13 14:00"
                    "tick_idx": step_count,
                    "agent": agent.name,
                    "observation": observation or {},
                    "reflection": reflection or {},
                    "plan": plan or {},
                    "drift_decision": drift_decision or {},
                    "action_result": action_result or {},
                }
                with SESSION_LOG_PATH.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(loop_entry) + "\n")

                action_result["datetime_start"] = tick_start
                plan["datetime_start"] = tick_start
                action_result["duration_min"] = MINUTES_PER_STEP
                plan["duration_min"] = MINUTES_PER_STEP
                # Also set next_datetime to the tick end for clarity
                action_result["next_datetime"] = (
                    current_time + timedelta(minutes=MINUTES_PER_STEP)
                ).strftime("%Y-%m-%d %H:%M")

                agent_states[agent.name]["last_action_result"] = action_result
                agent_states[agent.name]["history"].append(
                    {
                        "observation": orpda_out.get("observation"),
                        "reflection": reflection,
                        "plan": plan,
                        "drift_decision": drift_decision,
                        "action_result": action_result,
                    }
                )

                agent.current_action = {
                    "action": action_result.get("action", plan.get("action", "idle")),
                    "location": action_result.get(
                        "location", plan.get("location", "home")
                    ),
                    "drift_type": action_result.get(
                        "drift_type", drift_decision.get("drift_type", "none")
                    ),
                    "topic": action_result.get("topic") or plan.get("topic"),
                    "drift_intensity": drift_decision.get("drift_intensity"),
                    "sim_datetime": action_result.get(
                        "datetime_start", ctx["current_datetime"]
                    ),
                }
                real_ts = datetime.utcnow().isoformat() + "Z"
                # Log all ORPDA steps into memory/events with wrapped payloads
                obs_payload = {"observation": orpda_out.get("observation") or {}}
                refl_payload = {"reflection": reflection or {}}
                plan_payload = {"plan": plan or {}}
                drift_payload = {"drift_decision": drift_decision or {}}
                action_payload = {"action_result": action_result or {}}

                _log_memory_stream(
                    agent.name,
                    obs_payload,
                    step_count,
                    tick_start,
                    entry_type="observation",
                    real_ts=real_ts,
                )
                _log_event(
                    agent.name,
                    "observation",
                    obs_payload,
                    step_count,
                    tick_start,
                )
                _log_memory_stream(
                    agent.name,
                    refl_payload,
                    step_count,
                    tick_start,
                    entry_type="reflection",
                    real_ts=real_ts,
                )
                _log_event(
                    agent.name, "reflection", refl_payload, step_count, tick_start
                )
                _log_memory_stream(
                    agent.name,
                    plan_payload,
                    step_count,
                    tick_start,
                    entry_type="plan",
                    real_ts=real_ts,
                )
                _log_event(agent.name, "plan", plan_payload, step_count, tick_start)
                _log_memory_stream(
                    agent.name,
                    drift_payload,
                    step_count,
                    tick_start,
                    entry_type="drift_decision",
                    real_ts=real_ts,
                )
                _log_event(
                    agent.name, "drift_decision", drift_payload, step_count, tick_start
                )
                _log_memory_stream(
                    agent.name,
                    action_payload,
                    step_count,
                    tick_start,
                    entry_type="action_result",
                    real_ts=real_ts,
                )
                _log_event(
                    agent.name, "action_result", action_payload, step_count, tick_start
                )

            should_talk = False
            dialogue = []
            if cm:
                # Check if conversation should happen
                should_talk, context, a, b = cm.should_start_conversation(sim_minutes)
                if should_talk:
                    print(f"  → Conversation triggered: {context}")

                    speaker, listener = a, b
                    for _ in range(MAX_TURNS):
                        if not await cm.wants_to_speak(
                            speaker, listener, context, dialogue
                        ):
                            break
                        line = await with_backoff(
                            cm.generate_turn, speaker, listener, context, dialogue
                        )
                        if not line:
                            break
                        dialogue.append(line)
                        speaker, listener = listener, speaker

                    for line in dialogue:
                        print(f"  {line['speaker']}: {line['text']}")

                    await cm.store_turns(dialogue, context)
                    print()

            trace_entry = {
                "ts_real": datetime.now().isoformat() + "Z",
                "tick_time": current_time.strftime("%Y-%m-%d %H:%M"),
                "tick_idx": step_count,
                "agents": [
                    {
                        "name": name,
                        "action": ACTIVE_AGENTS[name].current_action,
                        "reflection": agent_states[name]["history"][-1].get(
                            "reflection", {}
                        ),
                    }
                    for name in ACTIVE_AGENTS
                ],
                "dialogue": dialogue if should_talk else [],
            }
            _log_trace(trace_entry)

            # Small delay to avoid rate limits and advance time
            await asyncio.sleep(1)
            current_time += timedelta(minutes=MINUTES_PER_STEP)
            _write_state_snapshot(current_time.hour * 60 + current_time.minute)
            step_count += 1


if __name__ == "__main__":
    # Tee stdout to session.log
    tee = TeeStdout(SESSION_LOG_PATH)
    sys.stdout = tee

    parser = argparse.ArgumentParser(
        description="Run ORPDA simulation for selected agents."
    )
    parser.add_argument(
        "--agents",
        type=str,
        help="Comma-separated agent names to simulate (default: first two in driftville_personas.json)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Number of ticks to simulate (default: 1)",
    )
    parser.add_argument(
        "--sim-start",
        type=str,
        help="Simulation start datetime (YYYY-MM-DD HH:MM). Defaults to now rounded to minute.",
    )
    args = parser.parse_args()

    if args.agents:
        wanted = [a.strip() for a in args.agents.split(",") if a.strip()]
        filtered = {k: v for k, v in AGENTS.items() if k in wanted}
        if not filtered:
            raise SystemExit(f"No matching agents found for: {wanted}")
        ACTIVE_AGENTS = filtered
    MAX_STEPS = args.steps
    start_dt = None
    if args.sim_start:
        try:
            start_dt = datetime.strptime(args.sim_start, "%Y-%m-%d %H:%M")
        except Exception:
            raise SystemExit("Invalid --sim-start format. Use YYYY-MM-DD HH:MM")
    if start_dt is None:
        start_dt = DEFAULT_START
    asyncio.run(run_simulation(num_days=1, start_time=start_dt))
