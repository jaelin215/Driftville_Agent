# conversation_manager.py
# orchestration only:
# imports LLM helpers from brain (plus a local import brain for module resolution),
# restores importance scoring in store_turns, and uses the imported load_history in its __main__ test.
# The per-turn dedupe, wants-to-speak, and turn generation still delegate to the shared utilities.

# -----------------------------------------*
# Step 2: Simple Conversation Trigger
# -----------------------------------------*
import json
import asyncio
import random
from datetime import datetime
from pathlib import Path

from gemini_api import call_gemini
from google.adk.runners import InMemoryRunner
from google.adk.models.google_llm import _ResourceExhaustedError
from google.genai.errors import ClientError

import brain
from brain import (
    importance_agent,
    run_and_log,
    safe_generate,
    generate_turn_line,
    load_history,
    summarize_dialogue,
)


ROOT = Path.cwd()
EVENT_LOG_PATH = ROOT / "app/logs/event_logs.jsonl"


async def with_backoff(coro_fn, *args, **kwargs):
    try:
        return await coro_fn(*args, **kwargs)
    except (_ResourceExhaustedError, ClientError):
        await asyncio.sleep(60)
        try:
            return await coro_fn(*args, **kwargs)
        except Exception:
            return None


class ConversationManager:
    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2
        self._seen = set()
        self.history = []

    # OK

    @staticmethod
    async def wants_to_speak(speaker, listener, context, history):
        recent = getattr(speaker, "memory", None) or []
        prompt = f"""You are {speaker.name}. Your personality is {speaker.personality}. Context: {context}.
Recent memories: {recent[-3:] if recent else "None"}
Do you want to speak now? Reply with yes/no only."""
        resp = await safe_generate(call_gemini, prompt)
        return resp and resp.strip().lower().startswith("y")

    async def generate_turn(self, speaker, listener, context, history):
        """Delegate turn generation to brain.generate_turn_line."""
        return await generate_turn_line(speaker, listener, context, history)

    async def store_turns(self, dialogue, context):
        """Store one conversation event with all turns and a single timestamp."""
        if not dialogue:
            return
        # dedupe on full dialogue
        key = (context, tuple((t.get("speaker"), t.get("text")) for t in dialogue))
        if key in self._seen:
            return
        self._seen.add(key)

        timestamp = datetime.now().isoformat()
        author = dialogue[0].get("speaker") if dialogue else None
        listener = dialogue[0].get("listener") if dialogue else None

        convo_text = " ".join((t.get("text") or "").strip() for t in dialogue).strip()
        summary_text = (await summarize_dialogue(convo_text)) or convo_text
        memory_text = (
            f"{self.agent1.name} had a conversation with "
            f"{self.agent2.name} about {summary_text}"
            if summary_text
            else ""
        )
        score = None
        if memory_text:
            async with InMemoryRunner(agent=importance_agent) as runner:
                res = await with_backoff(
                    run_and_log,
                    author,
                    [self.agent1.name, self.agent2.name],
                    memory_text,
                    runner,
                    summary_override=summary_text,
                )
                score = res[1] if res else None

        event_log = {
            "timestamp": timestamp,
            "type": "conversation",
            "context": context,
            "participants": [self.agent1.name, self.agent2.name],
            "dialogue": dialogue,
            "importance": score,
        }
        # append to in-memory agent logs if available
        for agent in [self.agent1, self.agent2]:
            if getattr(agent, "memory", None) is not None:
                agent.memory.append(event_log)
        with EVENT_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event_log) + "\n")

    def should_start_conversation(self, sim_time):
        """Check if agents should talk based on schedule and intention.

        initiation is a deliberate choice per agent (based on memory/context),
        and dialog ends when either side declines to continue. Skeleton:
        """
        action1 = self.agent1.get_current_action(sim_time)
        action2 = self.agent2.get_current_action(sim_time)
        print(action1)
        print(action2)

        # Same location + specific triggers
        if action1 and action2:
            if action1["location"] == action2["location"]:
                from_agent, to_agent = random.choice(
                    [(self.agent1, self.agent2), (self.agent2, self.agent1)]
                )
                return True, action1["action"], from_agent, to_agent

        return False, None, None, None


if __name__ == "__main__":

    async def _test():
        history = load_history(["Sam", "Lily"])
        print(f"Found {len(history)} conversations between Sam and Lily")
        for ev in history:
            ts = ev.get("timestamp", "")
            ctx = ev.get("context", "")
            turns = ev.get("dialogue", [])
            print(f"- {ts} [{ctx}]")
            for t in turns:
                print(f"  {t.get('speaker')}: {t.get('text')}")

    asyncio.run(_test())
