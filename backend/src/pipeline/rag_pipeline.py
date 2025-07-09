
import asyncio
import time
from typing import List, Dict, Any
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.config_settings.config_manager import ConfigurationManager
from backend.src.components.embedding import EmbeddingService
from backend.src.components.retriever import RetrievalService
from backend.src.components.reranker import RerankerService
from backend.src.components.llm_service import LLMService
from backend.src.components.response import ResponseService


class LegalRAGPipeline:
    """Orchestrates the legal RAG pipeline for processing queries and generating responses."""
    def __init__(self, config_manager: ConfigurationManager):
        try:
            logger.info("Initializing LegalRAGPipeline")
            self.config_manager = config_manager

            # Initialize services
            embedding_config = config_manager.get_embedding_config()
            self.embedding_service = EmbeddingService(embedding_config)

            retrieval_config = config_manager.get_retrieval_config()
            self.retrieval_service = RetrievalService(retrieval_config)

            reranker_config = config_manager.get_reranking_config()
            self.reranker_service = RerankerService(reranker_config)

            llm_config = config_manager.get_llm_config()
            self.llm_service = LLMService(llm_config)

            response_config = config_manager.get_response_config()
            self.response_service = ResponseService(response_config, self.llm_service)

            logger.info("LegalRAGPipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LegalRAGPipeline: {e}")
            raise LegalRAGException(e)

    async def process_query(self, query: str, model_id: str = None) -> Dict[str, Any]:
        """
        Processes a legal query through the RAG pipeline.

        Args:
            query: The user query string.
            model_id: Optional LLM model ID (defaults to highest-priority model).

        Returns:
            Dictionary with 'answer' and 'citations' (list of citation dictionaries).
        """
        try:
            start_time = time.time()
            logger.info(f"Processing query: {query}")

            # Step 1: Generate query embedding
            logger.info("Generating query embedding")
            query_embedding = await self.embedding_service.embed([query], input_type="query")
            query_embedding = query_embedding[0]  # Single query embedding

            # Step 2: Retrieve documents
            logger.info("Retrieving documents")
            retrieved_docs = await self.retrieval_service.retrieve(query_embedding)

            # Step 3: Rerank documents
            logger.info("Reranking documents")
            reranked_docs = await self.reranker_service.rerank(query, retrieved_docs)

            # Step 4: Generate response
            logger.info("Generating final response")
            model_id = model_id or self.llm_service.providers[0]['model_name']  # Default to highest-priority model
            response = await self.response_service.generate_response(query, reranked_docs, model_id)

            elapsed_time = time.time() - start_time
            logger.info(f"Processed query in {elapsed_time:.2f} seconds")
            return response
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise LegalRAGException(e)


# --- Test Function ---
async def main():
    """Tests the full LegalRAGPipeline with a sample legal query."""
    try:
        logger.info("Starting pipeline test")
        config_manager = ConfigurationManager()
        pipeline = LegalRAGPipeline(config_manager)

        query = "What is the exception to the rule in Foss v Harbottle?"
        response = await pipeline.process_query(query)

        logger.info("Pipeline Response:")
        logger.info(f"Answer: {response['answer'][:200]}...")
        logger.info("Citations:")
        for i, citation in enumerate(response['citations'], 1):
            logger.info(f"{i}. Citation: {citation['citation']}, Source: {citation['source']}")
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        raise LegalRAGException(e)


# --- Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())