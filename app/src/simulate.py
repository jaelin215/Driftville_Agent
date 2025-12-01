# simulate.py
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import json as _json

from google.adk.models.google_llm import _ResourceExhaustedError
from google.genai.errors import ClientError

from .agents import jaelin, maxime, sam, lily, AGENTS
from .conversation_manager import ConversationManager, with_backoff
from .orpda_runner import run_orpda_cycle


ROOT = Path.cwd()
STATE_SNAPSHOT_PATH = ROOT / "app/logs/state_snapshot.json"
SMALLVILLE_PERSONA_PATH = ROOT / "app/src/smallville_personas.json"

# Load raw persona blurbs for persona_injector
try:
    _smallville_persona_data = _json.loads(SMALLVILLE_PERSONA_PATH.read_text())
    RAW_PERSONAS = {
        p.get("name"): p.get("raw_persona", "") for p in _smallville_persona_data
    }
except Exception:
    RAW_PERSONAS = {}


def _write_state_snapshot(sim_time):
    """Persist latest sim-time positions for visualization."""
    try:
        STATE_SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = []
        for agent in AGENTS.values():
            action = agent.get_current_action(sim_time)
            payload.append(
                {
                    "name": agent.name,
                    "action": (action or {}).get("action", "idle"),
                    "location": (action or {}).get("location", "home"),
                    "drift_type": (action or {}).get("drift_type", "none"),
                    "drift_intensity": (action or {}).get("drift_intensity"),
                    "topic": (action or {}).get("topic"),
                }
            )
        STATE_SNAPSHOT_PATH.write_text(
            json.dumps({"sim_minutes": sim_time, "agents": payload}), encoding="utf-8"
        )
    except Exception:
        return


async def run_simulation(num_days=1):
    """Run 2-agent simulation with ORPDA (D = Drift)."""

    cm = ConversationManager(jaelin, maxime)

    MINUTES_PER_STEP = 15  # Drift loop runs per 15 minutes
    MAX_TURNS = 2
    START_TIME = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    MAX_STEPS = 2  # only simulate two time steps (two datetimes)

    agent_states = {
        name: {"last_action_result": None, "history": []} for name in AGENTS
    }
    current_time = START_TIME

    for day in range(num_days):
        print(f"\n=== DAY {day + 1} ===\n")

        step_count = 0
        while step_count < MAX_STEPS:
            sim_minutes = current_time.hour * 60 + current_time.minute
            _write_state_snapshot(sim_minutes)
            print(f"Time: {current_time.strftime('%H:%M')}")

            # Run ORPDA loop for each agent to update their current_action (+drift fields)
            for agent in AGENTS.values():
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
                action_result = orpda_out.get("action_result") or {}
                drift_decision = orpda_out.get("drift_decision") or {}
                plan = orpda_out.get("plan") or {}
                reflection = orpda_out.get("reflection") or {}

                # Clamp datetime and duration to the current tick to enforce chronological steps
                tick_start = current_time.strftime("%Y-%m-%d %H:%M")
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

            # Check if conversation should happen
            should_talk, context, a, b = cm.should_start_conversation(sim_minutes)
            if should_talk:
                print(f"  → Conversation triggered: {context}")

                dialogue = []
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

            # Small delay to avoid rate limits and advance time
            await asyncio.sleep(1)
            current_time += timedelta(minutes=MINUTES_PER_STEP)
            _write_state_snapshot(current_time.hour * 60 + current_time.minute)
            step_count += 1


if __name__ == "__main__":
    asyncio.run(run_simulation(num_days=1))
