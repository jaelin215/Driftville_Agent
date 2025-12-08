#!/usr/bin/env python3
"""
Extract the `action_result` section from session logs and turn it into text prompts
that can be sent to Nano Banana (or any text-to-image model).

Usage:
    python tools/generate_nanobanana_prompts.py \
        --log-dir app/logs \
        --pattern 'session_*.log' \
        --text-only > prompts.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Iterator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate image prompts from session log action_result entries."
    )
    parser.add_argument(
        "--log-dir",
        default="app/logs",
        help="Directory containing session log files (default: app/logs)",
    )
    parser.add_argument(
        "--pattern",
        default="session_*.log",
        help="Glob pattern for session logs to include (default: session_*.log)",
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Emit only the prompt text (omit metadata JSON).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of prompts to emit across all files.",
    )
    return parser.parse_args()


def iter_logs(log_dir: Path, pattern: str) -> Iterator[Path]:
    for path in sorted(log_dir.glob(pattern)):
        if path.is_file():
            yield path


def load_lines(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def humanize_location(loc: str | None) -> str:
    if not loc:
        return "unspecified location"
    return loc.replace(":", " ").replace("_", " ")


def humanize_action(action: str | None) -> str:
    if not action:
        return "activity"
    return action.replace("_", " ")


def build_prompt(agent: str, sim_time: str, ar: dict) -> str:
    location = humanize_location(ar.get("location"))
    action = humanize_action(ar.get("action"))
    topic = ar.get("topic")
    state_summary = ar.get("state_summary")
    drift_type = ar.get("drift_type")
    drift_topic = ar.get("drift_topic")
    drift_intensity = ar.get("drift_intensity")

    parts = [
        f"{agent} {action} at {location}.",
    ]
    if sim_time:
        parts.append(f"Time: {sim_time}.")
    if topic:
        parts.append(f"Context: {topic}.")
    if state_summary:
        parts.append(state_summary)
    if drift_type and drift_type != "none":
        drift_detail = drift_topic or "attention drift"
        intensity = f" (intensity {drift_intensity})" if drift_intensity is not None else ""
        parts.append(f"Attention drift{intensity}: {drift_detail}.")
    parts.append("Create a vivid, realistic scene.")
    return " ".join(parts)


def collect_prompts(paths: Iterable[Path]) -> Iterator[dict]:
    for path in paths:
        for entry in load_lines(path):
            orpda = entry.get("orpda", {})
            action_result = orpda.get("action_result")
            if not action_result:
                continue
            prompt = build_prompt(
                agent=entry.get("agent", "Unknown agent"),
                sim_time=entry.get("sim_time", ""),
                ar=action_result,
            )
            yield {
                "log": str(path),
                "tick": entry.get("tick"),
                "sim_time": entry.get("sim_time"),
                "prompt": prompt,
            }


def main() -> None:
    args = parse_args()
    log_dir = Path(args.log_dir)
    prompts = collect_prompts(iter_logs(log_dir, args.pattern))

    emitted = 0
    for prompt in prompts:
        if args.text_only:
            print(prompt["prompt"])
        else:
            print(json.dumps(prompt))
        emitted += 1
        if args.limit is not None and emitted >= args.limit:
            break


if __name__ == "__main__":
    main()
