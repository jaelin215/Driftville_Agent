import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd


def read_json_lines(path: Path) -> List[Dict[str, Any]]:
    """Load newline-delimited JSON records from a session log."""
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Line {idx} in {path} is not valid JSON: {exc}"
                ) from exc
    if not records:
        raise ValueError(f"No JSON records found in {path}")
    return records


def log_to_dataframe(log_path: Path) -> pd.DataFrame:
    """Flatten one session log into a dataframe and tag its source."""
    records = read_json_lines(log_path)
    df = pd.json_normalize(records, sep=".")
    df["source_log"] = str(log_path)
    return df


def find_logs(root: Path, pattern: str) -> List[Path]:
    """Collect session logs matching the glob pattern only in the given directory (no recursion)."""
    return sorted(p for p in root.glob(pattern) if p.is_file())


def convert_logs_to_parquet(log_paths: Iterable[Path], parquet_path: Path) -> None:
    """Combine multiple session logs into one Parquet file."""
    frames = [log_to_dataframe(p) for p in log_paths]
    if not frames:
        raise ValueError("No session logs found to convert.")
    df = pd.concat(frames, ignore_index=True, sort=False)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, engine="pyarrow", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert Driftville session logs (JSONL) to Parquet. "
            "Pass a single file to convert it, or a directory to combine matching logs."
        )
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        help="Session log file or directory containing session logs.",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        default="session*.log",
        help="Glob pattern for logs when a directory is provided (default: session*.log).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Output Parquet path. "
            "Defaults to <log>.parquet for a file, or combined_sessions.parquet in the directory."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Default: combine all session logs under app/logs if no path is provided.
    target_path: Path = args.path if args.path else Path("app/logs")

    if target_path.is_file():
        output_path = (
            args.output
            if args.output
            else target_path.with_suffix(target_path.suffix + ".parquet")
        )
        convert_logs_to_parquet([target_path], output_path)
        print(f"Wrote Parquet to {output_path}")
        return

    if target_path.is_dir():
        logs = find_logs(target_path, args.pattern)
        if not logs:
            raise SystemExit(
                f"No logs matching pattern '{args.pattern}' under {target_path}"
            )
        output_path = (
            args.output if args.output else target_path / "combined_sessions.parquet"
        )
        convert_logs_to_parquet(logs, output_path)
        print(f"Combined {len(logs)} logs into {output_path}")
        return

    raise SystemExit(f"{target_path} is neither a file nor directory.")


if __name__ == "__main__":
    main()
