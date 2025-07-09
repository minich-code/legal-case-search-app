import asyncio
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from box import ConfigBox
import torch
from sentence_transformers import CrossEncoder
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH

# Load .env file
load_dotenv()


# --- 1. Reranker Config ---
@dataclass
class RerankerConfig:
    """Configuration for reranking model and parameters."""
    model_name: str
    top_n: int

# --- 2. Config Manager ---
class ConfigManager:
    """Manages loading and validation of configuration from YAML and environment variables."""
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        try:
            logger.info(f"Initializing ConfigurationManager with config file: {config_path}")
            self.config_path = Path(config_path)
            self.config = read_yaml(self.config_path)
            if not self.config or 'reranker' not in self.config:
                raise ValueError("Configuration error: 'reranker' section missing in config file")
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error initializing ConfigurationManager: {e}")
            raise LegalRAGException(e)

    def get_reranking_config(self) -> RerankerConfig:
        """Extracts and validates reranking configuration from YAML."""
        try:
            reranking_config = self.config['reranker']

            if not hasattr(reranking_config, 'model_name'):
                raise ValueError("Reranking model name not found in configuration.")
            if not hasattr(reranking_config, 'top_n'):
                raise ValueError("Reranked top_n candidates not found in configuration.")

            return RerankerConfig(
                model_name=reranking_config.model_name,
                top_n=reranking_config.top_n
            )
        except Exception as e:
            logger.error(f"Error loading reranking configuration: {e}")
            raise LegalRAGException(e)


# --- 3. Reranker Service ---
class RerankerService:
    """Service for reranking documents using a Cross-Encoder model."""
    def __init__(self, config: RerankerConfig):
        try:
            if not isinstance(config, RerankerConfig):
                raise TypeError("config must be an instance of RerankerConfig")
            self.config = config
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"RerankerService initializing on device: '{self.device}'")
            self.model = CrossEncoder(self.config.model_name, device=self.device)
            logger.info(f"Cross-Encoder model '{self.config.model_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize CrossEncoder: {e}")
            raise LegalRAGException(e)

    async def rerank(self, query: str, documents: List[Dict[str, Any]], batch_size: int = None) -> List[Dict[str, Any]]:
        """
        Reranks documents based on relevance to a query using Cross-Encoder.

        Args:
            query: A non-empty string query.
            documents: List of document dictionaries with 'text' key.
            batch_size: Optional batch size for processing (default: process all).

        Returns:
            List of top-n reranked document dictionaries with 'rerank_score'.
        """
        try:
            if not query or not isinstance(query, str):
                raise ValueError("Query must be a non-empty string")
            if not documents:
                logger.warning("No documents provided for reranking")
                return []

            start_time = time.time()
            pairs = [[query, doc['text']] for doc in documents]
            batch_size = batch_size or len(pairs)  # Default to full batch

            loop = asyncio.get_event_loop()
            scores = []
            for i in range(0, len(pairs), batch_size):
                batch_pairs = pairs[i:i + batch_size]
                def predict_scores():
                    return self.model.predict(batch_pairs, show_progress_bar=False)
                batch_scores = await loop.run_in_executor(None, predict_scores)
                scores.extend(batch_scores)

            # Add scores to documents
            for doc, score in zip(documents, scores):
                doc['rerank_score'] = float(score)  # Ensure JSON-serializable

            # Sort by rerank_score and take top_n
            reranked_docs = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
            top_reranked_docs = reranked_docs[:self.config.top_n]

            elapsed_time = time.time() - start_time
            logger.info(f"Reranked {len(documents)} documents in {elapsed_time:.2f} seconds, kept top {len(top_reranked_docs)}")
            return top_reranked_docs
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            raise LegalRAGException(e)


# --- 4. Main Test Function ---
async def main():
    """Tests reranking with a sample query and dummy legal documents."""
    try:
        logger.info("Loading reranking configuration")
        config_manager = ConfigManager()
        config = config_manager.get_reranking_config()
        logger.info("Reranking configuration loaded")

        logger.info("Initializing RerankerService")
        reranker = RerankerService(config)

        query = "What is the exception to the rule in Foss v Harbottle?"
        dummy_documents = [
            {"id": "doc1", "text": "The rule in Foss v Harbottle limits minority shareholder actions, but exceptions exist for ultra vires acts.", "citation": "Case1", "chunk_sequence": 1},
            {"id": "doc2", "text": "Foss v Harbottle does not apply when the company acts illegally or fraudulently.", "citation": "Case2", "chunk_sequence": 1},
            {"id": "doc3", "text": "Unrelated legal principle about contract law.", "citation": "Case3", "chunk_sequence": 1},
            {"id": "doc4", "text": "Another exception to Foss v Harbottle is when personal rights of shareholders are infringed.", "citation": "Case4", "chunk_sequence": 1}
        ]

        logger.info(f"Reranking {len(dummy_documents)} documents for query: {query}")
        reranked_docs = await reranker.rerank(query, dummy_documents)

        if not reranked_docs:
            logger.warning("No reranked documents returned")
            return

        logger.info("Reranked Documents:")
        for i, doc in enumerate(reranked_docs, 1):
            logger.info(f"Document {i}:")
            logger.info(f"Citation: {doc.get('citation', 'N/A')}")
            logger.info(f"Text: {doc.get('text', 'N/A')[:150]}...")
            logger.info(f"Rerank Score: {doc.get('rerank_score', 'N/A'):.4f}")
            logger.info(f"Chunk Sequence: {doc.get('chunk_sequence', 'N/A')}")
    except Exception as e:
        logger.error(f"Error in reranking process: {e}")
        raise LegalRAGException(e)


# --- 5. Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())