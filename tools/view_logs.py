"""
Quick viewer for trace.log and memory_streams.log.

Usage:
  PYTHONPATH=. python tools/view_logs.py --trace app/logs/trace.log --memory app/logs/memory_streams.log --output tools/log_view.html
Then open tools/log_view.html in your browser.
"""

import argparse
import html
import json
from pathlib import Path
from collections import defaultdict

DEFAULT_TRACE = Path("app/logs/trace.log")
DEFAULT_MEMORY = Path("app/logs/memory_streams.log")
DEFAULT_SESSION = Path("app/logs/session.log")
DEFAULT_OUTPUT = Path("tools/log_view.html")


def read_jsonl(path: Path):
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def render_html(trace_entries, memory_entries, session_lines, output: Path):
    # Group trace by tick_idx
    by_tick = defaultdict(list)
    for e in trace_entries:
        by_tick[e.get("tick_idx", 0)].append(e)
    # Group memory by agent
    mem_by_agent = defaultdict(list)
    for m in memory_entries:
        mem_by_agent[m.get("agent", "unknown")].append(m)

    def esc(s):
        return html.escape(str(s))

    def bubble(turn, is_left=True):
        side = "left" if is_left else "right"
        return f"""
        <div class="bubble {side}">
          <div class="speaker">{esc(turn.get('speaker','?'))}</div>
          <div class="text">{esc(turn.get('text',''))}</div>
        </div>
        """

    blocks = []
    for tick in sorted(by_tick.keys()):
        for e in by_tick[tick]:
            agents = e.get("agents", [])
            dialogue = e.get("dialogue", [])
            blocks.append(f'<div class="tick"><div class="tick-header">Tick {tick} @ {esc(e.get("tick_time",""))}</div>')
            blocks.append('<div class="agents">')
            for a in agents:
                act = a.get("action") or {}
                refl = a.get("reflection") or {}
                blocks.append(f"""
                <div class="agent-card">
                  <div class="name">{esc(a.get('name',''))}</div>
                  <div><strong>Action:</strong> {esc(act.get('action','idle'))}</div>
                  <div><strong>Location:</strong> {esc(act.get('location',''))}</div>
                  <div><strong>Drift:</strong> {esc(act.get('drift_type',''))}</div>
                  <div><strong>Topic:</strong> {esc(act.get('topic',''))}</div>
                  <div><strong>Reflection:</strong> {esc(refl.get('state_summary',''))}</div>
                </div>
                """)
            blocks.append('</div>')  # agents
            if dialogue:
                blocks.append('<div class="dialogue">')
                for idx, turn in enumerate(dialogue):
                    blocks.append(bubble(turn, is_left=(idx % 2 == 0)))
                blocks.append('</div>')
            blocks.append('</div>')  # tick

    mem_blocks = []
    for agent, items in mem_by_agent.items():
        mem_blocks.append(f'<div class="mem-agent"><div class="mem-title">{esc(agent)}</div>')
        for m in items[-10:]:  # show last 10 per agent
            mem_blocks.append(f"""
            <div class="mem-item">
              <div><strong>ts:</strong> {esc(m.get('ts_created',''))}</div>
              <div>{esc(m.get('text',''))}</div>
            </div>
            """)
        mem_blocks.append('</div>')

    html_body = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Trace & Memory Viewer</title>
  <style>
    body {{ background:#0b132b; color:#f8f9ff; font-family: Arial, sans-serif; margin:0; padding:20px; }}
    .tick {{ border:1px solid rgba(111,255,233,0.3); border-radius:10px; padding:10px; margin-bottom:12px; }}
    .tick-header {{ font-weight:700; color:#6fffe9; margin-bottom:8px; }}
    .agents {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .agent-card {{ background:rgba(255,255,255,0.03); border:1px solid rgba(111,255,233,0.2); border-radius:8px; padding:8px; min-width:180px; }}
    .agent-card .name {{ font-weight:800; color:#ffd166; margin-bottom:4px; }}
    .dialogue {{ margin-top:8px; display:flex; flex-direction:column; gap:6px; }}
    .bubble {{ padding:8px 10px; border-radius:12px; max-width:70%; color:#0b132b; }}
    .bubble.left {{ align-self:flex-start; background:#ffd166; }}
    .bubble.right {{ align-self:flex-end; background:#6fffe9; }}
    .speaker {{ font-weight:700; margin-bottom:4px; }}
    .mem-section {{ margin-top:20px; }}
    .mem-title {{ font-weight:800; color:#6fffe9; margin-bottom:6px; }}
    .mem-item {{ background:rgba(255,255,255,0.03); border:1px solid rgba(111,255,233,0.2); border-radius:8px; padding:8px; margin-bottom:6px; }}
    .session-block {{ margin-top:20px; background:rgba(255,255,255,0.03); border:1px solid rgba(111,255,233,0.2); border-radius:8px; padding:10px; max-height:320px; overflow:auto; font-family: monospace; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h2>Trace (ticks)</h2>
  {''.join(blocks)}
  <div class="mem-section">
    <h2>Memory Streams (last 10 per agent)</h2>
    {''.join(mem_blocks)}
  </div>
  <div class="session-block">
    <h2>Session Log (stdout)</h2>
    {esc('\\n'.join(session_lines[-200:]))}
  </div>
</body>
</html>
"""
    output.write_text(html_body, encoding="utf-8")
    print(f"Wrote {output}")


def main():
    parser = argparse.ArgumentParser(description="View trace.log, memory_streams.log, and session.log as HTML")
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE, help="Path to trace.log")
    parser.add_argument("--memory", type=Path, default=DEFAULT_MEMORY, help="Path to memory_streams.log")
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION, help="Path to session.log (stdout)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output HTML file")
    args = parser.parse_args()

    trace_entries = read_jsonl(args.trace)
    memory_entries = read_jsonl(args.memory)
    session_lines = args.session.read_text(encoding="utf-8").splitlines() if args.session.exists() else []
    render_html(trace_entries, memory_entries, session_lines, args.output)


if __name__ == "__main__":
    main()
