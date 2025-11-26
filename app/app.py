from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import hashlib
import datetime

app = FastAPI()
EVENT_LOG_PATH = Path("app/logs/event_logs.jsonl")
MEMORY_LOG_PATH = Path("app/logs/memory.jsonl")


def load_events():
    events = []
    if EVENT_LOG_PATH.exists():
        with EVENT_LOG_PATH.open() as f:
            for line in f:
                try:
                    ev = json.loads(line)
                    events.append(ev)
                except Exception:
                    continue
    return sorted(events, key=lambda e: e.get("timestamp", ""))


def load_memories():
    grouped = {}
    if not MEMORY_LOG_PATH.exists():
        return grouped
    with MEMORY_LOG_PATH.open() as f:
        for line in f:
            try:
                mem = json.loads(line)
                participants = mem.get("participants") or []
                if not participants and mem.get("author"):
                    participants = [mem["author"]]
                if not participants:
                    participants = ["unknown"]
                for p in participants:
                    grouped.setdefault(p, []).append(mem)
            except Exception:
                continue
    return grouped


def color_for(name: str):
    # deterministic pastel-ish color from name hash
    h = hashlib.md5(name.encode()).hexdigest()
    r = int(h[:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return f"rgb({200 + r // 4},{200 + g // 4},{200 + b // 4})"


@app.get("/events")
def events():
    return JSONResponse(load_events())


@app.get("/memory")
def memory():
    return JSONResponse(load_memories())


from app.src.agents import AGENTS  # wherever you import it from


@app.get("/state")
def state():
    now_minutes = int(
        datetime.datetime.today().hour * 60 + datetime.datetime.today().minute
    )  # or your sim clock
    out = []
    for agent in AGENTS.values():
        action = agent.get_current_action(now_minutes)
        out.append(
            {
                "name": agent.name,
                "action": action["action"] if action else "idle",
                "location": action["location"] if action else "home",
            }
        )
    return JSONResponse(out)


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!doctype html>
<html>
<head>
  <style>
    :root {
      --bg: #f3f4f8;
      --card: #ffffff;
      --text: #2b2d42;
      --muted: #6c7080;
    }
    * { box-sizing: border-box; }
    body {
      font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      background: radial-gradient(circle at 20% 20%, #eef3ff 0, #f6f7fb 45%, #f3f4f8 100%);
      color: var(--text);
      min-height: 100vh;
      padding: 24px;
    }
    h2 { margin: 0 0 12px; letter-spacing: 0.3px; }
    #log { display: flex; flex-direction: column; gap: 16px; max-width: 960px; margin: 0 auto 48px; }
    .event {
      padding: 14px 16px;
      border-radius: 14px;
      background: var(--card);
      box-shadow: 0 12px 36px rgba(18, 38, 63, 0.08);
      border: 1px solid rgba(17, 24, 39, 0.04);
    }
    .meta {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 10px;
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }
    .pill {
      padding: 2px 8px;
      border-radius: 999px;
      background: #eef2ff;
      color: #4338ca;
      font-weight: 600;
      font-size: 11px;
    }
    .dialogue { display: flex; flex-direction: column; gap: 10px; }
    .msg {
      padding: 10px 12px;
      border-radius: 14px;
      max-width: 55%;
      display: inline-block;
      box-shadow: 0 6px 18px rgba(0,0,0,0.06);
      backdrop-filter: blur(4px);
      color: #111827;
    }
    .left  { align-self: flex-start; }
    .right { align-self: flex-end; text-align: right; }
    .name {
      min-width: 64px;
      font-weight: 700;
      font-size: 13px;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .emoji {
      font-size: 18px;
      line-height: 1;
    }
    .row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    #memories { max-width: 960px; margin: 0 auto; }
    .mem-card {
      margin-top: 10px;
      padding: 14px 16px;
      border-radius: 14px;
      background: var(--card);
      box-shadow: 0 12px 36px rgba(18, 38, 63, 0.08);
      border: 1px solid rgba(17, 24, 39, 0.04);
    }
    .mem-title { display: flex; align-items: center; gap: 8px; font-weight: 700; margin-bottom: 8px; }
    .mem-item { margin-bottom: 6px; color: var(--muted); font-size: 13px; }
    .mem-item strong { color: var(--text); }
  </style>
</head>
<body>
  <h2>Conversation Replay</h2>
  <div id="log"></div>
  <h2>Memories</h2>
  <div id="memories"></div>
  <script>
    const colorFor = (name) => {
      const h = Array.from(new TextEncoder().encode(name)).reduce((acc, v) => (acc + v) % 255, 0);
      const r = 180 + (h * 3) % 60;
      const g = 180 + (h * 5) % 60;
      const b = 180 + (h * 7) % 60;
      return { r, g, b };
    };
    const sideFor = (name, participants) => {
      const idx = (participants || []).indexOf(name);
      return idx % 2 === 0 ? "left" : "right"; // alternate by participant order
    };

    fetch("/events").then(r => r.json()).then(data => {
      const log = document.getElementById("log");
      data.forEach(ev => {
        const container = document.createElement("div");
        container.className = "event";

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `${ev.timestamp || ""} • ${ev.context || ""} • participants: ${(ev.participants || []).join(", ")}${ev.importance !== undefined ? " • importance " + ev.importance : ""}`;
        container.appendChild(meta);

        const dlg = document.createElement("div");
        dlg.className = "dialogue";
        (ev.dialogue || []).forEach(line => {
          const who = line.speaker || "?";
          const side = sideFor(who, ev.participants);

          const row = document.createElement("div");
          row.style.display = "flex";
          row.style.alignItems = "center";
          row.style.gap = "6px";
          if (side === "right") row.style.flexDirection = "row-reverse";

          const nameTag = document.createElement("div");
          nameTag.className = "name";
          nameTag.innerHTML = `<span class="emoji">💬</span>${who}`;

          const bubble = document.createElement("div");
          bubble.className = `msg ${side}`;
          const {r,g,b} = colorFor(who);
          bubble.style.background = `linear-gradient(135deg, rgba(${r},${g},${b},0.65), rgba(${r},${g},${b},0.4))`;
          bubble.style.border = `1px solid rgba(${r},${g},${b},0.55)`;
          bubble.textContent = line.text || "";

          row.appendChild(nameTag);
          row.appendChild(bubble);
          dlg.appendChild(row);
        });
        container.appendChild(dlg);
        log.appendChild(container);
      });
    });

    // render memories grouped by author
    fetch("/memory").then(r => r.json()).then(data => {
      const memRoot = document.getElementById("memories");
      Object.entries(data).forEach(([author, items]) => {
        const card = document.createElement("div");
        card.className = "mem-card";
        const title = document.createElement("div");
        title.className = "mem-title";
        title.innerHTML = `<span class="emoji">🧠</span>${author}`;
        card.appendChild(title);

        (items || []).forEach(m => {
          const {r,g,b} = colorFor(author);
          const line = document.createElement("div");
          line.className = "mem-item";
          line.innerHTML = `<strong style="color:rgb(${r},${g},${b});">(importance: ${m.importance ?? "-"})</strong> ${m.ts_created || ""} — ${m.text || ""}`;
          card.appendChild(line);
        });
        memRoot.appendChild(card);
      });
    });
  </script>
</body>
</html>
"""
