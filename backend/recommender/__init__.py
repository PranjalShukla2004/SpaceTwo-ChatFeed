# Marks recommender as a package and exposes top-level helpers.
from .index import search
from .embeddings import get_embeddings

__all__ = ["search", "get_embeddings"]
