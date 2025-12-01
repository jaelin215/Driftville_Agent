# app/src/agents.py
# only data structures and loading.
# Keep Agent, load_agents(), and the methods that mutate/query the agent instance
# (e.g., get_current_action, load_memories, load_reflections).
# No LLM or logging code here.

import json
from pathlib import Path
import datetime

ROOT = Path.cwd()
AGENT_PERSONAS_PATH = ROOT / "app/src/agent_personas.json"
MEMORY_PATH = ROOT / "app/logs/memory.jsonl"
REFLECTION_PATH = ROOT / "app/logs/reflection.jsonl"


# --------------------------------*
# Define agent
# --------------------------------*
class Agent:
    def __init__(
        self,
        name,
        personality,
        daily_schedule,
        current_time=None,
        current_location=None,
        current_action=None,
        current_environment=None,
        current_notes=None,
    ):
        self.name = name
        self.personality = personality
        self.daily_schedule = daily_schedule
        self.memory = []
        # Default to "now" and home if not provided (e.g., when loading static personas)
        self.current_time = current_time or datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
        self.current_action = current_action or "idle"
        self.location = current_location or "home"
        self.reflection = []
        self.current_environment = current_environment or "quiet"
        self.current_notes = current_notes or ""

    def load_memory(self, memory_path=MEMORY_PATH):
        """Load memories for this agent from a JSONL file."""
        self.memory = []
        if not memory_path.exists():
            return
        with memory_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if self.name in obj.get("participants"):
                        self.memory.append(obj)
                except Exception:
                    continue

    def load_reflections(self, reflection_path=REFLECTION_PATH):
        """Load memories for this agent from a JSONL file."""
        self.reflection = []
        if not reflection_path.exists():
            return
        with reflection_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get("author") == self.name:
                        self.reflection.append(obj)
                except Exception:
                    continue

    def get_current_action(self, sim_time):
        """Return what agent should be doing at this time"""
        # If current_action was set by ORPDA loop, prefer it.
        if self.current_action:
            return self.current_action
        for action in self.daily_schedule:
            if action["start_time"] <= sim_time < action["end_time"]:
                return action
        return None


# --------------------------------*
# Utils to load agents
# --------------------------------*
def load_agents(agent_personas_path=AGENT_PERSONAS_PATH):
    with agent_personas_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    agents = {}
    for item in data:
        agent = Agent(
            name=item["name"],
            personality=item.get("personality", {}),
            daily_schedule=item.get("schedule", []),
        )
        agent.load_memory()  # populate from memory.jsonl
        agents[agent.name] = agent

    return agents


# --------------------------------*
# Initialize agents
# --------------------------------*
AGENTS = load_agents()
jaelin = AGENTS.get("Jaelin")
maxime = AGENTS.get("Max")
derby = AGENTS.get("Derby")
sam = AGENTS.get("Sam")
lily = AGENTS.get("Lily")
try:
    print(jaelin.name)
    print(jaelin.memory)
except Exception:
    print(Exception)
