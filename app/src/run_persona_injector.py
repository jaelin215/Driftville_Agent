# app/src/run_persona_injector.py
# --------------------------------------
# Author: Jaelin Lee
# Description: CLI to run the persona_injector agent and write generated personas.
# --------------------------------------
"""
Run the persona_injector LLM agent to generate a persona+schedules JSON block.

Usage:
  python app/src/run_persona_injector.py --input raw_persona.txt --output app/src/driftville_personas.json

By default prints the LLM JSON to stdout. If --output is provided, writes there.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[2]
# print(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import yaml

from app.config.config import MODEL_NAME, MODEL_TEMPERATURE

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover

    def load_dotenv() -> None:
        return None


BASE_DIR = Path(__file__).resolve().parent  # app/src
ROOT_DIR = BASE_DIR.parent  # app
REPO_ROOT = ROOT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
YAML_PATH = ROOT_DIR / "src/yaml/persona_injector.yaml"


def load_prompt_config(path: Path) -> dict:
    """Load the persona injector prompt configuration from YAML."""
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not cfg or "instruction" not in cfg:
        raise ValueError(f"No instruction found in {path}")
    return cfg


def ensure_api_key_env() -> None:
    """Load environment variables to expose API keys."""
    load_dotenv()


async def call_llm(instruction: str, persona_text: str, model_name: str) -> str:
    """Invoke the persona injector with provided instruction and text."""
    from app.src.ollama_api import call_ollama  # late import to honor env setup

    print("here!!", model_name)
    # print(persona_text)
    # print(instruction)

    prompt = f"{instruction.strip()}\n\nUser Input:\n{persona_text.strip()}\n"
    resp = await call_ollama(
        prompt, model_name, use_stream=True, temperature=MODEL_TEMPERATURE
    )
    if not resp or not str(resp).strip():
        raise RuntimeError("LLM returned empty response")
    return str(resp).strip()


def main() -> None:
    """CLI entry to generate personas from raw input text."""
    ensure_api_key_env()
    parser = argparse.ArgumentParser(description="Run persona_injector LLM agent.")
    parser.add_argument(
        "--input",
        type=Path,
        default=BASE_DIR / "smallville_personas.json",
        help="Path to file containing raw persona text",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "driftville_personas.json",
        help="Path to write LLM JSON output (default: app/src/driftville_personas.json)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Override model name (default: value in persona_injector.yaml, fallback {MODEL_NAME})",
    )
    args = parser.parse_args()

    cfg = load_prompt_config(YAML_PATH)
    instruction = cfg.get("instruction", "")
    # model_name = args.model or cfg.get("model") or MODEL_NAME
    # os.environ["MODEL_NAME"] = model_name  # hint for gemini_api config

    persona_text = args.input.read_text(encoding="utf-8")
    try:
        raw = asyncio.run(
            asyncio.wait_for(
                call_llm(instruction, persona_text, MODEL_NAME), timeout=60
            )
        )
    except asyncio.TimeoutError:
        raise SystemExit("LLM call timed out. Try a smaller input or increase timeout.")

    # Try to pretty-format JSON if possible
    cleaned = raw
    try:
        parsed = json.loads(raw)
        cleaned = json.dumps(parsed, indent=2)
    except Exception:
        pass

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(cleaned, encoding="utf-8")
        print(f"Wrote output to {args.output}")
    else:
        print(cleaned)


if __name__ == "__main__":
    main()
