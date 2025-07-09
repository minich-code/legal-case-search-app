import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from backend.src.utils.common import read_yaml
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.constants import CONFIG_FILEPATH
from backend.src.llm import LLMService, LLMConfig, ConfigManager as LLMConfigManager
from importlib import import_module
from tenacity import retry, stop_after_attempt, wait_exponential

# Load .env file
load_dotenv()


# --- 1. Response Config ---
@dataclass
class ResponseConfig:
    """Configuration for response generation and citation parameters."""
    max_citations: int
    cot_template: str


# --- 2. Config Manager ---
class ConfigManager:
    """Manages loading and validation of configuration from YAML and environment variables."""
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        try:
            logger.info(f"Initializing ConfigurationManager with config file: {config_path}")
            self.config_path = Path(config_path)
            self.config = read_yaml(self.config_path)
            if not self.config or 'response' not in self.config:
                raise ValueError("Configuration error: 'response' section missing in config file")
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error initializing ConfigurationManager: {e}")
            raise LegalRAGException(e)

    def get_response_config(self) -> ResponseConfig:
        """Extracts and validates response configuration from YAML."""
        try:
            response_config = self.config['response']
            if not hasattr(response_config, 'max_citations'):
                raise ValueError("Max citations not found in configuration.")
            if not hasattr(response_config, 'cot_template_path'):
                raise ValueError("CoT template path not found in configuration.")

            # Load CoT template
            template_path = response_config.cot_template_path.replace('/', '.').replace('.py', '')
            module = import_module(template_path)
            cot_template = getattr(module, 'COT_PROMPT_TEMPLATE', None)
            if not cot_template:
                raise ValueError(f"Invalid CoT template at {response_config.cot_template_path}")

            return ResponseConfig(
                max_citations=response_config.max_citations,
                cot_template=cot_template
            )
        except Exception as e:
            logger.error(f"Error loading response configuration: {e}")
            raise LegalRAGException(e)


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


# --- 4. Main Test Function ---
async def main():
    """Tests response generation with a legal query and dummy documents."""
    try:
        logger.info("Loading response configuration")
        config_manager = ConfigManager()
        response_config = config_manager.get_response_config()

        logger.info("Loading LLM configuration")
        llm_config_manager = LLMConfigManager()
        llm_config = llm_config_manager.get_llm_config()
        llm_service = LLMService(llm_config)

        logger.info("Initializing ResponseService")
        response_service = ResponseService(response_config, llm_service)

        query = "What is the exception to the rule in Foss v Harbottle?"
        dummy_documents = [
            {"id": "doc1", "text": "The rule in Foss v Harbottle limits minority shareholder actions, but exceptions exist for ultra vires acts.", "citation": "[2025] KEHC 4273 (KLR)", "chunk_sequence": 1},
            {"id": "doc2", "text": "Foss v Harbottle does not apply when the company acts illegally or fraudulently.", "citation": "[2024] KEHC 1234 (KLR)", "chunk_sequence": 1},
            {"id": "doc3", "text": "Another exception to Foss v Harbottle is when personal rights of shareholders are infringed.", "citation": "[2023] KEHC 5678 (KLR)", "chunk_sequence": 1}
        ]
        model_id = llm_service.providers[0]['model_name']  # Use first available model (e.g., Grok)

        logger.info(f"Generating response for query: {query}")
        result = await response_service.generate_response(query, dummy_documents, model_id)

        logger.info("Response:")
        logger.info(f"Answer: {result['answer'][:200]}...")
        logger.info("Citations:")
        for i, citation in enumerate(result['citations'], 1):
            logger.info(f"{i}. Citation: {citation['citation']}, Source: {citation['source']}")
    except Exception as e:
        logger.error(f"Error in response test: {e}")
        raise LegalRAGException(e)


# --- 5. Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())