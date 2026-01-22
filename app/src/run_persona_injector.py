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
import os
import sys
from pathlib import Path
from app.config.config import load_config
import yaml

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
# DEFAULT_MODEL = "default"


def load_prompt_config(path: Path) -> dict:
    """Load the persona injector prompt configuration from YAML."""
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not cfg or "instruction" not in cfg:
        raise ValueError(f"No instruction found in {path}")
    return cfg


def ensure_api_key_env() -> None:
    """Load environment variables to expose Gemini keys."""
    load_dotenv()


async def call_llm(instruction: str, persona_text: str, model_name: str, temperature: float = None) -> str:
    """Invoke the Gemini-backed persona injector with provided instruction and text."""
    from app.src.llm_api import (
        call_llm as call_llm_api,  # late import to honor env setup
    )

    print(model_name)
    # print(persona_text)
    # print(instruction)

    prompt = f"{instruction.strip()}\n\nUser Input:\n{persona_text.strip()}\n"
    resp = await call_llm_api(prompt, model_name, temperature=temperature)
    if not resp or not str(resp).strip():
        raise RuntimeError("LLM returned empty response")
    return str(resp).strip()

async def run_all_models(
        instruction: str, persona_text: str, models_to_run: dict) -> list[tuple[str, str]]:
    """Run persona generation for all specified models concurrently."""
    tasks = []
    for model_key, model_config in models_to_run.items():
        tasks.append(call_llm(instruction, persona_text, model_key, model_config.get("temperature")))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # pair model keys with their results for easy identitication

    return list(zip(models_to_run.keys(), results))


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
        # help=f"Override model name (default: value in persona_injector.yaml, fallback {DEFAULT_MODEL})",
        help="Run for a single specific model key from config.yaml (e.g., gemini-1.5-pro"
    )
    args = parser.parse_args()

    cfg = load_prompt_config(YAML_PATH)
    instruction = cfg.get("instruction", "")

    # Load models from the main config file
    app_config = load_config()
    all_models = app_config.get("models_to_run", {})

    if not all_models:
        raise SystemExit(
            "Error: No models found under 'models_to_run' in your config.yaml."
        )

    models_to_run = {}
    if args.model:
        if args.model in all_models:
            models_to_run[args.model] = all_models[args.model]
        else:
            raise SystemExit(
                f"Error: Model key '{args.model}' not found in config.yaml under 'models_to_run'."
                f"Available keys: {list(all_models.keys())}"
            )
    else:
        models_to_run = all_models

    # model_name = args.model or cfg.get("model") or DEFAULT_MODEL
    # os.environ["MODEL_NAME"] = model_name  # hint for gemini_api config

    persona_text = args.input.read_text(encoding="utf-8")
    try:
        # raw = asyncio.run(
        #     asyncio.wait_for(
        #         call_llm(instruction, persona_text, model_name), timeout=60
        #     )
        # )
        model_results = asyncio.run(
            run_all_models(instruction, persona_text, models_to_run)
        )
    except Exception as e:
        raise SystemExit(f"An unexpected error occurred: {e}")
    # except asyncio.TimeoutError:
    #     raise SystemExit("LLM call timed out. Try a smaller input or increase timeout.")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # # Try to pretty-format JSON if possible
    # cleaned = raw
    # try:
    #     parsed = json.loads(raw)
    #     cleaned = json.dumps(parsed, indent=2)
    # except Exception:
    #     pass
    #
    # if args.output:
    #     args.output.parent.mkdir(parents=True, exist_ok=True)
    #     args.output.write_text(cleaned, encoding="utf-8")
    #     print(f"Wrote output to {args.output}")
    # else:
    #     print(cleaned)

    for model_key, result in model_results:
        if isinstance(result, Exception):
            print(f"Failed to generate persona for '{model_key}': {result}")
            continue

        if result == "Error generating response":
            print(f"Failed to generate persona for '{model_key}': LLM API error")
            continue

        # Try to pretty-format JSON if possible
        cleaned_output = result
        try:
            if "```json" in cleaned_output:
                cleaned_output = cleaned_output.split("```json")[1].split("```")[0]
            parsed = json.loads(cleaned_output)
            cleaned_output = json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            print(f"Warning: Output for '{model_key}' is not a valid JSON. Saving raw output.")
            pass

        output_file = args.output_dir / f"driftville_personas_{model_key}.json"
        output_file.write_text(cleaned_output, encoding="utf-8")
        print(f"Successfully wrote output for '{model_key}' to {output_file}")

if __name__ == "__main__":
    main()
