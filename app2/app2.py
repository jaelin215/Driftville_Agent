from flask import Flask, render_template_string, request, jsonify
import json
from pathlib import Path
import subprocess
import os

APP = Flask(__name__)
PERSONA_PATH = (
    Path(__file__).resolve().parent.parent / "app/src/driftville_personas.json"
)
RAW_PERSONA_PATH = (
    Path(__file__).resolve().parent.parent / "app/src/smallville_personas.json"
)


def _minutes_from_dt(dt_str: str) -> int:
    try:
        parts = dt_str.split(" ")
        hm = parts[1]
        h, m = hm.split(":")[:2]
        return int(h) * 60 + int(m)
    except Exception:
        return 0


def load_personas():
    """Load personas from driftville_personas.json and normalize schedules to start/end minutes, attaching raw bios from smallville_personas.json."""
    with PERSONA_PATH.open() as f:
        raw = json.load(f)

    raw_map = {}
    if RAW_PERSONA_PATH.exists():
        try:
            with RAW_PERSONA_PATH.open() as f:
                raw_src = json.load(f)
                for item in raw_src:
                    raw_map[item.get("name")] = item.get("raw_persona", "")
        except Exception:
            raw_map = {}

    personas = []
    for entry in raw:
        p = entry.get("persona", {})
        name = p.get("name", "Unknown")
        schedule = []
        for slot in entry.get("schedule", []):
            start_min = _minutes_from_dt(slot.get("datetime_start", "00:00"))
            dur = int(slot.get("duration_min", 0))
            schedule.append(
                {
                    "datetime_start": slot.get("datetime_start"),
                    "start_time": start_min,
                    "end_time": start_min + dur,
                    "duration_min": dur,
                    "location": slot.get("location", "home"),
                    "action": slot.get("action", ""),
                    "environment_description": slot.get("environment_description", ""),
                    "notes": slot.get("notes", ""),
                }
            )
        personas.append(
            {
                "name": name,
                "raw_persona": raw_map.get(name, ""),
                "schedule": schedule,
            }
        )
    return personas


PERSONAS = load_personas()

EMOJI_MAP = {
    "Isabella Rodriguez": "☕️",
    "Tom Moreno": "🛒",
    "Giorgio Rossi": "📐",
    "Adam Smith": "📚",
    "Sam Moore": "🪴",
    "Maria Lopez": "🎮",
    "Mei Lin": "🎓",
    "Jennifer Moore": "🎨",
    "Hailey Johnson": "✍️",
    "Eddy Lin": "🎼",
    "John Lin": "💊",
    "Abigail Chen": "🖥️",
}
FACE_MAP = {
    "Isabella Rodriguez": "👩",
    "Tom Moreno": "👨",
    "Giorgio Rossi": "👨",
    "Adam Smith": "👨",
    "Sam Moore": "👨",
    "Maria Lopez": "👩",
    "Mei Lin": "👩",
    "Jennifer Moore": "👩",
    "Hailey Johnson": "👩",
    "Eddy Lin": "👨",
    "John Lin": "👨",
    "Abigail Chen": "👩",
}

HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Driftville</title>
  <style>
    body { font-family: "Press Start 2P", "Inter", -apple-system, sans-serif; margin:0; padding:0; background: radial-gradient(circle at 20% 20%, #1c2541, #0b132b); color:#f8f9ff; }
    header { padding: 18px 24px; background: rgba(255,255,255,0.06); box-shadow: 0 10px 25px rgba(0,0,0,0.25); position: sticky; top:0; z-index:2; }
    h1 { margin:0; font-size: 18px; letter-spacing: 1px; }
    .panel { padding: 16px 24px; }
    button { background:#6fffe9; color:#0b132b; border:none; border-radius:10px; padding:10px 14px; font-weight:700; cursor:pointer; box-shadow: 0 8px 20px rgba(111,255,233,0.4); }
    button:hover { transform: translateY(-1px); }
    .grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(150px,1fr)); gap:12px; transition: height 0.3s ease, opacity 0.3s ease; }
    .card { background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%); border:1px solid rgba(111,255,233,0.3); border-radius:14px; padding:12px; box-shadow: 0 10px 25px rgba(0,0,0,0.35); cursor:pointer; }
    .card:hover { border-color:#6fffe9; }
    .emoji { font-size:32px; }
    .duo { display:flex; gap:6px; align-items:center; }
    .name { margin-top:6px; font-weight:700; }
    .muted { color:#9fb3c8; font-size:11px; margin-top:4px; }
    .arcade-label { font-weight:900; font-size:13px; letter-spacing:1px; color:#6fffe9; text-transform:uppercase; text-shadow: 1px 1px 0 #0b132b, 2px 2px 0 #0b132b; }
    .hidden { opacity:0; pointer-events:none; transition: opacity 0.25s ease; }
    #bio { margin-top:16px; background: rgba(255,255,255,0.05); border:1px solid rgba(111,255,233,0.3); border-radius:12px; padding:14px; min-height:140px; position:relative; }
    #floorplan { margin-top:16px; padding:14px; background: rgba(255,255,255,0.04); border:1px solid rgba(111,255,233,0.25); border-radius:12px; }
    .town { display:flex; justify-content:center; gap:10px; min-height:130px; align-items:center; flex-wrap:wrap; padding:8px 0; transition: min-height 0.25s ease, max-height 0.25s ease; }
    .tile { width:150px; height:80px; background: linear-gradient(135deg, #0f1f3a 0%, #16294d 100%); border:1px dashed rgba(111,255,233,0.4); border-radius:10px; padding:10px; text-align:center; color:#f8f9ff; display:flex; flex-direction:column; align-items:center; justify-content:center; box-sizing:border-box; }
    .tile .emoji { font-size:24px; }
    .faded { opacity: 0.35; transition: opacity 0.25s ease; pointer-events: none; }
    .placeholder { border:1px dashed rgba(111,255,233,0.3); background: rgba(255,255,255,0.02); color:#9fb3c8; }
    .centered { display:flex; flex-direction:column; align-items:center; text-align:center; }
    #restart { background: transparent; box-shadow:none; color:#6fffe9; border:1px solid rgba(111,255,233,0.5); border-radius:8px; height:28px; display:none; align-items:center; justify-content:center; padding:0 8px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px; gap:4px; }
    #restart:hover { transform:none; box-shadow: none; }
    /* Floorplan */
    #floorplan-map { margin-top:12px; background: rgba(255,255,255,0.04); border:1px solid rgba(111,255,233,0.25); border-radius:12px; padding:12px; display:none; }
    #map-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; }
    .cell { position:relative; border:1px dashed rgba(111,255,233,0.3); border-radius:10px; min-height:120px; padding:8px; color:#9fb3c8; box-sizing:border-box; }
    .cell-label { font-size:12px; margin-bottom:6px; font-weight:700; color:#6fffe9; }
    .children { font-size:11px; line-height:1.4; color:#b8c7d9; }
    .token-tray { display:flex; flex-wrap:wrap; gap:6px; justify-content:flex-end; margin-top:auto; }
    .cell { display:flex; flex-direction:column; gap:8px; }
    .token { padding:6px 10px; border-radius:999px; font-size:11px; color:#0b132b; font-weight:700; background:#6fffe9; box-shadow: 0 6px 14px rgba(0,0,0,0.15); }
    .sim-config { margin-top:10px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; color:#9fb3c8; font-size:12px; }
    .sim-config label { display:flex; align-items:center; gap:6px; }
    .sim-config input { background:rgba(255,255,255,0.06); border:1px solid rgba(111,255,233,0.3); border-radius:8px; color:#f8f9ff; padding:6px 8px; font-size:12px; }
    .sim-slider { width:200px; accent-color:#6fffe9; }
    #session-log { margin-top:12px; background: rgba(255,255,255,0.04); border:1px solid rgba(111,255,233,0.25); border-radius:12px; padding:12px; display:none; }
    #session-log pre { margin:0; max-height:260px; overflow-y:auto; white-space:pre-wrap; color:#cdd7e5; font-size:12px; }
  </style>
</head>
<body>
  <header><h1>Driftville</h1></header>
  <div class="panel">
    <div class="grid" id="grid"></div>

    <div id="floorplan">
      <div id="floor-top" class="centered" style="position:relative;">
        <button id="restart" title="Restart" style="position:absolute; left:0; top:-6px;">← RESTART</button>
        <div class="muted arcade-label" id="town-label" style="margin-bottom:6px; text-align:center;">Select one persona</div>
      </div>
      <div class="town" id="town"></div>
      <div id="floor-bottom" style="margin-top:10px; margin-bottom:12px; display:flex; justify-content:center;">
        <button id="simulate" style="min-width:220px; margin-bottom:8px;">Simulate distractions</button>
      </div>
      <div class="sim-config">
        <label>Start (UTC)
          <input id="date-input" type="datetime-local" value="2023-02-13T14:00">
        </label>
        <label>Ticks
          <input id="ticks-input" type="number" min="1" max="100" value="4" style="width:70px;">
        </label>
        <span style="color:#ffd166;">15-minute steps</span>
        <label id="time-wrapper">Time
          <input id="time-slider" class="sim-slider" type="range" min="0" max="1440" step="15" value="840">
        </label>
        <span id="time-display" style="font-weight:700; color:#6fffe9;">14:00</span>
      </div>
      <div id="floorplan-map">
        <div class="muted" style="margin-bottom:6px;">Driftville Town</div>
        <div id="map-grid"></div>
      </div>
    </div>

    <div id="bio">
      <div id="bio-content">Select a persona to see their bio.</div>
    </div>

    <div id="session-log">
      <div class="muted" style="margin-bottom:6px;">Session Log (latest)</div>
      <pre id="session-log-body"></pre>
    </div>
  </div>

  <script>
    const personas = {{ personas | tojson }};
    const emojiMap = {{ emoji_map | tojson }};
    const faceMap = {{ face_map | tojson }};
    const personaByName = Object.fromEntries(personas.map(p => [p.name, p]));
    const scheduleByName = Object.fromEntries(personas.map(p => [p.name, p.schedule || []]));
    const grid = document.getElementById("grid");
    const bioContent = document.getElementById("bio-content");
    const town = document.getElementById("town");
    const townLabel = document.getElementById("town-label");
    const floorTop = document.getElementById("floor-top");
    const floorBottom = document.getElementById("floor-bottom");
    const simBtn = document.getElementById("simulate");
    const timeWrapper = document.getElementById("time-wrapper");
    const restartBtn = document.getElementById("restart");
    const ticksInput = document.getElementById("ticks-input");
    const dateInput = document.getElementById("date-input");
    const timeSlider = document.getElementById("time-slider");
    const timeDisplay = document.getElementById("time-display");
    const chosen = []; // names added to Driftville (max 1 for ORPDA loop)
    let simLocked = false;
    const floorplanMap = document.getElementById("floorplan-map");
    const mapGrid = document.getElementById("map-grid");
    const sessionLogPanel = document.getElementById("session-log");
    const sessionLogBody = document.getElementById("session-log-body");
    const setRestartVisible = (show) => {
      if (restartBtn) restartBtn.style.display = show ? "inline-block" : "none";
      if (timeWrapper) timeWrapper.style.display = show ? "none" : "";
    };
    let mapLayout = [];
    let mapIds = new Set();

    function rebuildMapFromSelection() {
      const tree = {};
      const addLoc = (loc) => {
        if (!loc) return;
        const [parent, child] = loc.split(":");
        if (!tree[parent]) tree[parent] = new Set();
        if (child) tree[parent].add(child.replace(/_/g, " "));
      };
      if (chosen.length === 0) {
        addLoc("home");
      } else {
        chosen.forEach(name => {
          (scheduleByName[name] || []).forEach(slot => addLoc(slot.location || "home"));
        });
      }
      // ensure at least one row
      if (Object.keys(tree).length === 0) addLoc("home");

      mapLayout = Object.keys(tree).map(parent => ({
        id: parent,
        label: parent.replace(/_/g, " "),
        children: Array.from(tree[parent]),
      }));
      mapIds = new Set(mapLayout.map(c => c.id));
      buildMap();
      refreshMap();
    }

    function buildMap() {
      mapGrid.innerHTML = "";
      mapLayout.forEach(cell => {
        const div = document.createElement("div");
        div.className = "cell";
        div.dataset.cellId = cell.id;
        const children = (cell.children || []).map(c => `<span>${c}</span>`).join(" · ");
        div.innerHTML = `<div class="cell-label">${cell.label}</div><div class="children">${children}</div><div class="token-tray"></div>`;
        mapGrid.appendChild(div);
      });
    }

    function placeTokens(assignments) {
      mapLayout.forEach(cell => {
        const target = mapGrid.querySelector(`[data-cell-id="${cell.id}"]`);
        if (!target) return;
        const tray = target.querySelector(".token-tray") || target;
        // remove old tokens
        tray.querySelectorAll(".token").forEach(t => t.remove());
        const list = assignments[cell.id] || [];
        list.forEach((name, idx) => {
          const tok = document.createElement("div");
          tok.className = "token";
          tok.style.background = idx % 2 === 0 ? "#6fffe9" : "#ffd166";
          const icon = faceMap[name] || emojiMap[name] || "🧩";
          tok.textContent = `${icon} ${name.split(" ")[0] || name}`;
          tray.appendChild(tok);
        });
      });
    }

    let simMinute = 14 * 60; // default 14:00
    const minutesToStr = (mins) => {
      const h = Math.floor((mins || 0) / 60) % 24;
      const m = (mins || 0) % 60;
      return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
    };
    const updateSimTimeDisplay = () => {
      if (timeDisplay) timeDisplay.textContent = minutesToStr(simMinute);
      if (timeSlider) timeSlider.value = simMinute;
    };
    const minutesNow = () => simMinute;
    const currentLocationFor = (name, minute) => {
      const sched = scheduleByName[name] || [];
      const slot = sched.find(s => minute >= (s.start_time ?? 0) && minute < (s.end_time ?? 0));
      if (slot && slot.location) return slot.location;
      const route = guessRoute(name);
      return route[0] || "home";
    };
    const buildAssignmentsAt = (minute) => {
      if (chosen.length === 0) return {};
      const assignments = {};
      chosen.forEach(name => {
        const persona = personaByName[name];
        if (!persona) return;
        const loc = currentLocationFor(name, minute);
        let cell = (loc || "home").split(":")[0];
        if (!mapIds.has(cell)) cell = "outdoor";
        if (!assignments[cell]) assignments[cell] = [];
        assignments[cell].push(name);
      });
      return assignments;
    };

    function refreshMap() {
      placeTokens(buildAssignmentsAt(minutesNow()));
    }

    function guessRoute(name) {
      const persona = personas.find(x => x.name === name) || {};
      const text = (persona.raw_persona || "").toLowerCase();
      const route = [];
      const pushIf = (key, id) => { if (text.includes(key)) route.push(id); };
      pushIf("home", "home");
      pushIf("cafe", "Hobbs_Cafe");
      pushIf("hobbs", "Hobbs_Cafe");
      pushIf("market", "Willow_Market_and_Pharmacy");
      pushIf("pharmacy", "Willow_Market_and_Pharmacy");
      pushIf("college", "Oak_Hill_College");
      pushIf("park", "Johnson_Park");
      pushIf("studio", "art_studio");
      pushIf("writer", "writer_desk");
      pushIf("classroom", "Oak_Hill_College");
      if (route.length === 0) route.push("home", "office");
      return route.slice(0, 4);
    }
    function renderTown(message = "") {
      town.innerHTML = "";
      chosen.forEach(name => {
        const tile = document.createElement("div");
        tile.className = "tile";
        const prof = emojiMap[name] || "🧩";
        tile.innerHTML = `<div class="emoji">${prof}</div><div style="font-size:11px; margin-top:4px;">${name}</div>`;
        tile.onclick = () => {
          if (simLocked) return;
          const idx = chosen.indexOf(name);
          if (idx >= 0) {
            chosen.splice(idx, 1);
            renderTown();
          }
        };
        town.appendChild(tile);
      });
      // add empty placeholders up to 1 slot
      for (let i = chosen.length; i < 1; i++) {
        const ph = document.createElement("div");
        ph.className = "tile placeholder";
        ph.innerHTML = `<div style="font-size:12px;">Empty slot</div>`;
        town.appendChild(ph);
      }
      if (message) {
        townLabel.textContent = message;
      } else {
        townLabel.textContent = chosen.length < 1 ? "Select one persona" : "Ready to simulate ORPDA";
      }
      rebuildMapFromSelection();
    }

    personas.forEach(p => {
      const card = document.createElement("div");
      card.className = "card";
      const prof = emojiMap[p.name] || "🧩";
      card.innerHTML = `
        <div class="emoji">${prof}</div>
        <div class="name">${p.name}</div>
        <div class="muted">view bio</div>
      `;
      card.onclick = () => {
        if (simLocked) return;
        bioContent.innerHTML = `
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <div class="emoji" style="font-size:28px;">${emojiMap[p.name] || "🧩"}</div>
            <div style="font-weight:700;">${p.name}</div>
          </div>
          <div style="white-space:pre-wrap; line-height:1.5;">${(p.raw_persona || "").replace(/\\n/g,"\\n")}</div>
        `;
        const idx = chosen.indexOf(p.name);
        if (idx >= 0) {
          chosen.splice(idx, 1);
        } else if (chosen.length < 1) {
          chosen.push(p.name);
        } else {
          alert("Only one persona at a time for ORPDA loop. Click the selected tile below to remove.");
          renderTown("Only one persona at a time");
          return;
        }
        renderTown();
      };
      grid.appendChild(card);
    });
    // initial placeholders
    renderTown();
    rebuildMapFromSelection();
    updateSimTimeDisplay();
    setInterval(refreshMap, 1000 * 30); // update positions every 30s
    if (timeSlider) {
      timeSlider.oninput = (e) => {
        simMinute = parseInt(e.target.value, 10) || 0;
        updateSimTimeDisplay();
        refreshMap();
      };
    }

    simBtn.onclick = () => {
      if (chosen.length < 1) {
        bioContent.textContent = "Select a persona to run their ORPDA loop.";
        return;
      }
      const [a] = chosen; // single persona
      bioContent.innerHTML = `<strong>Simulating ORPDA</strong> for ${a}...`;
      floorTop.classList.add("faded");
      floorBottom.classList.add("faded");
      grid.classList.add("hidden");
      grid.style.height = "0px";
      grid.style.opacity = "0";
      grid.style.pointerEvents = "none";
      simBtn.style.display = "none";
      setRestartVisible(true);
      if (floorplanMap) floorplanMap.style.display = "block";
      townLabel.textContent = "Welcome to Driftville!";
      town.style.minHeight = "60px";
      town.style.maxHeight = "60px";
      simLocked = true;
      let steps = 1;
      if (ticksInput) {
        const parsed = parseInt(ticksInput.value, 10);
        if (Number.isFinite(parsed)) steps = Math.max(1, Math.min(100, parsed));
      }
      let simStart = "2023-02-13 14:00";
      if (dateInput && dateInput.value) {
        simStart = dateInput.value.replace("T", " ");
      };
    };

    restartBtn.onclick = () => {
      // simple reload/reset of selections and UI
      chosen.splice(0, chosen.length);
      renderTown();
      bioContent.textContent = "Select a persona to see their bio.";
      setRestartVisible(false);
      if (floorplanMap) floorplanMap.style.display = "none";
      grid.classList.remove("hidden");
      grid.style.height = "";
      grid.style.opacity = "1";
      grid.style.pointerEvents = "auto";
      simBtn.style.display = "inline-block";
      floorTop.classList.remove("faded");
      floorBottom.classList.remove("faded");
      townLabel.textContent = chosen.length < 1 ? "Select one persona" : "Ready to simulate ORPDA";
      town.style.minHeight = "130px";
      town.style.maxHeight = "130px";
      simLocked = false;
      if (sessionLogPanel) sessionLogPanel.style.display = "none";
      if (sessionLogBody) sessionLogBody.textContent = "";
      sessionLogJsonl = [];
    };
  </script>
</body>
</html>
"""


@APP.route("/")
def home():
    return render_template_string(
        HTML, personas=PERSONAS, emoji_map=EMOJI_MAP, face_map=FACE_MAP
    )


@APP.post("/simulate_agents")
def simulate_agents():
    """
    Kick off backend ORPDA simulation (app/src/simulate.py) with selected agents.
    Payload: { "agents": ["Name1"], "sim_start": "YYYY-MM-DD HH:MM", "steps": 1 }
    """
    try:
        body = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    agents = body.get("agents") or []
    sim_start = body.get("sim_start")  # optional
    steps = body.get("steps") or 1

    if not agents:
        return jsonify({"error": "agents list required"}), 400

    repo_root = Path(__file__).resolve().parent.parent
    sim_path = repo_root / "app/src/simulate.py"
    cmd = [
        "python",
        str(sim_path),
        "--agents",
        ",".join(agents),
        "--steps",
        str(steps),
    ]
    if sim_start:
        cmd += ["--sim-start", sim_start]

    # Run simulate.py
    try:
        env = dict(**os.environ)
        # ensure project root on PYTHONPATH for app.src imports
        env["PYTHONPATH"] = env.get("PYTHONPATH", str(repo_root))
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
    except Exception as e:
        return jsonify({"error": f"Failed to run simulate.py: {e}"}), 500

    # Grab latest session log if present
    session_log_jsonl = []
    session_log_path = None
    try:
        log_dir = repo_root / "app/logs"
        candidates = sorted(
            log_dir.glob("session_*.jsonl"), key=lambda p: p.stat().st_mtime
        )
        if candidates:
            session_log_path = candidates[-1]
            with session_log_path.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        session_log_jsonl.append(json.loads(line))
                    except Exception:
                        continue
    except Exception:
        session_log_jsonl = []

    status = proc.returncode
    result = {
        "status": "ok" if status == 0 else "error",
        "returncode": status,
        "stdout_tail": (proc.stdout or "").splitlines()[-20:],
        "stderr_tail": (proc.stderr or "").splitlines()[-20:],
        "logs": {
            "memory_streams": str(repo_root / "app/logs/memory_streams.log"),
            "events": str(repo_root / "app/logs/events.log"),
            "trace": str(repo_root / "app/logs/trace.log"),
        },
        "session_log_path": str(session_log_path) if session_log_path else None,
        "session_log_jsonl": session_log_jsonl,  # full log, not just tail
    }
    return jsonify(result), (200 if status == 0 else 500)


@APP.get("/session_log/latest")
def latest_session_log():
    repo_root = Path(__file__).resolve().parent.parent
    log_dir = repo_root / "app/logs"
    agent_filter = request.args.get("agent")
    session_log_jsonl = []
    session_log_path = None
    try:
        candidates = sorted(
            log_dir.glob("session_*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for path in candidates:
            entries = []
            try:
                with path.open("r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entries.append(json.loads(line))
                        except Exception:
                            continue
            except Exception:
                continue
            if agent_filter:
                if not any(
                    (e.get("agent") or "").lower() == agent_filter.lower()
                    for e in entries
                ):
                    continue
            session_log_jsonl = entries
            session_log_path = path
            break
    except Exception:
        session_log_jsonl = []

    return jsonify(
        {
            "session_log_path": str(session_log_path) if session_log_path else None,
            "session_log_jsonl": session_log_jsonl,
        }
    )


if __name__ == "__main__":
    APP.run(debug=True)
