# model.py (or models.py)

from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str

class ChatRequest(BaseModel):
    thread_id: str
    messages: List[ChatMessage]
    geo: Optional[Dict] = None
    availability_required: bool = False

class Recommendation(BaseModel):
    id: str
    kind: str  # "collaborator" | "project" | "cluster"
    title: str
    subtitle: Optional[str] = None
    media_url: Optional[str] = None
    distance_km: Optional[float] = None
    score: float = Field(default=0.0)
    meta: dict = Field(default_factory=dict)

class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation] = []
