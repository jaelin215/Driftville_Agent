# app/config/config.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Loads configuration from YAML and exposes model/drift flags.
# --------------------------------------
import yaml
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "app/config/config.yaml"


def load_config():
    """Parse the YAML config file and return a dict."""
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


config = load_config()
MODEL_NAME = config.get("model", {}).get("name", "gemini-2.5-flash-lite")
MODEL_NAME_2 = config.get("model2", {}).get("name", "gemini-2.5-flash")
USE_DRIFT = config.get("use_drift", True)
EMBEDDING_MODEL_NAME = config.get("embedding_model", {}).get(
    "name", "text-embedding-004"
)
PERSONA_NAME = config.get("sim_config", {}).get("persona", "Mei Lin")
SIM_START_TIME = config.get("sim_config", {}).get("start_time", "2023-02-13 06:00")
NUM_TICKS = config.get("sim_config", {}).get("num_ticks", 5)
LOAD_PROMPT_FROM_LANGFUSE = config.get("load_prompt_from_langfuse", False)
