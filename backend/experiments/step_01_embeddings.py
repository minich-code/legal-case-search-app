import os
import sys
import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional
import voyageai
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from pathlib import Path
from box import ConfigBox
from backend.src.utils.common import read_yaml
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.constants import CONFIG_FILEPATH

load_dotenv()


# --- 1. Configuration Dataclass ---
@dataclass
class EmbeddingConfig:
    """Configuration for embedding model and API credentials."""
    api_key: str
    embedding_model_name: str


# --- 2. Configuration Manager Class ---
class ConfigurationManager:
    """Manages loading and validation of configuration from YAML and environment variables."""
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        try:
            logger.info(f"Initializing ConfigurationManager with config file: {config_path}")
            self.config_path = Path(config_path)
            self.config = read_yaml(self.config_path)
            if not self.config or 'embedding_models' not in self.config:
                raise ValueError("Configuration error: 'embedding_models' section missing in config file")
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error initializing ConfigurationManager: {e}")
            raise LegalRAGException(e)

    def get_embedding_config(self) -> EmbeddingConfig:
        """Extracts and validates embedding configuration."""
        try:
            embedding_config = self.config['embedding_models']
            api_key = os.environ.get('VOYAGE_API_KEY')

            if not api_key:
                logger.warning("VOYAGE_API_KEY not set, ensure .env is configured")
                raise ValueError("Voyage API key not found in environment variables.")
            if not hasattr(embedding_config, 'embedding_model_name'):
                raise ValueError("Embedding model name not found in configuration.")

            return EmbeddingConfig(
                api_key=api_key,
                embedding_model_name=embedding_config.embedding_model_name
            )
        except Exception as e:
            logger.error(f"Error loading embedding configuration: {e}")
            raise LegalRAGException(e)


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


# --- 4. Main Function for Testing ---
async def main():
    """Tests embedding functionality with sample legal query and documents."""
    try:
        # Initialize Configuration Manager
        config_manager = ConfigurationManager()
        # Get Embedding Configuration
        embedding_config = config_manager.get_embedding_config()
        # Initialize Embedding Service
        embedder = EmbeddingService(embedding_config)

        # Test embedding a query
        query = "What is the standard for a preliminary objection?"
        query_embedding = await embedder.embed([query], input_type="query")
        logger.info(f"Successfully embedded query. Vector length: {len(query_embedding[0])}")

        # Test embedding documents
        docs = ["This is the first legal document.", "This is the second legal document."]
        doc_embeddings = await embedder.embed(docs, input_type="document")
        logger.info(f"Successfully embedded {len(doc_embeddings)} documents.")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise LegalRAGException(e)


# --- 5. Run the Test ---
if __name__ == "__main__":
    asyncio.run(main())