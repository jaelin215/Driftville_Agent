# simulate.py
import asyncio
import json
from pathlib import Path

from agents import jaelin, maxime, sam, lily, AGENTS
from conversation_manager import ConversationManager, with_backoff
from google.adk.models.google_llm import _ResourceExhaustedError
from google.genai.errors import ClientError

ROOT = Path.cwd()
STATE_SNAPSHOT_PATH = ROOT / "app/logs/state_snapshot.json"


async def run_simulation(num_days=1):
    """Run minimal 2-agent simulation"""

    cm = ConversationManager(jaelin, maxime)

    # Time in minutes
    MINUTES_PER_STEP = 30  # Each step = 30 min
    START_MIN = 7 * 60  # 07:00
    END_MIN = 11 * 60  # 11:00 (exclusive)
    MAX_TURNS = 8

    for day in range(num_days):
        print(f"\n=== DAY {day + 1} ===\n")

        sim_time = START_MIN
        while sim_time < END_MIN:
            _write_state_snapshot(sim_time)
            hour = sim_time // 60
            minute = sim_time % 60

            print(f"Time: {hour:02d}:{minute:02d}")

            # Check if conversation should happen
            should_talk, context, a, b = cm.should_start_conversation(sim_time)
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
            sim_time += MINUTES_PER_STEP
            _write_state_snapshot(sim_time)


if __name__ == "__main__":
    asyncio.run(run_simulation(num_days=1))


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
                }
            )
        STATE_SNAPSHOT_PATH.write_text(
            json.dumps({"sim_minutes": sim_time, "agents": payload}), encoding="utf-8"
        )
    except Exception:
        return
