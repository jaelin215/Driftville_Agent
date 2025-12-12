#!/usr/bin/env python3
"""
Create Nano Banana-ready art prompts by pairing ORPA and ORPDA logs
for the same agent and sim_time.

Example:
    python tools/generate_scene_pairs.py --text-only --agent Isabella --time 11:00
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterator, List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate example pixel-art prompts for ORPA/ORPDA entries at the same time."
    )
    parser.add_argument(
        "--dir",
        default="app/logs",
        help="Directory with session log files (default: app/logs)",
    )
    parser.add_argument(
        "--orpa",
        default="session_orpa_*.log",
        help="Glob for ORPA logs (default: session_orpa_*.log)",
    )
    parser.add_argument(
        "--orpda",
        default="session_orpda_*.log",
        help="Glob for ORPDA logs (default: session_orpda_*.log)",
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Emit only the final prompt string per entry.",
    )
    parser.add_argument(
        "--agent",
        help="Case-insensitive substring to filter agent names (e.g., --agent tom).",
    )
    parser.add_argument(
        "--time",
        help="Substring match on sim_time to filter (e.g., --time 11:15).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional max number of prompts to emit (combined).",
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


def base_instructions() -> str:
    return (
        "Generate a 16:9 high-definition pixel art screenshot in a retro 16-bit RPG "
        "life-sim style (think Stardew Valley or Sims GBA). Use an isometric view, vibrant colors, "
        "and a game UI aesthetic. Add a small top-left pixel banner with the time and location for this image. "
        "Add a beige RPG dialogue box at the bottom labeled with the character name, containing the summary/context text. "
        "Include a consistent top title bar that reads 'ORPA' or 'ORPDA' in bold pixel font, white text on a black background; match the reference sample’s text size, stroke weight, padding, and bar height so labels are uniform across all images."
    )


def drift_instructions(
    drift_type: str | None, drift_topic: str | None, drift_intensity
) -> str:
    if not drift_type or drift_type == "none":
        return (
            "Standard mode: the character performs the action calmly and competently."
        )
    detail = drift_topic or "a distracting thought"
    intensity = f" (intensity {drift_intensity})" if drift_intensity is not None else ""
    if drift_type == "behavioral":
        return (
            f"Distraction mode{intensity}: show the behavioral drift. The character should visibly do the distraction "
            f"instead of the planned action, centered on {detail}. Facial expression should match the drift topic; default to curious/inspired/neutral unless the drift is clearly negative."
        )
    return (
        f"Distraction mode{intensity}: attentional leak. Show the main action, but the character is visibly preoccupied (expression fits the drift: default to calm/curious/upbeat daydreaming unless the drift is clearly negative), "
        f"with a thought bubble or subtle hint about {detail}."
    )


def build_prompt(entry: dict, source: str) -> str:
    ar = (
        entry.get("orpda", {}).get("action_result")
        or entry.get("action_result")
        or entry.get("orpda", {}).get("observation")
    )
    if not ar:
        return ""
    agent = entry.get("agent", "Unknown character")
    sim_time = entry.get("sim_time", "Unknown time")
    location = humanize_location(ar.get("location"))
    action = humanize_action(ar.get("action"))
    topic = ar.get("topic") or "No topic provided."
    state_summary = ar.get("state_summary") or topic
    drift_type = ar.get("drift_type")
    drift_topic = ar.get("drift_topic")
    drift_intensity = ar.get("drift_intensity")

    lines: List[str] = [
        f"Source: {source} | Agent: {agent} | Time: {sim_time}",
        base_instructions(),
        f"Scene: {agent} at {location}, {action}.",
        f"Context: {topic}",
        f"Dialogue text: {state_summary}",
        drift_instructions(drift_type, drift_topic, drift_intensity),
    ]
    return " ".join(lines)


def gather_entries(
    log_dir: Path, pattern: str, label: str
) -> Dict[Tuple[str, str], List[dict]]:
    grouped: Dict[Tuple[str, str], List[dict]] = {}
    for path in iter_logs(log_dir, pattern):
        for entry in load_lines(path):
            key = (entry.get("agent", ""), entry.get("sim_time", ""))
            grouped.setdefault(key, []).append(
                {"entry": entry, "label": label, "log": str(path)}
            )
    return grouped


def main() -> None:
    args = parse_args()
    log_dir = Path(args.dir)

    orpa = gather_entries(log_dir, args.orpa_pattern, "ORPA")
    orpda = gather_entries(log_dir, args.orpda_pattern, "ORPDA")

    keys = sorted(set(orpa.keys()) | set(orpda.keys()))

    if args.text_only:
        print("Create two images side by side for ORPA and ORPDA based on below:")

    emitted = 0
    for key in keys:
        agent, sim_time = key
        if args.agent and args.agent.lower() not in agent.lower():
            continue
        if args.time and args.time not in sim_time:
            continue
        if key in orpa:
            for wrap in orpa[key]:
                prompt = build_prompt(wrap["entry"], "ORPA")
                if not prompt:
                    continue
                if args.text_only:
                    print(prompt)
                else:
                    print(
                        json.dumps(
                            {
                                "agent": agent,
                                "sim_time": sim_time,
                                "mode": "ORPA",
                                "prompt": prompt,
                            }
                        )
                    )
                emitted += 1
                if args.limit is not None and emitted >= args.limit:
                    return
        if key in orpda:
            for wrap in orpda[key]:
                prompt = build_prompt(wrap["entry"], "ORPDA")
                if not prompt:
                    continue
                if args.text_only:
                    print(prompt)
                else:
                    print(
                        json.dumps(
                            {
                                "agent": agent,
                                "sim_time": sim_time,
                                "mode": "ORPDA",
                                "prompt": prompt,
                            }
                        )
                    )
                emitted += 1
                if args.limit is not None and emitted >= args.limit:
                    return


if __name__ == "__main__":
    main()
