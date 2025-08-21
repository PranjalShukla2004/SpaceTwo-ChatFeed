import os
import hashlib
import numpy as np
from typing import List, Dict
from pinecone import Pinecone
from openai import OpenAI
from .embeddings import get_embeddings

INDEX_NAME = os.getenv("PINECONE_INDEX", "spacetwo-collaborators")
USE_LOCAL = os.getenv("EMBED_FALLBACK", "").lower() in ("1","true","yes","on")
EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))
MODEL_EMBED = os.getenv("MODEL_EMBED", "text-embedding-3-small")

# Vector schema: id, values (embedding), metadata {name, roles, styles, location:{lat,lng}, availability, portfolio_url}

def get_pc():
    raw = os.getenv("PINECONE_API_KEY")
    if not raw:
        raise RuntimeError("PINECONE_API_KEY missing")
    api_key = raw.strip().strip('"').strip("'")  # remove newline/quotes
    return Pinecone(api_key=api_key)


def ensure_index(dim: int = 3072):
    PC = get_pc()
    if INDEX_NAME not in [i.name for i in PC.list_indexes()]:
        PC.create_index(name=INDEX_NAME, dimension=dim, metric="cosine")
    return PC.Index(INDEX_NAME)

def local_embed(text: str) -> List[float]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big") % (2**32 - 1)
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(EMBED_DIM)
    v = v / np.linalg.norm(v)
    return v.astype("float32").tolist()

def embed_query(text: str) -> List[float]:
    if USE_LOCAL:
        return local_embed(text)
    # OpenAI path (only if key exists)
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        # no key? fall back locally instead of crashing
        return local_embed(text)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        return client.embeddings.create(model=MODEL_EMBED, input=text).data[0].embedding
    except Exception as e:
        # quota/auth/network errors -> fall back so endpoint still works
        print(f"[embed_query] OpenAI error ({type(e).__name__}): {e} -> using local fallback")
        return local_embed(text)

def search(query: str, top_k: int = 5, filters: Dict = None) -> List[Dict]:
    idx = ensure_index()  # must return pinecone.Index bound to your PINECONE_INDEX
    qv = embed_query(query)
    kwargs = {"vector": qv, "top_k": int(top_k), "include_metadata": True}
    if filters:
        kwargs["filter"] = filters
    res = idx.query(**kwargs)

    out = []
    for m in getattr(res, "matches", []):
        md = m.metadata or {}
        roles = md.get("roles") or ([md["role"]] if md.get("role") else [])
        out.append({
            "id": m.id,
            "score": float(getattr(m, "score", 0.0) or 0.0),
            "name": md.get("name"),
            "roles": roles,
            "styles": md.get("styles", []),
            "availability": md.get("availability", False),
            "portfolio_url": md.get("portfolio_url"),
            "location": md.get("location"),
            "media_url": md.get("media_url"),
        })
    return out


def upsert_collaborators(items: List[Dict]):
    """items: [{id, text, metadata}] — text is embedded; metadata merged into vector metadata."""
    idx = ensure_index()
    emb = get_embeddings()
    texts = [it["text"] for it in items]
    vecs = emb.embed_documents(texts)
    to_upsert = []
    for it, v in zip(items, vecs):
        md = it.get("metadata", {})
        to_upsert.append({"id": it["id"], "values": v, "metadata": md})
    idx.upsert(vectors=to_upsert)
