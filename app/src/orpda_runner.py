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
    """Execute one ORPDA/ORPA pass and merge structured outputs from sub-agents."""
    prompt = json.dumps(context, ensure_ascii=False)

    async with InMemoryRunner(agent=root_agent) as runner:
        events = await runner.run_debug(prompt, verbose=False)

    merged = {
        "observation": None,
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

            # merge only known ORPDA keys
            for key in merged.keys():
                if key in data:
                    merged[key] = data[key]

    # Remove None keys
    return {k: v for k, v in merged.items() if v is not None}


# -------------------------
# END
# -------------------------

if __name__ == "__main__":
    print("orpda_runner loaded (clean mode).")
