# Driftville ORPDA Simulator

Persona-based ORPDA loop (Observe → Reflect → Plan → Drift → Act) with a small web UI and ablation metrics.

## Quick Start
1) Install deps (activate your env first: Enter your `GOOGLE_API_KEY` in .env ):
   pip install -r requirements.txt
2) Set model in `app/config/config.yaml` (e.g., gemini-2.5-flash-lite).
3) Run the FastAPI app (backend services):
   uvicorn app.app:app --reload
4) UI status: the Driftville page is visualization-only (no live ORPDA wiring yet). To preview the layout:
   python app2/app2.py
   # visit the printed URL (default http://127.0.0.1:5000)

## ORPDA Loop
- YAML agent configs live in `app/src/yaml/` (`root_agent.yaml`, `observer.yaml`, etc.).
- Programmatic runner: `app/src/orpda_runner.py` exposes `run_orpda_cycle(ctx)`; call with a context dict (raw persona, last_action_result, recent_history, current_datetime).

## Simulation CLI
- `app/src/simulate.py` runs a ticked ORPDA loop over personas in `app/src/driftville_personas.json`.
- Run with package import safety:
   python -m app.src.simulate
- To control start time (after adding the argparse flag as needed), pass `--sim-start "YYYY-MM-DD HH:MM"`.

## Logs
- Session logs: `app/logs/session_*.log`
- Memory streams: `app/logs/memory_streams*.log`
- Trace/events: `app/logs/trace.log`, `app/logs/events.log`

## Metrics & Ablation
- `app/src/metrics.py` compares ORPDA (with drift) vs ORPA (no drift).
- Compute and plot:
   python -m app.src.metrics
- Outputs: `app/logs/metrics.json` and `app/logs/metrics_plot.png`.

## Personas
- Driftville schedules: `app/src/driftville_personas.json`
- Raw bios: `app/src/smallville_personas.json`
- UI persona loader (arcade-style): `app2/app2.py`

## Config
- Model selection: `app/config/config.yaml` (`MODEL_NAME` used by agents).
- Additional personas: add to `driftville_personas.json` with schedule blocks; raw bios can go into `smallville_personas.json`.

## Development Notes
- Keep `sys.path` setup at the top of scripts when running as plain Python (`Path(__file__).resolve().parents[2]`).
- Avoid hard resets; logs are useful for debugging.
