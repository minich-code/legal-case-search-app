
import asyncio
import time
from typing import List, Dict, Any
import torch
from sentence_transformers import CrossEncoder
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.config_entity.config_params import RerankerConfig


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

