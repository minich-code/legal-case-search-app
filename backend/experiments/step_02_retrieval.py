import asyncio
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH
from backend.src.utils.exception import LegalRAGException
from backend.src.utils.logger import logger

# Environment Loading
load_dotenv()

# --- 1. Data Class ---
@dataclass
class RetrievalConfig:
    """Configuration for Pinecone vector store and retrieval parameters."""
    pinecone_index_name: str
    pinecone_api_key: str
    retrieval_top_k: int


# --- 2. Config Manager Class ---
class ConfigManager:
    """Manages loading and validation of configuration from YAML and environment variables."""
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        try:
            logger.info(f"Initializing ConfigurationManager with config file: {config_path}")
            self.config_path = Path(config_path)
            self.config = read_yaml(self.config_path)
            if not self.config or 'retrieval' not in self.config:
                raise ValueError("Configuration error: 'vector_store' section missing in config file")
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error initializing ConfigurationManager: {e}")
            raise LegalRAGException(e)

    def get_retrieval_config(self) -> RetrievalConfig:
        """Extracts and validates retrieval configuration from YAML and environment."""
        try:
            vector_store_config = self.config['vector_store']
            retrieval_config = self.config['retrieval']
            api_key = os.environ.get('PINECONE_API_KEY')

            if not api_key:
                logger.warning("PINECONE_API_KEY not set, ensure .env is configured")
                raise ValueError("Pinecone API key not found in environment variables.")
            if not hasattr(vector_store_config, 'index_name'):
                raise ValueError("Pinecone index name not found in configuration.")
            if not hasattr(retrieval_config, 'top_k_candidates'):
                raise ValueError("Retrieval top_k_candidates not found in configuration.")

            return RetrievalConfig(
                pinecone_index_name=vector_store_config.index_name,
                pinecone_api_key=api_key,
                retrieval_top_k=retrieval_config.top_k_candidates
            )
        except Exception as e:
            logger.error(f"Error loading retrieval configuration: {e}")
            raise LegalRAGException(e)


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


# --- 4. Test Function ---
async def main():
    """Tests dense retrieval with a sample query embedding."""
    try:
        # Initialize ConfigManager
        logger.info("Loading configuration using ConfigManager")
        config_manager = ConfigManager()
        retrieval_config = config_manager.get_retrieval_config()
        logger.info("Retrieval configuration loaded")

        # Initialize RetrievalService
        retriever = RetrievalService(config=retrieval_config)

        # Test retrieval with dummy embedding
        dummy_embedding = [0.1] * 1024  # Matches voyage-law-2 dimensionality
        logger.info(f"Retrieving top {retrieval_config.retrieval_top_k} candidates")
        results = await retriever.retrieve(dummy_embedding)

        logger.info(f"Retrieved {len(results)} documents")
        for i, doc in enumerate(results, 1):
            logger.info(f"Document {i}:")
            logger.info(f"Citation: {doc.get('citation', 'N/A')}")
            logger.info(f"Excerpt: {doc.get('text', 'N/A')[:100]}...")
    except Exception as e:
        logger.error(f"Retrieval test failed: {e}")
        raise LegalRAGException(e)


# --- 5. Run the Test ---
if __name__ == "__main__":
    asyncio.run(main())