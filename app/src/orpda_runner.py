# app/src/orpda_runner.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Builds the YAML-defined agent graph and runs a single ORPDA cycle.
# --------------------------------------
"""
orpda_runner.py
Minimal ORPDA engine:
- Loads root_agent from YAML
- Runs ORPDA loop via InMemoryRunner
- Extracts structured JSON from model output
"""

import asyncio
import json
import logging
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*Pydantic serializer warnings.*")

import yaml
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.events import Event, EventActions

# from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from langfuse import Langfuse, get_client, propagate_attributes
from opentelemetry import trace

# -------------------------
# Load environment & paths
# -------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
print(REPO_ROOT)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from app.config.config import (
    LOAD_PROMPT_FROM_LANGFUSE,
    MODEL_NAME,
    # MODEL_TEMPERATURE,
    NUM_TICKS,
    PERSONA_NAME,
    SIM_START_TIME,
    USE_DRIFT,
)
from app.src.observe_non_llm_agent import deterministic_observe

# Initialize local/cloud Ollama model via LiteLLM
try:
    my_local_model = LiteLlm(model=f"ollama/{MODEL_NAME}")
    print("Successfully loaded a model via LiteLLM")
except Exception as e:
    print(f"Error: {type(e).__name__}: e")
    print("Failed to load model vis LiteLLM")
print("import complete")

load_dotenv()

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
YAML_DIR = ROOT / "yaml"

# -------------------------
# Setup Langfuse
# -------------------------
# Assign tags automatically depends on USE_DRIFT config value
if USE_DRIFT:
    tags = [
        "ORPDA",
        PERSONA_NAME,
        f"num_ticks={NUM_TICKS}",
        f"start={SIM_START_TIME.split(' ')[-1]}",
        MODEL_NAME,
    ]
else:
    tags = [
        "ORPA",
        PERSONA_NAME,
        f"num_ticks={NUM_TICKS}",
        f"start={SIM_START_TIME.split(' ')[-1]}",
        MODEL_NAME,
    ]

langfuse = get_client()


# -------------------------
# Build Observation Agent (non-LLM)
# -------------------------
class FunctionAgent(BaseAgent):
    """Initializes a FunctionAgent with a name and a function to execute.

    Sets up the agent with the provided name and stores the function for later execution.

    Args:
        name: The name of the agent.
        fn: A callable that processes the agent's context and returns a dictionary.
    """

    def __init__(self, name, fn):
        super().__init__(name=name)
        # Agent inherits from a Pydantic model; use object.__setattr__ to bypass field checks
        object.__setattr__(self, "_fn", fn)

    async def arun(self, ctx, *, send):
        """Runs the agent asynchronously and emits the function's output as JSON.

        Converts the input context to a dictionary if needed, applies the agent's function, and sends the result as a JSON-formatted message.

        Args:
            ctx: The input context, either as a string or dictionary.
            send: A coroutine for sending output messages.

        Returns:
            The output dictionary produced by the agent's function.
        """
        # ctx arrives as a string; load it if needed
        if isinstance(ctx, str):
            try:
                ctx_obj = json.loads(ctx)
            except Exception:
                ctx_obj = {"raw": ctx}
        else:
            ctx_obj = ctx

        output = self._fn(ctx_obj)  # -> {"observation": ...}
        # emit as JSON text so your downstream merge loop picks it up
        try:
            await send(json.dumps(output))
        except Exception:
            # Fallback: some runtimes may not support sending raw strings here
            pass
        return output

    async def _run_async_impl(self, ctx):
        """Emit deterministic observation as a synthetic Event (no LLM call)."""
        text = ""
        if ctx.user_content and getattr(ctx.user_content, "parts", None):
            for part in ctx.user_content.parts:
                if getattr(part, "text", None):
                    text += part.text or ""

        try:
            ctx_obj = json.loads(text) if text else {}
        except Exception:
            ctx_obj = {"raw": text}

        output = self._fn(ctx_obj)
        content = Content(role=self.name, parts=[Part(text=json.dumps(output))])
        event = Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=content,
            actions=EventActions(end_of_agent=True),
        )
        yield event


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

    # 3) Simple factual summary (can be refined later)
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
# Build Agent from YAML
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

    # Non-LLM tool agent (for Symbolic Observer)
    if cls == "ToolAgent":
        tool = cfg.get("tool_name")
        if tool == "deterministic_observer":
            return FunctionAgent(name=cfg["name"], fn=deterministic_observe)
        raise ValueError(f"Unknown tool_name: {tool}")

    # Default: LlmAgent
    instruction_text = cfg.get("instruction", "")
    instruction_field = instruction_text

    # If Langfuse client is available, link prompts even when using local YAML
    if langfuse and not LOAD_PROMPT_FROM_LANGFUSE:
        instruction_field = create_local_instruction_with_link(
            langfuse, cfg["name"], instruction_text
        )

    llm = LlmAgent(
        name=cfg["name"],
        model=my_local_model,
        instruction=instruction_field,
        tools=[],
    )

    # If sub-agents exist, wrap in sequential
    return (
        SequentialAgent(name=f"{cfg['name']}_seq", sub_agents=[llm] + sub_agents)
        if sub_agents
        else llm
    )


# -------------------------
# Build Agent from Langfuse Prompt
# -------------------------
def create_dynamic_instruction(
    langfuse, prompt_name: str, label: str = "latest", fallback: str = ""
):
    def get_instruction(ctx):
        prompt = None
        # Link this prompt to the current generation/span
        try:
            prompt = langfuse.get_prompt(prompt_name, label=label)
            langfuse.update_current_generation(prompt=prompt)
            current_span = trace.get_current_span()
            current_span.set_attribute("langfuse.observation.prompt.name", prompt.name)
            current_span.set_attribute(
                "langfuse.observation.prompt.version", prompt.version
            )
        except Exception:
            # If we can't fetch/link, log and fall back to local text
            logger.warning(
                f"failed to fetch/link Langfuse prompt (label={label}); "
                "falling back to local instruction",
                prompt_name,
                label,
                exc_info=True,
            )
            pass  # don't break the run if linkage fails

        if prompt:
            return prompt.compile()
        return fallback

    return get_instruction


def create_local_instruction_with_link(
    langfuse_client, prompt_name: str, local_instruction: str, label: str = "latest"
):
    """Return a callable that links a Langfuse prompt but returns the local instruction text."""

    def get_instruction(ctx):
        try:
            prompt = langfuse_client.get_prompt(prompt_name, label=label)
            langfuse_client.update_current_generation(prompt=prompt)
            current_span = trace.get_current_span()
            current_span.set_attribute("langfuse.observation.prompt.name", prompt.name)
            current_span.set_attribute(
                "langfuse.observation.prompt.version", prompt.version
            )
        except Exception:
            # If we can't fetch/link, fall back silently to local text
            pass
        return local_instruction

    return get_instruction


def build_agent_from_langfuse_prompt(cfg_path: Path):
    """Recursively construct ADK agents from YAML configs."""
    cfg = str(cfg_path).split("/")[-1].split(".yaml")[0]
    print(cfg)  # ORPDA | ORPA

    langfuse = Langfuse()

    reflector_prompt_path = "reflector"
    planner_prompt_path = "planner"
    drifter_prompt_path = "drifter"
    actor_prompt_path = "actor_orpda" if USE_DRIFT else "actor_orpa"

    reflector_agent = LlmAgent(
        name="reflector",
        model=my_local_model,
        include_contents="none",  # default | none
        instruction=create_dynamic_instruction(
            langfuse, reflector_prompt_path, label="latest"
        ),
        tools=[],
    )

    planner_agent = LlmAgent(
        name="planner",
        model=my_local_model,
        include_contents="none",  # default | none
        instruction=create_dynamic_instruction(
            langfuse, planner_prompt_path, label="latest"
        ),
        tools=[],
    )

    drifter_agent = LlmAgent(
        name="drifter",
        model=my_local_model,
        include_contents="default",  # default | none
        instruction=create_dynamic_instruction(
            langfuse, drifter_prompt_path, label="latest"
        ),
        tools=[],
    )

    actor_agent = LlmAgent(
        name="actor",
        model=my_local_model,
        include_contents="none",  # default | none
        instruction=create_dynamic_instruction(
            langfuse, actor_prompt_path, label="latest"
        ),
        tools=[],
    )

    # Non-LLM tool agent
    observer_agent = FunctionAgent(name="observer", fn=deterministic_observe)

    # If sub-agents exist, wrap in sequential
    agent_name = Path(cfg).stem
    if USE_DRIFT:
        return SequentialAgent(
            name=f"{agent_name}_sequence",
            sub_agents=[
                observer_agent,
                reflector_agent,
                planner_agent,
                drifter_agent,
                actor_agent,
            ],
        )
    else:
        return SequentialAgent(
            name=f"{agent_name}_sequence",
            sub_agents=[
                observer_agent,
                reflector_agent,
                planner_agent,
                actor_agent,
            ],
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

root_agent = (
    build_agent_from_langfuse_prompt(YAML_DIR / cfg_path)
    if LOAD_PROMPT_FROM_LANGFUSE
    else build_agent(YAML_DIR / cfg_path)
)


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
    with langfuse.start_as_current_observation(as_type="span", name="my-trace") as _:
        # Let the observer ToolAgent run first; start with raw context
        prompt = json.dumps(context, ensure_ascii=False)

        # Add tags to all observations created within this execution scope

        with propagate_attributes(tags=tags):
            # Google ADK runner call here
            async with InMemoryRunner(agent=root_agent) as runner:
                events = await runner.run_debug(prompt, verbose=False)

    # 3) Seed merged values; observation will be filled from ToolAgent or fallback
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
            for key in (
                "observation",
                "reflection",
                "plan",
                "drift_decision",
                "action_result",
            ):
                if key in data:
                    merged[key] = data[key]

    # If observer output didn't arrive, fall back to local deterministic version
    if merged["observation"] is None:
        merged["observation"] = build_observation(context)["observation"]

    # Remove None keys
    return {k: v for k, v in merged.items() if v is not None}


# -------------------------
# END
# -------------------------

if __name__ == "__main__":
    print("orpda_runner loaded (clean mode).")
    context = {
        "persona": {
            "name": "Isabella Rodriguez",
            "occupation": "Cafe Owner",
            "relationship": {"name": "", "relation_type": "family"},
            "innate_tendency": ["friendly", "outgoing", "hospitable"],
            "learned_tendency": "Isabella Rodriguez is a cafe owner who loves to make people feel welcome.",
            "current_situation": "Planning a Valentine's Day party.",
            "lifestyle": "goes to bed around 11pm, wakes around 6am.",
        },
        "schedule": [
            {
                "datetime_start": "2023-02-13 06:00",
                "duration_min": 15,
                "location": "home:bedroom",
                "action": "morning_routine",
                "environment_description": "alarm clock ringing, coffee machine whirring, sunlight filtering",
                "notes": "morning routine",
            },
            {
                "datetime_start": "2023-02-13 08:00",
                "duration_min": 15,
                "location": "Hobbs_Cafe:main_floor",
                "action": "work",
                "environment_description": "espresso machine whirring, customers ordering, music playing",
                "notes": "opening cafe",
            },
        ],
    }

    async def run():
        response = await run_orpda_cycle(context=context)
        print("Response:", response)
        return response

    asyncio.run(run())
