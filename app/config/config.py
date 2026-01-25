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


###############################
# Load config
###############################
config = load_config()

###############################
# Simulation config
###############################
USE_DRIFT = config.get("use_drift", True)
PERSONA_NAME = config.get("sim_config", {}).get("persona", "Mei Lin")
SIM_START_TIME = config.get("sim_config", {}).get("start_time", "2023-02-13 06:00")
NUM_TICKS = config.get("sim_config", {}).get("num_ticks", 5)
LOAD_PROMPT_FROM_LANGFUSE = config.get("load_prompt_from_langfuse", False)

###############################
# Analytics config
###############################
EMBEDDING_MODEL_NAME = config.get("embedding_model", {}).get(
    "name", "text-embedding-004"
)
EMBED_COST_PER_1K_TOKENS = config.get("embed_cost_per_1k_tokens", 0.00015)

###############################
# Ollama config
###############################
OLLAMA_MODELS = config.get("ollama_models", {})
MODEL_NAME = OLLAMA_MODELS.get("default", "ollama/llama2:latest")
MODEL_TEMPERATURE = config.get("temperature", 0.1)

###############################
# Gemini config
###############################
# MODEL_NAME = config.get("model", {}).get("name", "gemini-2.5-flash-lite")
# MODEL_NAME_2 = config.get("model2", {}).get("name", "gemini-2.5-flash")

###############################
# LiteLLM config (using Ollama)
###############################
# OLLAMA_MODELS = config.get("ollama_models", {})
# LLAMA = OLLAMA_MODELS.get("llama", "ollama/llama2:latest")
# MISTRAL = OLLAMA_MODELS.get("mistral", "ollama/mistral:latest")
# QWEN = OLLAMA_MODELS.get("qwen", "ollama/qwen3:8b")
# GPT_OSS = OLLAMA_MODELS.get("gpt-oss", "ollama/gpt-oss:20b-cloud")
# DEEPSEEK = OLLAMA_MODELS.get("deepseek", "ollama/deepseek-r1:8b")

###############################
# OpenRouter config
###############################
# OPENROUTER_MODELS = config.get("openrouter_models", {})
