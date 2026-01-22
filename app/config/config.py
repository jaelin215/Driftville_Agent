# app/config/config.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Loads configuration from YAML and exposes model/drift flags.
# --------------------------------------
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "app/config/config.yaml"


def load_config():
    """Parse the YAML config file and return a dict."""
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)

def normalize_model_id(raw: str, default_provider: str | None = None) -> tuple[str, str]:
    raw = raw.strip()

    if "/" in raw:
        provider, model = raw.split("/", 1)
    else:
        provider, model = (default_provider or ""), raw

    # If someone redundantly wrote "gemini/gemini-2.5.flash", don't "double-prefix" later.

    if provider and model.startswith(provider + "-"):
        normalized_model = model
    else:
        normalized_model = model

    return provider, normalized_model

config = load_config()

MODELS_CONFIG = config.get("models_to_run", {})


DEFAULT_MODEL_CONFIG = MODELS_CONFIG.get("default", {})
MODEL_NAME = DEFAULT_MODEL_CONFIG.get("name", "gemini/gemini-2.5-flash-lite")
PROVIDER, MODEL_NAME = normalize_model_id(MODEL_NAME)
# These are the latest Gemini apis to change to - older models are not available
# gemini-2.5-flash
# gemini-2.5-flash-lite
# gemini-2.5-pro
# gemini-2.5-flash-image

MODEL_TEMPERATURE = DEFAULT_MODEL_CONFIG.get("temperature", 0.5)


USE_DRIFT = config.get("use_drift", True)
EMBEDDING_MODEL_NAME = config.get("embedding_model", {}).get(
    "name", "text-embedding-004"
)
EMBED_COST_PER_1K_TOKENS = config.get("embed_cost_per_1k_tokens", 0.00015)
PERSONA_NAME = config.get("sim_config", {}).get("persona", "Mei Lin")
SIM_START_TIME = config.get("sim_config", {}).get("start_time", "2023-02-13 06:00")
NUM_TICKS = config.get("sim_config", {}).get("num_ticks", 5)
LOAD_PROMPT_FROM_LANGFUSE = config.get("load_prompt_from_langfuse", False)
