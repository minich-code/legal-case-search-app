
import asyncio
import time
from typing import List
import voyageai
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.config_entity.config_params import EmbeddingConfig


# --- 3. The Embedding Service Class ---
class EmbeddingService:
    """Service for generating embeddings using Voyage AI."""
    def __init__(self, config: EmbeddingConfig):
        try:
            if not isinstance(config, EmbeddingConfig):
                raise ValueError("Invalid configuration: must be an EmbeddingConfig instance")
            self.config = config
            self.client = voyageai.Client(api_key=self.config.api_key)
            logger.info(f"EmbeddingService initialized with model '{self.config.embedding_model_name}'.")
        except Exception as e:
            logger.error(f"Failed to initialize Voyage AI client: {e}")
            raise LegalRAGException(e)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed(self, texts: List[str], input_type: str) -> List[List[float]]:
        """
        Embeds a list of texts using Voyage AI.

        Args:
            texts: A list of strings to embed (non-empty)
            input_type: Either "query" or "document"

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            if not texts or not isinstance(texts, list):
                raise ValueError("Input texts must be a non-empty list")
            if not all(isinstance(text, str) and text.strip() for text in texts):
                raise ValueError("All texts must be non-empty strings")
            if input_type not in ["query", "document"]:
                raise ValueError("input_type must be either 'query' or 'document'")

            start_time = time.time()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.embed(
                    texts=texts,
                    model=self.config.embedding_model_name,
                    input_type=input_type,
                    truncation=True
                )
            )
            elapsed_time = time.time() - start_time
            logger.info(f"Embedded {len(texts)} texts in {elapsed_time:.2f} seconds")
            return result.embeddings
        except Exception as e:
            logger.error(f"Error during embedding with Voyage AI: {e}")
            raise LegalRAGException(e)


