# gemini_api.py
from google import genai
import asyncio
import time
from collections import deque

import os, sys
from dotenv import load_dotenv
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
# print(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from config.config import MODEL_NAME

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


class RateLimiter:
    def __init__(self, calls_per_minute=15):
        self.rate = calls_per_minute
        self.calls = deque()

    async def acquire(self):
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


async def call_gemini(prompt):
    """Call Gemini with rate limiting"""
    await rate_limiter.acquire()

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"  [Gemini API error: {e}]")
        return "Error generating response"
