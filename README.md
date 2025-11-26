# Writeups

**Components required for agent coherence:**

- matable memory system: events, actions, reflections, plans (`memory.jsonl`)
    - id
    - ts_created: creation timestamp
    - ts_last_accessed: most recent access timestampt
    - importance: importance score assigned by LLM
    - text: natural language description

- immutable event logs (audit log): full diaglogues input/output (`event_logs.jsonl`)

**Retrieval**
The memory retrieval model then uses the recency, importance, and relevance scores (which depend on the timestamps and importance score) to dynamically retrieve a subset of these memories to inform the agent's behavior. Informs agent's moment-to-moment behaviour like the original RPG town paper.

- recenty
- importance
- relevance


**Rate Limit**
A few practical ways to stay under the Gemini rate limits:

- Throttle between turns: Add a fixed sleep (e.g., 3–6s) after each turn generation and after each importance/summarize call. Also cap concurrent requests with an asyncio.Semaphore(1 or 2) so we don’t burst.

- Backoff using retry hints: When we catch 429/503, read the retryDelay if present, await sleep(retry_delay + jitter), then retry once. Fall back to a no-op if it still fails.

- Cut call volume: Fewer turns per convo (lower MAX_TURNS), skip wants_to_speak LLM calls by using a simple probabilistic rule, and cache/reuse importance scores instead of scoring every conversation. Summarize only every N conversations.

- Batch logging: Log memories once per conversation, not per turn (we partly doing this); avoid scoring empty/short snippets.

- Use lighter model / higher quota: If possible, switch to a lower-load model (e.g., flash-lite) or upgrade to a paid tier for higher limits.

- Pre-generate or mock in tests: When developing, stub turn generation/scoring to avoid burning quota.

- Combine throttling + jittered backoff to smooth bursts and greatly reduce 429s.




**LLM call duplication**
Skip duplicate summarize/log calls
In conversation_manager.store_turns, you already create summary_text and pass it as summary_override to run_and_log. Make sure run_and_log doesn’t re-summarize. If summary_override is provided, pass it straight to log_conv_memory and skip summarize_dialogue.

Stop re-asking to summarize in the console
Those repeated “Summarize this…” prompts appear because you’re calling run_and_log after generating the prompt text itself. When logging, pass only the finalized summary string; don’t re-run the summarization on the raw dialogue prompt. If you still see multiple “Summarize this…” entries, ensure there’s only one run_and_log call per conversation.

Throttle calls
Add a small sleep between turns/conversations (e.g., await asyncio.sleep(2) inside your loop) and lower MAX_TURNS (e.g., 3–4). This reduces 429s and duplicate sessions.

Don’t call wants_to_speak with the LLM each turn
Use a simple heuristic (random yes with, say, 60–70% chance) or only ask once per conversation, then reuse the answer for subsequent turns.

Deduplicate before logging
In store_turns, if the same dialogue text shows up (same speaker/text pairs), skip logging.

Use cosine relevance safely
Already fixed recent_text to avoid None; keep the prompt short by truncating history to last few lines (you already do history[-6:]).

If you want me to implement these now, I can:

Replace LLM wants_to_speak with a heuristic.
Add a 2s sleep per turn and set MAX_TURNS = 3.
Ensure run_and_log never calls summarize_dialogue when summary_override is given.
Add a short-circuit dedupe in store_turns when the dialogue didn’t change.

