from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import hashlib
import datetime
import json as _json

app = FastAPI()
EVENT_LOG_PATH = Path("app/logs/event_logs.jsonl")
MEMORY_LOG_PATH = Path("app/logs/memory.jsonl")
SMALLVILLE_PATH = Path("app/src/smallville_personas.json")
UI_SIM_LOG_PATH = Path("app/logs/ui_simulate.log")


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


from app.src.agents import AGENTS, Agent  # wherever you import it from
from app.src.conversation_manager import ConversationManager, with_backoff
from app.src.orpda_runner import run_orpda_cycle
from datetime import timedelta

try:
    _raw_smallville = _json.loads(SMALLVILLE_PATH.read_text())
    RAW_PERSONAS = {p.get("name"): p.get("raw_persona", "") for p in _raw_smallville}
except Exception:
    RAW_PERSONAS = {}


def _make_agent(name: str):
    """Create a lightweight Agent with raw persona text."""
    persona_text = RAW_PERSONAS.get(name, "")
    agent = Agent(name=name, personality={"raw_persona": persona_text}, daily_schedule=[])
    agent.memory = []
    return agent

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
                "drift_type": (action or {}).get("drift_type", "none"),
                "drift_intensity": (action or {}).get("drift_intensity"),
                "topic": (action or {}).get("topic"),
            }
        )
    return JSONResponse(out)


@app.get("/personas")
def personas():
    return JSONResponse({"personas": sorted(RAW_PERSONAS.keys())})


async def _run_tick(agent_a, agent_b, current_time, agent_states, minutes_per_step=15):
    """Run one ORPDA tick for both agents and optionally generate a short dialogue."""
    tick_start = current_time.strftime("%Y-%m-%d %H:%M")
    for agent in (agent_a, agent_b):
        ctx = {
            "raw_persona": getattr(agent, "personality", {}).get("raw_persona", ""),
            "last_action_result": agent_states[agent.name]["last_action_result"],
            "recent_history": agent_states[agent.name]["history"][-3:],
            "current_datetime": tick_start,
        }
        orpda_out = await run_orpda_cycle(ctx)
        action_result = orpda_out.get("action_result") or {}
        drift_decision = orpda_out.get("drift_decision") or {}
        plan = orpda_out.get("plan") or {}
        reflection = orpda_out.get("reflection") or {}
        observation = orpda_out.get("observation")

        # clamp timing to tick
        action_result["datetime_start"] = tick_start
        plan["datetime_start"] = tick_start
        action_result["duration_min"] = minutes_per_step
        plan["duration_min"] = minutes_per_step
        action_result["next_datetime"] = (
            current_time + timedelta(minutes=minutes_per_step)
        ).strftime("%Y-%m-%d %H:%M")

        agent_states[agent.name]["last_action_result"] = action_result
        agent_states[agent.name]["history"].append(
            {
                "observation": observation,
                "reflection": reflection,
                "plan": plan,
                "drift_decision": drift_decision,
                "action_result": action_result,
            }
        )

        agent.current_action = {
            "action": action_result.get("action", plan.get("action", "idle")),
            "location": action_result.get("location", plan.get("location", "home")),
            "drift_type": action_result.get(
                "drift_type", drift_decision.get("drift_type", "none")
            ),
            "topic": action_result.get("topic") or plan.get("topic"),
            "drift_intensity": drift_decision.get("drift_intensity"),
            "sim_datetime": action_result.get("datetime_start", tick_start),
        }

    # Force a short conversation each tick
    cm = ConversationManager(agent_a, agent_b)
    dialogue = []
    speaker, listener = agent_a, agent_b
    MAX_TURNS = 4
    for _ in range(MAX_TURNS):
        if not await cm.wants_to_speak(speaker, listener, "tick", dialogue):
            break
        line = await with_backoff(
            cm.generate_turn, speaker, listener, "tick", dialogue
        )
        if not line:
            break
        dialogue.append(line)
        speaker, listener = listener, speaker

    return {
        "tick_time": tick_start,
        "agents": [
            {
                "name": agent_a.name,
                "action": agent_a.current_action,
                "reflection": agent_states[agent_a.name]["history"][-1]
                .get("reflection", {}),
            },
            {
                "name": agent_b.name,
                "action": agent_b.current_action,
                "reflection": agent_states[agent_b.name]["history"][-1]
                .get("reflection", {}),
            },
        ],
        "dialogue": dialogue,
    }


@app.post("/simulate_pair")
async def simulate_pair(payload: dict):
    """Run a short 2-tick ORPDA conversation for two selected personas."""
    name_a = payload.get("agent1")
    name_b = payload.get("agent2")
    if not name_a or not name_b or name_a not in RAW_PERSONAS or name_b not in RAW_PERSONAS:
        return JSONResponse({"error": "agent1 and agent2 must be valid persona names"}, status_code=400)

    agent_a = _make_agent(name_a)
    agent_b = _make_agent(name_b)

    agent_states = {name_a: {"last_action_result": None, "history": []},
                    name_b: {"last_action_result": None, "history": []}}

    now = datetime.datetime.now().replace(second=0, microsecond=0)
    timeline = []
    for _ in range(2):  # two ticks
        tick = await _run_tick(agent_a, agent_b, now, agent_states, minutes_per_step=15)
        timeline.append(tick)
        now = now + timedelta(minutes=15)

    # Append to UI simulation log for real-time inspection (includes per-turn dialogue and per-tick agent states)
    try:
        UI_SIM_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent1": name_a,
            "agent2": name_b,
            "timeline": timeline,
            "agent_states": agent_states,
        }
        with UI_SIM_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass

    return JSONResponse({"timeline": timeline, "agent_states": agent_states})


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
  <div id="controls" style="margin-bottom:12px; display:flex; gap:8px; flex-wrap:wrap;">
    <select id="agent1"></select>
    <select id="agent2"></select>
    <button id="run">Simulate 2 steps</button>
  </div>
  <div id="log"></div>
  <h2>Memories</h2>
  <div id="memories"></div>
  <script>
    const agent1Sel = document.getElementById("agent1");
    const agent2Sel = document.getElementById("agent2");
    const runBtn = document.getElementById("run");
    const log = document.getElementById("log");

    fetch("/personas").then(r => r.json()).then(data => {
      (data.personas || []).forEach(name => {
        const opt1 = document.createElement("option");
        opt1.value = opt1.textContent = name;
        const opt2 = opt1.cloneNode(true);
        agent1Sel.appendChild(opt1);
        agent2Sel.appendChild(opt2);
      });
    });

    runBtn.onclick = () => {
      log.innerHTML = "";
      fetch("/simulate_pair", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent1: agent1Sel.value, agent2: agent2Sel.value }),
      }).then(r => r.json()).then(data => {
        (data.timeline || []).forEach((tick, idx) => {
          const wrap = document.createElement("div");
          wrap.className = "event";
          const header = document.createElement("div");
          header.className = "meta";
          header.textContent = `Tick ${idx + 1} @ ${tick.tick_time}`;
          wrap.appendChild(header);

          const drift = document.createElement("div");
          drift.className = "meta";
          drift.textContent = tick.agents.map(a => `${a.name}: ${a.action.drift_type || 'none'} (${a.action.topic || ''})`).join(" | ");
          wrap.appendChild(drift);

          const reflections = document.createElement("div");
          reflections.className = "meta";
          reflections.textContent = tick.agents.map(a => {
            const ref = a.reflection || {};
            const st = ref.state_summary || "";
            const attn = ref.attention_stability || "";
            return `${a.name}: ${st} ${attn ? `[attention: ${attn}]` : ""}`;
          }).join(" | ");
          wrap.appendChild(reflections);

          const diag = document.createElement("div");
          diag.className = "dialogue";
          (tick.dialogue || []).forEach(turn => {
            const row = document.createElement("div");
            row.className = "row";
            const name = document.createElement("div");
            name.className = "name";
            name.textContent = turn.speaker;
            const bubble = document.createElement("div");
            bubble.className = `msg ${turn.speaker === tick.agents[0].name ? "left" : "right"}`;
            bubble.textContent = turn.text;
            row.appendChild(name);
            row.appendChild(bubble);
            diag.appendChild(row);
          });
          wrap.appendChild(diag);
          log.appendChild(wrap);
        });
      });
    };

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
