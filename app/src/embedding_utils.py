import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)


def embed_texts(texts, model="text-embedding-004"):
    """
    Embed a list of strings using Gemini embeddings.
    Handles batch size limit of 100.
    """
    if not texts:
        return []

    # clean None/empty
    clean = [t for t in texts if t and isinstance(t, str)]
    if not clean:
        return []

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


def embed_text(text, model="text-embedding-004"):
    """
    Embed a single string using Gemini embeddings.
    """
    if not text:
        return []

    resp = client.models.embed_content(
        model=model,
        contents=[text],
    )

    if resp.embeddings:
        return resp.embeddings[0].values
    return []
