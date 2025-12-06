# app/src/embedding_utils.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Helpers for Gemini embeddings of text for drift/metrics analysis.
# --------------------------------------
import os
import sys
from pathlib import Path

try:
    from google import genai  # type: ignore
except ImportError:
    genai = None
from dotenv import load_dotenv

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config.config import EMBEDDING_MODEL_NAME

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY) if genai and GOOGLE_API_KEY else None


def embed_texts(texts, model=EMBEDDING_MODEL_NAME):
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

        resp = client.models.embed_content(
            model=model,
            contents=batch,
        )

        for emb in resp.embeddings:
            vectors.append(emb.values)

    return vectors


def embed_text(text, model=EMBEDDING_MODEL_NAME):
    """Embed a single string with Gemini embeddings."""
    if client is None:
        raise ImportError(
            "google-genai is not installed or GOOGLE_API_KEY is missing; install "
            "google-genai and set GOOGLE_API_KEY to use embeddings."
        )
    if not text:
        return []

    resp = client.models.embed_content(
        model=model,
        contents=[text],
    )

    if resp.embeddings:
        return resp.embeddings[0].values
    return []
