def deterministic_observe(context: dict) -> dict:
    """
    Replace the LLM observer.
    Extracts structured fields directly from context without hallucination.
    """
    persona = context.get("persona", {}) or {}
    name = persona.get("name", "The person")

    slot = context.get("current_slot", {}) or {}
    last = context.get("last_action_result") or {}

    # fallback if missing fields
    dt = (
        last.get("next_datetime")
        or slot.get("datetime_start")
        or context.get("current_datetime")
    )
    duration = slot.get("duration_min", 15)
    location = last.get("location") or slot.get("location", "unknown")
    action = last.get("action") or slot.get("action", "unknown")

    state_summary = f"{name} is at {location} doing {action}."

    observation = {
        "datetime_start": dt,
        "duration_min": duration,
        "location": location,
        "action": action,
        # Pass-through inputs, untouched
        "environment_description": context.get(
            "environment_description", slot.get("environment_description", {})
        ),
        "recent_history": context.get("recent_history", []),
        "state_summary": slot.get("state_summary", state_summary),
    }

    # Return the full context plus the computed observation so downstream agents see everything.
    merged = dict(context)
    merged["observation"] = observation
    return merged
