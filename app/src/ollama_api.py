# app/src/ollama_api.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Ollama client wrapper with rate limiting for agent calls.
# --------------------------------------
import asyncio
import os
import sys
import time
from collections import deque
from pathlib import Path

from dotenv import load_dotenv
from ollama import Client

# Paths
ROOT = Path(__file__).resolve().parents[2]
print(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config.config import MODEL_NAME, MODEL_TEMPERATURE

load_dotenv()


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
            wait_time = 60*15 - (now - self.calls[0])
            print(f"  [Rate limit: waiting {wait_time:.1f}s]")
            await asyncio.sleep(wait_time + 0.1)

        self.calls.append(time.time())


rate_limiter = RateLimiter(calls_per_minute=15)


async def call_ollama(prompt, model=None, temperature=None, use_stream=False):
    """Call any LLM using Ollama with rate limiting."""
    await rate_limiter.acquire()

    # Get model name and temperature from config, with fallbacks
    final_model_name = model or MODEL_NAME
    final_temperature = temperature or MODEL_TEMPERATURE
    start_time = time.time()
    api_key = os.getenv("OLLAMA_API_KEY")
    # For Ollama cloud service, embed API key in the host URL
    host = f"https://ollama-api:{api_key}@api.ollama.com"
    client = Client(host=host)

    try:
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]

        if use_stream:
            response = ""
            for part in client.chat(
                final_model_name,
                messages=messages,
                stream=use_stream,
                options={"temperature": final_temperature},
            ):
                chunk = part["message"]["content"]
                response += chunk
                # print(chunk, end="", flush=True)
            print()  # New line after streaming

        else:
            response = client.chat(
                final_model_name,
                messages=messages,
                stream=use_stream,
                options={"temperature": final_temperature},
            )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\nResponse time: {elapsed_time:.2f} seconds")

        if use_stream:
            return response
        else:
            return response["message"]["content"]

    except Exception as e:
        print(f"  [LLM API error: {e}]")
        return "Error generating response"


if __name__ == "__main__":
    # async def test_temperature():
    #     prompt = "Write a unique 3-sentence story about a blue cat."

    #     print("--- TESTING TEMP 0.0 ---")
    #     res1 = await call_ollama(prompt, temperature=0.0)
    #     res2 = await call_ollama(prompt, temperature=0.0)
    #     print(f"Match: {res1 == res2}")  # MUST be True

    #     print("\n--- TESTING TEMP 1.0 ---")
    #     res3 = await call_ollama(prompt, temperature=1.0)
    #     res4 = await call_ollama(prompt, temperature=1.0)
    #     print(f"Match: {res3 == res4}")  # SHOULD be False
    # asyncio.run(test_temperature())

    # async def test_entropy():
    #     words_temp_0 = []
    #     words_temp_1 = []
    #     prompt = "Give me one random noun. Only the word."

    #     for _ in range(5):
    #         words_temp_0.append(await call_ollama(prompt, temperature=0.0))
    #         words_temp_1.append(await call_ollama(prompt, temperature=1.0))

    #     print(f"Temp 0.0 words: {set(words_temp_0)}")  # Should have 1 unique word
    #     print(
    #         f"Temp 1.0 words: {set(words_temp_1)}"
    #     )  # Should have multiple unique words
    # asyncio.run(test_entropy())
    
    prompt = "hello. how are you?"
    response = asyncio.run(call_ollama(prompt=prompt, use_stream=True))
    print(response)
    print()
    print(MODEL_NAME, MODEL_TEMPERATURE)
