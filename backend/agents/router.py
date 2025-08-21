# agents/router.py
import os
from typing import Tuple, List
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

_system = """
You are a router for a creative-collaboration chat. Decide whether the latest user
message should trigger recommendations. Output STRICT JSON with keys:
- intent: one of ["recommend_collaborators","recommend_projects","small_talk"].
- query: a concise search string derived from user context.
- tags: list of style/role tags.
"""

_prompt = ChatPromptTemplate.from_messages([
    ("system", _system),
    ("human", "History: {history}\nLatest: {latest}")
])

_parser = JsonOutputParser()

def _get_model():
    # Create the LLM only when needed (avoid import-time errors)
    return ChatOpenAI(model=os.getenv("MODEL_CHAT", "gpt-4o-mini"), temperature=0)

def route(history: str, latest: str) -> Tuple[str, str, List[str]]:
    try:
        model = _get_model()
        chain = _prompt | model | _parser
        out = chain.invoke({"history": history, "latest": latest})
        return out.get("intent", "small_talk"), out.get("query", latest), out.get("tags", [])
    except Exception:
        # Safe fallback if API key missing or offline
        text = f"{history}\n{latest}".lower()
        if any(k in text for k in ["editor", "composer", "designer", "animator", "collab", "recommend"]):
            return "recommend_collaborators", latest, []
        return "small_talk", latest, []
