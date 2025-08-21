import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List
from pathlib import Path
from model import ChatRequest, ChatResponse, Recommendation
from agents.router import route
from recommender.index import search


load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)


app = FastAPI(title="SpacetwoChat Backend", version="0.1.0")
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)




@app.get("/health")
def health():
    return {"ok": True}




@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 1) Extract latest user message
    latest_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    history = "\n".join([f"{m.role}: {m.content}" for m in req.messages[-10:]])

    # 2) Route intent
    intent, q, tags = route(history, latest_user)

    recs: List[Recommendation] = []
    reply = ""


    if intent == "recommend_collaborators":
        # Optional: compose Pinecone filter from req.geo / availability
        filters = {}
        if req.availability_required:
            filters["availability"] = {"$eq": True}
        # Future: add geo-box filter via pre-indexed geohash buckets
        hits = search(q, top_k=6, filters=filters)
        for h in hits:
            recs.append(Recommendation(
                id=h["id"],
                kind="collaborator",
                title=h.get("name") or "Untitled",
                subtitle=", ".join(h.get("roles", [])) or "Creator",
                media_url=h.get("media_url"),
                score=h.get("score", 0.0),
                meta={"styles": h.get("styles", []), "portfolio_url": h.get("portfolio_url")}
            ))
        reply = f"I found {len(recs)} collaborators for ‘{q}’. Want to invite any of them?"
    elif intent == "recommend_projects":
        # Placeholder — same pattern, different index/namespace
        reply = "Here are some projects you might like (stub)."
    else:
        reply = "Got it. Tell me what you want to make, and I can line up the right people."


    return ChatResponse(reply=reply, recommendations=recs)




# --- Optional: a simple ingest route (for quick testing) ---
from fastapi import Body
from recommender.index import upsert_collaborators

@app.post("/api/ingest")
def ingest(payload: dict = Body(...)):
    # Example usage: upsert_collaborators(payload["items"])
    return {"upserted": len(payload["items"]) }