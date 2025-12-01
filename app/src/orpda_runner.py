from pathlib import Path
import yaml
import json
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.runners import InMemoryRunner
from google.adk.models.google_llm import Gemini
from app.config.config import MODEL_NAME  # your model choice

ROOT = Path(__file__).resolve().parent
YAML_DIR = ROOT / "yaml"


def build_agent(cfg_path: Path):
    cfg = yaml.safe_load(cfg_path.read_text())
    sub_agents = [
        build_agent((cfg_path.parent / s["config_path"]).resolve())
        for s in cfg.get("sub_agents", [])
    ]
    cls = cfg.get("agent_class", "LlmAgent")

    if cls == "SequentialAgent":
        return SequentialAgent(name=cfg["name"], sub_agents=sub_agents)
    if cls == "ParallelAgent":
        return ParallelAgent(name=cfg["name"], sub_agents=sub_agents)
    if cls == "LoopAgent":
        # Keep loop to 1 iteration per sim tick to avoid long-running inner loops.
        return LoopAgent(
            name=cfg["name"],
            sub_agents=sub_agents,
            max_iterations=1,
        )

    # Default: LlmAgent (optionally prepend to a Sequential if there are sub-agents)
    llm = LlmAgent(
        name=cfg["name"],
        model=Gemini(model=MODEL_NAME),
        instruction=cfg.get("instruction", ""),
        tools=[],  # extend if needed
    )
    if sub_agents:
        return SequentialAgent(
            name=f"{cfg['name']}_seq",
            sub_agents=[llm] + sub_agents,
        )
    return llm


root_agent = build_agent(YAML_DIR / "root_agent.yaml")


async def run_orpda_cycle(context: dict) -> dict:
    # ADK agents accept input and return events; unwrap to JSON dict
    prompt = json.dumps(context, ensure_ascii=False)
    async with InMemoryRunner(agent=root_agent) as runner:
        events = await runner.run_debug(prompt, verbose=False)
    out = {}
    for ev in events:
        if getattr(ev.content, "parts", None):
            for part in ev.content.parts:
                if getattr(part, "text", None):
                    try:
                        out.update(json.loads(part.text))
                    except Exception:
                        continue
    return out
