import os
from langchain_openai import OpenAIEmbeddings


_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(model=os.getenv("MODEL_EMBED", "text-embedding-3-large"))
    return _embeddings