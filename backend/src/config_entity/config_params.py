from dataclasses import dataclass, field
from typing import List, Dict, Any

# ---- Embedding Config ----
@dataclass
class EmbeddingConfig:
    """Configuration for embedding model and API credentials."""
    api_key: str
    embedding_model_name: str

# --- Retrieval Config ---
@dataclass
class RetrievalConfig:
    """Configuration for Pinecone vector store and retrieval parameters."""
    pinecone_index_name: str
    pinecone_api_key: str
    retrieval_top_k: int

#--- Reranker Config ---
@dataclass
class RerankerConfig:
    """Configuration for reranking model and parameters."""
    model_name: str
    top_n: int

# --- LLM Config ---
@dataclass
class LLMConfig:
    """Configuration for LLM providers and generation parameters."""
    max_tokens: int
    providers: List[Dict[str, Any]] = field(default_factory=list)

# --- Response Config ---
@dataclass
class ResponseConfig:
    """Configuration for response generation and citation parameters."""
    max_citations: int
    cot_template: str