# backend/seed_dummy_users.py
from __future__ import annotations
import os, time, hashlib
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)  # <-- load .env FIRST

# ---- config from env (after load_dotenv) ----
USE_LOCAL  = os.getenv("EMBED_FALLBACK", "").lower() in ("1", "true", "yes", "on")
EMBED_DIM  = int(os.getenv("EMBED_DIM", "1536"))
MODEL_EMBED = os.getenv("MODEL_EMBED", "text-embedding-3-small")
INDEX_NAME = os.getenv("PINECONE_INDEX", "spacetwo-chat")

from pinecone import Pinecone, ServerlessSpec

def get_pc() -> Pinecone:
    key = os.getenv("PINECONE_API_KEY")
    if not key:
        raise RuntimeError("Missing PINECONE_API_KEY — check backend/.env and load order.")
    return Pinecone(api_key=key)

# --------- embeddings (OpenAI with automatic local fallback) ---------
def _local_embed(text: str) -> List[float]:
    import numpy as np
    h = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big") % (2**32 - 1)
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(EMBED_DIM)
    v = v / np.linalg.norm(v)
    return v.astype("float32").tolist()

def embed(text: str) -> List[float]:
    if USE_LOCAL:
        return _local_embed(text)

    from openai import OpenAI
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("[embed] OPENAI_API_KEY not set → using local fallback.")
        return _local_embed(text)

    client = OpenAI(api_key=key)
    try:
        out = client.embeddings.create(model=MODEL_EMBED, input=text)
        return out.data[0].embedding
    except Exception as e:
        print(f"[embed] OpenAI error ({type(e).__name__}): {e} → using local fallback.")
        return _local_embed(text)

# --------- ensure index ---------
pc = get_pc()
if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
    print(f"[pinecone] Creating index '{INDEX_NAME}' (dim={EMBED_DIM})...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while True:
        info = pc.describe_index(INDEX_NAME)
        if info.status.get("ready"):
            break
        time.sleep(1)
idx = pc.Index(INDEX_NAME)

# --------- dummy profiles ---------
def text_repr(p: Dict) -> str:
    return (
        f"{p['name']} — {p['role']}.\n"
        f"Styles: {', '.join(p['styles'])}.\n"
        f"Location: {p['location']}.\n"
        f"Bio: {p['bio']}"
    )

profiles = [
  {"id":"u1","name":"Maya Tan","role":"Video Editor","styles":["lo-fi","fast cuts","TikTok"],"location":"Glasgow, UK","bio":"Lo-fi reels editor; punchy transitions, vintage overlays."},
  {"id":"u2","name":"Leo Park","role":"Video Editor","styles":["cinematic","color grading"],"location":"London, UK","bio":"Filmic LUTs, smooth cross-cuts, tasteful sound design."},
  {"id":"u3","name":"Anya Rao","role":"Motion Designer","styles":["kinetic type","music sync"],"location":"Manchester, UK","bio":"Text-driven motion; bold type systems timed to beats."},
  {"id":"u4","name":"Jay Patel","role":"Video Editor","styles":["lo-fi","fast cuts","humor"],"location":"Edinburgh, UK","bio":"Comedy shorts; whip cuts, punch-ins, meme timing."},
  {"id":"u5","name":"Sara Kim","role":"Sound Designer","styles":["ambient","lo-fi"],"location":"Glasgow, UK","bio":"Ambient beds, tape hiss, vinyl crackle, subtle risers."},
]

vectors = [{
    "id": p["id"],
    "values": embed(text_repr(p)),
    "metadata": {
        "name": p["name"],
        "roles": [p["role"]],
        "styles": p["styles"],
        "location": p["location"],
        "bio": p["bio"],
        "availability": True,
    }
} for p in profiles]

idx.upsert(vectors=vectors)
print(f"[done] Upserted {len(vectors)} profiles into '{INDEX_NAME}'. USE_LOCAL={USE_LOCAL}, DIM={EMBED_DIM}")
