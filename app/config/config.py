# app/config/config.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Loads configuration from YAML and exposes model/drift flags.
# --------------------------------------
import yaml
from pathlib import Path


ROOT = Path.cwd()
print(ROOT)


CONFIG_PATH = ROOT / "app/config/config.yaml"


def load_config():
    """Parse the YAML config file and return a dict."""
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


config = load_config()
MODEL_NAME = config.get("model", {}).get("name", "gemini-2.5-flash-lite")
MODEL_NAME_2 = config.get("model2", {}).get("name", "gemini-2.5-flash-lite")
USE_DRIFT = config.get("use_drift", True)
