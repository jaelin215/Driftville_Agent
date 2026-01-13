# app/src/gemini_api.py
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

from dotenv import load_dotenv
from google import genai

# Paths
ROOT = Path(__file__).resolve().parents[1]
# print(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config.config import MODEL_NAME

load_dotenv()
# Prefer GEMINI_API_KEY; fall back to GOOGLE_API_KEY.
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Missing API key: set GEMINI_API_KEY or GOOGLE_API_KEY in your environment/.env"
    )
client = genai.Client(api_key=API_KEY)


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


async def call_gemini(prompt, model=None, timeout_sec: float = 30):
    """Call Gemini with rate limiting; if model is None, uses MODEL_NAME."""
    await rate_limiter.acquire()

    try:
        # Note: some client versions don't accept request_options. To avoid breaking,
        # we pass only required params.
        response = client.models.generate_content(
            model=model or MODEL_NAME,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"  [Gemini API error: {e}]")
        return "Error generating response"
