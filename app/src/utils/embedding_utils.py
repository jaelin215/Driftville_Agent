# app/src/embedding_utils.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Helpers for Gemini embeddings of text for drift/metrics analysis.
# --------------------------------------
import os
import sys
from pathlib import Path
from typing import List

try:
    from google import genai  # type: ignore
except ImportError:
    genai = None
from dotenv import load_dotenv
from langfuse import get_client, observe, propagate_attributes

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config.config import EMBEDDING_MODEL_NAME, MODEL_NAME

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY) if genai and GOOGLE_API_KEY else None
langfuse = get_client()

# Cost is $0.15 per 1,000,000 tokens -> $0.00015 per 1,000 tokens
EMBED_COST_PER_1K_TOKENS = float(os.getenv("EMBED_COST_PER_1K_TOKENS", "0.00015"))


def _estimate_embed_cost(tokens: int) -> float:
    """
    USD cost estimate for Gemini embeddings.
    Standard Rate: $0.15 / 1M tokens
    """
    return round((tokens / 1000) * EMBED_COST_PER_1K_TOKENS, 6)


@observe(as_type="embedding")
def embed_texts(texts: List[str], model=EMBEDDING_MODEL_NAME):
    """Embed a list of texts with Gemini, batching to stay under limits."""
    if client is None:
        raise ImportError(
            "google-genai is not installed or GOOGLE_API_KEY is missing; install "
            "google-genai and set GOOGLE_API_KEY to use embeddings."
        )
    if not texts:
        return []

    # clean None/empty
    clean = [t for t in texts if t and isinstance(t, str)]
    if not clean:
        return []

    # The batch size is not about characters or tokens.
    # It does not split individual texts; each text remains whole.
    # It simply means "send up to 100 texts at a time into a batch."
    BATCH = 100
    vectors = []

    for i in range(0, len(clean), BATCH):
        batch = clean[i : i + BATCH]

        with propagate_attributes(tags=["embedding-job"]):
            resp = client.models.embed_content(
                model=model,
                contents=batch,
            )
        # Update with embedding token usage and cost
        embed_response = client.models.count_tokens(model=MODEL_NAME, contents=texts)
        embed_cost = _estimate_embed_cost(embed_response.total_tokens)
        print("cost: ", embed_cost)
        langfuse.update_current_generation(
            usage_details={"input": embed_response.total_tokens},
            cost_details={"input": embed_cost},
        )
        for emb in resp.embeddings:
            vectors.append(emb.values)

    return vectors


# @observe(as_type="embedding")
# def embed_text(text, model=EMBEDDING_MODEL_NAME):
#     """Embed a single string with Gemini embeddings."""
#     if client is None:
#         raise ImportError(
#             "google-genai is not installed or GOOGLE_API_KEY is missing; install "
#             "google-genai and set GOOGLE_API_KEY to use embeddings."
#         )
#     if not text:
#         return []

#     resp = client.models.embed_content(
#         model=model,
#         contents=[text],
#     )

#     if resp.embeddings:
#         return resp.embeddings[0].values
#     return []


if __name__ == "__main__":
    embed = embed_texts(["hello, world!"])
    print(len(embed[0]))

    # client = genai.Client(api_key=GOOGLE_API_KEY) if genai and GOOGLE_API_KEY else None
    # text = "hello, world!"

    # response = client.models.count_tokens(model=MODEL_NAME, contents=text)
    # token_count = response.total_tokens

    # print(f"Total tokens: {response.total_tokens}")
