# app/src/orpda_runner.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Builds the YAML-defined agent graph and runs a single ORPDA cycle.
# --------------------------------------
"""
orpda_runner.py — cleaned (Option A)
Minimal ORPDA engine:
- Loads root_agent from YAML
- Runs ORPDA loop via InMemoryRunner
- Extracts structured JSON from model output
"""

import json
from pathlib import Path
import yaml
from google.adk.agents import (
    LlmAgent,
    SequentialAgent,
    ParallelAgent,
    LoopAgent,
)
from google.adk.runners import InMemoryRunner
from google.adk.models.google_llm import Gemini
from dotenv import load_dotenv

import sys

# -------------------------
# Load environment & paths
# -------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config.config import MODEL_NAME, USE_DRIFT
# from app.src.observe_non_llm_agent import deterministic_observe

load_dotenv()

ROOT = Path(__file__).resolve().parent
YAML_DIR = ROOT / "yaml"


# -------------------------
# YAML → ADK Agent Builder
# -------------------------
def build_agent(cfg_path: Path):
    """Recursively construct ADK agents from YAML configs."""
    cfg_text = cfg_path.read_text().strip()
    if not cfg_text:
        raise ValueError(f"YAML config is empty: {cfg_path}")

    cfg = yaml.safe_load(cfg_text)
    if not isinstance(cfg, dict):
        raise ValueError(
            f"Malformed YAML in {cfg_path}: must load into a dict, got {type(cfg)}"
        )

    sub_agents = []
    for s in cfg.get("sub_agents", []):
        sub_cfg_path = (cfg_path.parent / s["config_path"]).resolve()
        sub_agents.append(build_agent(sub_cfg_path))

    cls = cfg.get("agent_class", "LlmAgent")

    if cls == "SequentialAgent":
        return SequentialAgent(name=cfg["name"], sub_agents=sub_agents)

    if cls == "ParallelAgent":
        return ParallelAgent(name=cfg["name"], sub_agents=sub_agents)

    if cls == "LoopAgent":
        return LoopAgent(
            name=cfg["name"],
            sub_agents=sub_agents,
            max_iterations=cfg.get("max_iterations", 15),  # avoid runaway loops
        )

    # Default: LlmAgent
    llm = LlmAgent(
        name=cfg["name"],
        model=Gemini(model=MODEL_NAME),
        instruction=cfg.get("instruction", ""),
        tools=[],
    )

    # If sub-agents exist, wrap in sequential
    return (
        SequentialAgent(name=f"{cfg['name']}_seq", sub_agents=[llm] + sub_agents)
        if sub_agents
        else llm
    )


def build_observation(ctx: dict) -> dict:
    """
    Deterministic, non-LLM observer.

    Uses:
      - persona
      - current_slot
      - last_action_result

    to produce a single `observation` block that downstream LLM agents consume.
    """
    persona = ctx.get("persona", {})
    name = persona.get("name", "The person")

    current_slot = ctx.get("current_slot", {})
    last = ctx.get("last_action_result")

    # 1) Decide time / action / location: follow your old Observer rules
    if last:
        # continue from last.next_datetime and reuse its action/location
        datetime_start = last.get("next_datetime", current_slot.get("datetime_start"))
        location = last.get("location", current_slot.get("location"))
        action = last.get("action", current_slot.get("action"))
    else:
        # first tick: copy from current_slot
        datetime_start = current_slot.get("datetime_start")
        location = current_slot.get("location")
        action = current_slot.get("action")

    # 2) Duration: default to 15 min, capped by current_slot
    slot_duration = current_slot.get("duration_min", 15) or 15
    duration_min = min(slot_duration, 15)

    # 3) Simple factual summary (you can refine later)
    state_summary = f"{name} is at {location} doing {action}."
    state_summary = state_summary[:160]  # keep it short

    return {
        "observation": {
            "datetime_start": datetime_start,
            "duration_min": duration_min,
            "location": location,
            "action": action,
            "state_summary": state_summary,
        }
    }


# -------------------------
# Extract JSON in ```json blocks
# -------------------------
def extract_json_from_markdown(text: str):
    """Strip markdown fences to recover JSON payloads."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        return "\n".join(lines[1:-1]).strip()
    return text


# Build root agent (ONLY one used in Option A)
cfg_path = "orpda_sequence.yaml" if USE_DRIFT else "orpa_sequence.yaml"
root_agent = build_agent(YAML_DIR / cfg_path)


# -------------------------
# Run ORPDA cycle
# -------------------------
async def run_orpda_cycle(context: dict) -> dict:
    """
    Execute one ORPDA/ORPA pass and merge structured outputs from sub-agents.
    Now:
      - Observation is computed symbolically in Python (non-LLM).
      - LLM agents only handle reflection/plan/drift/action.
    """
    # 1) Build deterministic observation
    obs_block = build_observation(context)

    # 2) Inject into context so Reflector/Planner see it
    ctx_with_obs = {**context, **obs_block}

    prompt = json.dumps(ctx_with_obs, ensure_ascii=False)

    async with InMemoryRunner(agent=root_agent) as runner:
        events = await runner.run_debug(prompt, verbose=False)

    # 3) Seed merged with the symbolic observation
    merged = {
        "observation": obs_block["observation"],
        "reflection": None,
        "plan": None,
        "drift_decision": None,
        "action_result": None,
    }

    for ev in events:
        parts = getattr(ev.content, "parts", None)
        if not parts:
            continue

        for part in parts:
            raw = getattr(part, "text", None)
            if not raw:
                continue

            cleaned = extract_json_from_markdown(raw)

            try:
                data = json.loads(cleaned)
            except Exception:
                continue

            # merge only known ORPDA keys (observation already set)
            for key in ("reflection", "plan", "drift_decision", "action_result"):
                if key in data:
                    merged[key] = data[key]

    # Remove None keys
    return {k: v for k, v in merged.items() if v is not None}


# -------------------------
# END
# -------------------------

if __name__ == "__main__":
    print("orpda_runner loaded (clean mode).")
    run_orpda_cycle("hello")
