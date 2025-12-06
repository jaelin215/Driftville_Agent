def deterministic_observe(context: dict) -> dict:
    """
    Replace the LLM observer.
    Extracts structured fields directly from context without hallucination.
    """
    slot = context.get("current_slot", {})
    last = context.get("last_action_result", None)

    # fallback if missing fields
    dt = slot.get("datetime_start") or context.get("current_datetime")

    return {
        "observation": {
            "datetime_start": dt,
            "duration_min": slot.get("duration_min", 15),
            "location": slot.get("location", "unknown"),
            "action": slot.get("action", "unknown"),
            # NEW: pass-through inputs, untouched
            "environment": context.get("environment", {}),
            "recent_memory": context.get("recent_memory", []),
            "state_summary": slot.get("state_summary", ""),
        }
    }
