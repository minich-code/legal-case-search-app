

import time
from typing import List, Dict, Any
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.src.config_entity.config_params import ResponseConfig
from backend.src.components.llm_service import LLMService


# --- 3. Response Service ---
class ResponseService:
    """Service for generating final responses with citations using a Chain of Thought template."""
    def __init__(self, response_config: ResponseConfig, llm_service: LLMService):
        try:
            if not isinstance(response_config, ResponseConfig):
                raise TypeError("response_config must be an instance of ResponseConfig")
            if not isinstance(llm_service, LLMService):
                raise TypeError("llm_service must be an instance of LLMService")
            self.config = response_config
            self.llm_service = llm_service
            logger.info("ResponseService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ResponseService: {e}")
            raise LegalRAGException(e)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_response(self, query: str, documents: List[Dict[str, Any]], model_id: str) -> Dict[str, Any]:
        """
        Generates a final response with citations using the CoT template.

        Args:
            query: The user query string.
            documents: List of document dictionaries with 'text' and 'citation' keys.
            model_id: The LLM model to use (e.g., 'llama-3.3-70b-versatile').

        Returns:
            Dictionary with 'answer' and 'citations' (list of citation dictionaries).
        """
        try:
            if not query or not isinstance(query, str):
                raise ValueError("Query must be a non-empty string")
            if not documents:
                logger.warning("No documents provided for response generation")
                documents = []

            start_time = time.time()
            # Format documents for the prompt
            formatted_docs = []
            citations = []
            for i, doc in enumerate(documents[:self.config.max_citations], 1):
                text = doc.get('text', 'N/A')
                citation = doc.get('citation', 'N/A')
                link = doc.get('link', 'TBD')  # Placeholder for future links
                formatted_docs.append(f"Document {i}: {text}\nCitation: {citation}\nSource: {link}")
                citations.append({"citation": citation, "source": link})
            documents_str = "\n\n".join(formatted_docs) or "No documents available."

            # Format the CoT prompt
            prompt = self.config.cot_template.format(
                query=query,
                documents=documents_str,
                max_citations=self.config.max_citations
            )

            # Call LLMService
            response = await self.llm_service.generate(
                model_id=model_id,
                system_prompt="You are a legal assistant specializing in case law analysis.",
                user_prompt=prompt
            )

            elapsed_time = time.time() - start_time
            logger.info(f"Generated response in {elapsed_time:.2f} seconds: {response[:100]}...")

            return {
                "answer": response,
                "citations": citations
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise LegalRAGException(e)

