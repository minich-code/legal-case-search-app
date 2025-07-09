
import asyncio
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone
from backend.src.utils.exception import LegalRAGException
from backend.src.utils.logger import logger
from backend.src.config_entity.config_params import RetrievalConfig

# Environment Loading
load_dotenv()

# --- 3. Retrieval Service Class ---
class RetrievalService:
    """Service for dense retrieval from Pinecone vector index, designed for async pipelines."""
    def __init__(self, config: RetrievalConfig):
        if not isinstance(config, RetrievalConfig):
            raise TypeError("config must be an instance of RetrievalConfig")
        self.config = config
        self.index = None
        self._initialize_pinecone()

    def _initialize_pinecone(self):
        """Initializes Pinecone connection with validation."""
        try:
            logger.info("Initializing Pinecone connection...")
            pc = Pinecone(api_key=self.config.pinecone_api_key)
            available_indexes = pc.list_indexes().names()

            if self.config.pinecone_index_name not in available_indexes:
                raise ValueError(
                    f"Index '{self.config.pinecone_index_name}' not found. "
                    f"Available indexes: {', '.join(available_indexes)}"
                )
            self.index = pc.Index(self.config.pinecone_index_name)
            logger.info(f"Successfully connected to Pinecone index: '{self.config.pinecone_index_name}'")
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
            raise LegalRAGException(e)

    async def retrieve(self, query_embedding: List[float], namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top-k documents from Pinecone using dense retrieval.

        Args:
            query_embedding: A list of floats representing the query vector.
            namespace: Optional Pinecone namespace for retrieval (default: None).

        Returns:
            List of dictionaries containing metadata for top-k documents.
        """
        try:
            if not query_embedding or not isinstance(query_embedding, list):
                raise ValueError("query_embedding must be a non-empty list of floats")
            if not all(isinstance(x, (int, float)) for x in query_embedding):
                raise ValueError("query_embedding must contain only numbers")
            # Validate dimensionality (e.g., 1024 for voyage-law-2)
            expected_dim = 1024  # Adjust based on your index
            if len(query_embedding) != expected_dim:
                raise ValueError(f"query_embedding dimension {len(query_embedding)} does not match expected {expected_dim}")

            start_time = time.time()
            loop = asyncio.get_event_loop()
            query_response = await loop.run_in_executor(
                None,
                lambda: self.index.query(
                    vector=query_embedding,
                    top_k=self.config.retrieval_top_k,
                    include_metadata=True,
                    namespace=namespace
                )
            )
            candidates = [match.metadata for match in query_response.matches if match.metadata]
            elapsed_time = time.time() - start_time
            logger.info(f"Retrieved {len(candidates)} documents in {elapsed_time:.2f} seconds")
            if not candidates:
                logger.warning("No candidates found for the given query")
            return candidates
        except Exception as e:
            logger.error(f"Error during retrieval operation: {e}")
            raise LegalRAGException(e)


