# app/src/llm_api.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Gemini client wrapper with rate limiting for agent calls.
# --------------------------------------
import asyncio
import os
import sys
import time
from collections import deque
from pathlib import Path

import litellm
from dotenv import load_dotenv
from google import genai
from app.config.config import MODELS_CONFIG, MODEL_NAME, MODEL_TEMPERATURE, PROVIDER, normalize_model_id

# Paths
ROOT = Path(__file__).resolve().parents[1]
# print(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


load_dotenv()

# Set keys for the providers from .env.
litellm.openai_api_key = os.getenv("OPENAI_API_KEY")
litellm.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
litellm.google_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Optional: To disable verbose logging from litellm
litellm.set_verbose = False

# # Prefer GEMINI_API_KEY; fall back to GOOGLE_API_KEY.
# API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     raise RuntimeError(
#         "Missing API key: set GEMINI_API_KEY or GOOGLE_API_KEY in your environment/.env"
#     )
# client = genai.Client(api_key=API_KEY)


class RateLimiter:
    def __init__(self, calls_per_minute=15):
        """Track timestamps to cap outbound calls per minute."""
        self.rate = calls_per_minute
        self.calls = deque()

    async def acquire(self):
        """Sleep if needed so calls stay within the per-minute quota."""
        now = time.time()
        # Remove calls older than 1 minute
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()

        if len(self.calls) >= self.rate:
            wait_time = 60 - (now - self.calls[0])
            print(f"  [Rate limit: waiting {wait_time:.1f}s]")
            await asyncio.sleep(wait_time + 0.1)

        self.calls.append(time.time())


rate_limiter = RateLimiter(calls_per_minute=15)




async def call_llm(prompt, model=None, timeout_sec: float = 30, temperature=None):
    """Call any LLM using litellm with rate limiting."""
    await rate_limiter.acquire()

    # Look up model configuration by logical name (e.g. 'default' or 'gemini')
    model_key = model or 'default'
    model_config = MODELS_CONFIG.get(model_key, {})

    # Get model name and temperature from config, with fallbacks
    final_model_name = model_config.get("name", model or MODEL_NAME)
    final_temperature = model_config.get(
        temperature
        if temperature is not None
        else model_config.get("temperature", MODEL_TEMPERATURE)
    )

    try:
        # Use litellm's async completion function.
        messages = [{"content": prompt, "role": "user"}]
        response = await litellm.acompletion(
            model=final_model_name,
            messages=messages,
            timeout=timeout_sec,
            temperature=final_temperature,
        )
        return response.choices[0].messages.content
    except Exception as e:
        print(f"  [LLM API error: {e}]")
        return "Error generating response"
