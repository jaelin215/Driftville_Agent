# app/src/agents.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Lightweight Agent class representing persona state and memory.
# --------------------------------------

import json
from pathlib import Path
import datetime

ROOT = Path.cwd()


# --------------------------------*
# Define agent
# --------------------------------*
class Agent:
    """Container for persona state, schedule, and short-term memory."""

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
        """Initialize an agent with persona details and the current context."""
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
