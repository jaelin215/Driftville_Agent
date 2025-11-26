# app/src/brain.py
# single place for LLM helpers

import asyncio
import datetime
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.runners import InMemoryRunner

from config.config import MODEL_NAME

# serialize LLM requests to avoid bursts / rate hits
_llm_semaphore = asyncio.Semaphore(1)

load_dotenv()

# -----------------------------------------*
# Config
# -----------------------------------------*
ROOT = Path.cwd()
MEMORY_PATH = ROOT / "app/logs/memory.jsonl"
EVENT_LOG_PATH = ROOT / "app/logs/event_logs.jsonl"

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)


# -----------------------------------------*
# Utils
# -----------------------------------------*
def calc_recency_score(last_accessed_date=None, decay_factor=0.995):
    if last_accessed_date is None:
        last_accessed_date = datetime.date.today()
    days_since = (datetime.date.today() - last_accessed_date).days
    score = decay_factor ** max(days_since, 0)
    return days_since, score


def log_conv_memory(
    author: str, participants: List[str], summary: str, score: int | float
):
    """the core components of a Memory Stream object, including the natural language description (text)
    and the LLM-generated Importance score [i, 45, 47, 48]

    1. Direct LLM output: Importance score is calculated and stored
    at the time the memory object (the observation) is created [i, 48].
    2. Permanent Storage: This Importance score is then stored permanently
    as part of the memory object in the Memory Stream [i, 45, 48].

    This design means the Importance calculation is not re-run per retrieval prompt;
    it only happens once when the memory is first logged
    """
    entry = {
        "ts_created": datetime.datetime.today().isoformat() + "Z",
        "ts_last_accessed": datetime.datetime.today().isoformat() + "Z",
        "importance": score,
        "type": "conversation",
        "participants": participants,
        "text": summary,
    }
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def load_history(participants, log_path=EVENT_LOG_PATH):
    """Return list of conversation events matching all participants."""
    want = set(participants)
    matches = []
    if not log_path.exists():
        return matches
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                parts = set(obj.get("participants", []))
                if want.issubset(parts):
                    matches.append(obj)
            except Exception:
                continue
    return matches


# -----------------------------------------*
# Safe generation helper
# -----------------------------------------*
async def safe_generate(fn, *args, retries=2, base_delay=2.0, **kwargs):
    for attempt in range(retries + 1):
        try:
            return await fn(*args, **kwargs)
        except Exception:
            if attempt == retries:
                return None
            await asyncio.sleep(base_delay * (2**attempt))
    return None


# -----------------------------------------*
# Agents
# -----------------------------------------*
importance_agent = LlmAgent(
    name="importance_agent",
    model=Gemini(model=MODEL_NAME, retry_config=retry_config),
    instruction="""Output scale by rating the input on a scale of 1 to 10 as integer, 
    where 1 is "purely mundane" (e.g., brushing teeth) and 10 is "extremely poignant" (e.g., a breakup)
    """,
)

turn_agent = LlmAgent(
    name="turn_agent",
    model=Gemini(model=MODEL_NAME, retry_config=retry_config),
    instruction="Given context, history, and memories, produce ONE short in-character line for the speaker.",
)

summary_agent = LlmAgent(
    name="summary_agent",
    model=Gemini(model=MODEL_NAME, retry_config=retry_config),
    instruction="Summarize observations into a concise one- or two-sentence memory for later recall.",
)


# -----------------------------------------*
# Turn generation
# -----------------------------------------*
def _relevant_memories(
    agent, other_name: str | None, context: str | None, limit: int = 3
):
    mems = getattr(agent, "memory", None) or []
    lower_other = (other_name or "").lower()
    lower_ctx = (context or "").lower()
    query = " ".join(x for x in [lower_other, lower_ctx] if x).strip()

    def cosine_overlap(a: str, b: str) -> float:
        """Lightweight cosine similarity on bag-of-words."""
        if not a or not b:
            return 0.0

        def to_counts(s):
            counts = {}
            for w in s.split():
                counts[w] = counts.get(w, 0) + 1
            return counts

        ca, cb = to_counts(a), to_counts(b)
        if not ca or not cb:
            return 0.0
        dot = sum(ca.get(w, 0) * cb.get(w, 0) for w in ca)
        na = sum(v * v for v in ca.values()) ** 0.5
        nb = sum(v * v for v in cb.values()) ** 0.5
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def recency_score(ts: str):
        try:
            dt = datetime.datetime.fromisoformat(ts.replace("Z", ""))
            days = (datetime.datetime.now() - dt).days
            return max(0.0, 1.0 - min(days / 30.0, 1.0))
        except Exception:
            return 0.5

    scored = []
    for m in mems:
        text = (m.get("text") or "").lower()
        importance = float(m.get("importance", 0)) / 10.0
        rec = recency_score(m.get("ts_last_accessed", "ts_created"))
        relevance = cosine_overlap(query, text) if query else 0.0
        score = (importance * 0.4) + (rec * 0.3) + (relevance * 0.3)
        scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:limit]]


async def generate_turn_line(speaker, listener, context, history, observation=None):
    """Generate one line of dialogue for the speaker using memory/context/history."""
    recent = _relevant_memories(speaker, listener.name if listener else None, context)
    recent_text = (
        " ".join((r.get("text") or "") for r in recent).strip() if recent else "None"
    )
    last_line = history[-1]["text"] if history else ""
    short_history = "\n".join(
        f"{t.get('speaker')}: {t.get('text')}" for t in history[-6:]
    )

    summary = ""
    if isinstance(getattr(speaker, "personality", {}), dict):
        summary = speaker.personality
    prompt = f"""{speaker.name}'s personality: {summary or speaker.name}
Current Context: {context}
Observation: {observation or last_line or "N/A"}
Relevant Memory Summary: {recent_text}
Recent Dialogue:
{short_history or "None"}
Action: Respond naturally in character to continue the dialogue with {listener.name if listener else "other party"}, building on the latest turn.
Reply with only {speaker.name}'s next line (no listener line)."""

    async with _llm_semaphore:
        async with InMemoryRunner(agent=turn_agent) as runner:
            events = await safe_generate(runner.run_debug, prompt, verbose=False)
        if not events:
            return None
        text = None
        for ev in events:
            if getattr(ev.content, "parts", None):
                for part in ev.content.parts:
                    if getattr(part, "text", None):
                        text = part.text.strip()
                        break
            if text:
                break
        if not text:
            return None
        line = text.split("\\n")[0]
        if ":" in line:
            line = line.split(":", 1)[1].strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1].strip()
        return {"speaker": speaker.name, "text": line}


# -----------------------------------------*
# Run agents
# -----------------------------------------*
async def run_and_log(
    author: str,
    participants: List[str],
    dialogue: str,
    runner: InMemoryRunner,
    summary_override: str | None = None,
):
    async with _llm_semaphore:
        events = await runner.run_debug(dialogue, verbose=False)
    score = None
    for ev in events:
        if getattr(ev.content, "parts", None):
            for part in ev.content.parts:
                if getattr(part, "text", None) and part.text.strip().isdigit():
                    score = int(part.text.strip())
                    break
    if score is not None:
        summary = (
            summary_override
            if summary_override is not None
            else await summarize_dialogue(dialogue)
        )
        log_conv_memory(author, participants, summary, score)
    return events, score


async def summarize_dialogue(text: str):
    """Use summary_agent to condense dialogue into a short memory entry."""
    if not text or not text.strip():
        return None
    async with _llm_semaphore:
        async with InMemoryRunner(agent=summary_agent) as runner:
            events = await safe_generate(
                runner.run_debug,
                f"Summarize this into one or two sentences capturing key facts: {text}",
                verbose=False,
            )
        if not events:
            return None
        for ev in events:
            if getattr(ev.content, "parts", None):
                for part in ev.content.parts:
                    if getattr(part, "text", None):
                        return part.text.strip()
    return None


if __name__ == "__main__":
    days, recency = calc_recency_score(datetime.date(2025, 11, 20))
    print(f"Days since: {days}, recency score: {recency:.4f}")
    history = load_history(["Sam", "Jaelin"])
    print(f"Loaded {len(history)} conversations between two agents")

    from agents import jaelin, maxime, sam, lily

    print("agents loaded")

    async def test():
        await generate_turn_line(jaelin, sam, "Lunch", history)

    asyncio.run(test())
