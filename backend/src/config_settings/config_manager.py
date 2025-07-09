# import os
# from dotenv import load_dotenv
# from pathlib import Path
# from backend.src.utils.common import read_yaml
# from backend.src.utils.logger import logger
# from backend.src.utils.exception import LegalRAGException
# from backend.src.constants import CONFIG_FILEPATH
# from importlib import import_module
# from backend.src.config_entity.config_params import (EmbeddingConfig, RetrievalConfig, RerankerConfig, LLMConfig, ResponseConfig)
#
# load_dotenv()
#
# # --- 2. Configuration Manager Class ---
# class ConfigurationManager:
#     """Manages loading and validation of configuration from YAML and environment variables."""
#     def __init__(
#             self,
#             config_path: str = CONFIG_FILEPATH
#         ):
#
#         try:
#             logger.info(f"Initializing ConfigurationManager")
#
#             self.config_path = Path(config_path)
#             self.config = read_yaml(self.config_path)
#
#             if not self.config or 'embedding_models' not in self.config:
#                 raise ValueError("Configuration error: 'embedding_models' section missing in config file")
#
#             if not self.config or 'vector_store' not in self.config:
#                 raise ValueError("Configuration error: 'vector_store' section missing in config file")
#
#             if not self.config or 'retrieval' not in self.config:
#                 raise ValueError("Configuration error: 'vector_store' section missing in config file")
#
#             if not self.config or 'reranker' not in self.config:
#                 raise ValueError("Configuration error: 'reranker' section missing in config file")
#
#             if not self.config or 'generation' not in self.config:
#                 raise ValueError("Configuration error: 'vector_store' section missing in config file")
#
#             if not self.config or 'response' not in self.config:
#                 raise ValueError("Configuration error: 'response' section missing in config file")
#
#
#             logger.info("Configuration loaded successfully.")
#         except Exception as e:
#             logger.error(f"Error initializing ConfigurationManager: {e}")
#             raise LegalRAGException(e)
#
# # -------------Embedding config -----------------------
#
#     def get_embedding_config(self) -> EmbeddingConfig:
#         """Extracts and validates embedding configuration."""
#         try:
#             embedding_config = self.config['embedding_models']
#             api_key = os.environ.get('VOYAGE_API_KEY')
#
#             if not api_key:
#                 logger.warning("VOYAGE_API_KEY not set, ensure .env is configured")
#                 raise ValueError("Voyage API key not found in environment variables.")
#             if not hasattr(embedding_config, 'embedding_model_name'):
#                 raise ValueError("Embedding model name not found in configuration.")
#
#             return EmbeddingConfig(
#                 api_key=api_key,
#                 embedding_model_name=embedding_config.embedding_model_name
#             )
#         except Exception as e:
#             logger.error(f"Error loading embedding configuration: {e}")
#             raise LegalRAGException(e)
#
#
# # -------------Retrieval config -----------------------
#
#     def get_retrieval_config(self) -> RetrievalConfig:
#         """Extracts and validates retrieval configuration from YAML and environment."""
#         try:
#             vector_store_config = self.config['vector_store']
#             retrieval_config = self.config['retrieval']
#             api_key = os.environ.get('PINECONE_API_KEY')
#
#             if not api_key:
#                 logger.warning("PINECONE_API_KEY not set, ensure .env is configured")
#                 raise ValueError("Pinecone API key not found in environment variables.")
#             if not hasattr(vector_store_config, 'index_name'):
#                 raise ValueError("Pinecone index name not found in configuration.")
#             if not hasattr(retrieval_config, 'top_k_candidates'):
#                 raise ValueError("Retrieval top_k_candidates not found in configuration.")
#
#             return RetrievalConfig(
#                 pinecone_index_name=vector_store_config.index_name,
#                 pinecone_api_key=api_key,
#                 retrieval_top_k=retrieval_config.top_k_candidates
#             )
#         except Exception as e:
#             logger.error(f"Error loading retrieval configuration: {e}")
#             raise LegalRAGException(e)
#
#
# # -------------Reranker config -----------------------
#     def get_reranking_config(self) -> RerankerConfig:
#         """Extracts and validates reranking configuration from YAML."""
#         try:
#             reranking_config = self.config['reranker']
#
#             if not hasattr(reranking_config, 'model_name'):
#                 raise ValueError("Reranking model name not found in configuration.")
#             if not hasattr(reranking_config, 'top_n'):
#                 raise ValueError("Reranked top_n candidates not found in configuration.")
#
#             return RerankerConfig(
#                 model_name=reranking_config.model_name,
#                 top_n=reranking_config.top_n
#             )
#         except Exception as e:
#             logger.error(f"Error loading reranking configuration: {e}")
#             raise LegalRAGException(e)
#
#
# # -------------Generation config -----------------------
#     def get_llm_config(self) -> LLMConfig:
#         """Extracts and validates LLM configuration from YAML."""
#         try:
#             generation_config = self.config['generation']
#             if not hasattr(generation_config, 'max_tokens'):
#                 raise ValueError("Max tokens not found in configuration.")
#             if not hasattr(generation_config, 'providers'):
#                 raise ValueError("Providers not found in configuration.")
#
#             # Validate provider priorities
#             providers = generation_config.providers
#             for provider in providers:
#                 if not provider.get('priority'):
#                     logger.warning(f"Priority not set for {provider.get('model_name')}, defaulting to 999")
#                     provider['priority'] = 999
#
#             return LLMConfig(
#                 max_tokens=generation_config.max_tokens,
#                 providers=providers
#             )
#         except Exception as e:
#             logger.error(f"Error loading LLM configuration: {e}")
#             raise LegalRAGException(e)
#
#
# # -------------Response config -----------------------
#     def get_response_config(self) -> ResponseConfig:
#         """Extracts and validates response configuration from YAML."""
#         try:
#             response_config = self.config['response']
#             if not hasattr(response_config, 'max_citations'):
#                 raise ValueError("Max citations not found in configuration.")
#             if not hasattr(response_config, 'cot_template_path'):
#                 raise ValueError("CoT template path not found in configuration.")
#
#             # Load CoT template
#             template_path = response_config.cot_template_path.replace('/', '.').replace('.py', '')
#             module = import_module(template_path)
#             cot_template = getattr(module, 'COT_PROMPT_TEMPLATE', None)
#             if not cot_template:
#                 raise ValueError(f"Invalid CoT template at {response_config.cot_template_path}")
#
#             return ResponseConfig(
#                 max_citations=response_config.max_citations,
#                 cot_template=cot_template
#             )
#         except Exception as e:
#             logger.error(f"Error loading response configuration: {e}")
#             raise LegalRAGException(e)


import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, List
from backend.src.utils.common import read_yaml
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.constants import CONFIG_FILEPATH
from importlib import import_module
from backend.src.config_entity.config_params import (EmbeddingConfig, RetrievalConfig, RerankerConfig, LLMConfig, ResponseConfig)

load_dotenv()

# --- Configuration Manager Class ---
class ConfigurationManager:
    """Manages loading and validation of configuration from YAML and environment variables."""
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        try:
            logger.info(f"Initializing ConfigurationManager with config file: {config_path}")
            self.config_path = Path(config_path)
            self.config = read_yaml(self.config_path)
            if not self.config:
                raise ValueError("Configuration error: config file is empty or invalid")
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error initializing ConfigurationManager: {e}")
            raise LegalRAGException(e)

    @staticmethod
    def _get_api_key(key_name: str) -> str:
        """Fetches and validates an API key from environment variables."""
        api_key = os.environ.get(key_name)
        if not api_key:
            logger.warning(f"{key_name} not set, ensure .env is configured")
            raise ValueError(f"{key_name} not found in environment variables.")
        return api_key

    @staticmethod
    def _validate_section(section: str, config: Any, required_fields: List[str]) -> None:
        """Validates that required fields exist in a config section."""
        for field in required_fields:
            if not hasattr(config, field):
                raise ValueError(f"{field} not found in {section} configuration.")

    def get_embedding_config(self) -> EmbeddingConfig:
        """Extracts and validates embedding configuration."""
        try:
            logger.info("Loading embedding configuration")
            embedding_config = self.config.get('embedding_models')
            if not embedding_config:
                raise ValueError("Configuration error: 'embedding_models' section missing")
            self._validate_section('embedding_models', embedding_config, ['embedding_model_name'])
            api_key = self._get_api_key('VOYAGE_API_KEY')
            return EmbeddingConfig(
                api_key=api_key,
                embedding_model_name=embedding_config.embedding_model_name
            )
        except Exception as e:
            logger.error(f"Error loading embedding configuration: {e}")
            raise LegalRAGException(e)

    def get_retrieval_config(self) -> RetrievalConfig:
        """Extracts and validates retrieval configuration from YAML and environment."""
        try:
            logger.info("Loading retrieval configuration")
            vector_store_config = self.config.get('vector_store')
            retrieval_config = self.config.get('retrieval')
            if not vector_store_config:
                raise ValueError("Configuration error: 'vector_store' section missing")
            if not retrieval_config:
                raise ValueError("Configuration error: 'retrieval' section missing")
            self._validate_section('vector_store', vector_store_config, ['index_name'])
            self._validate_section('retrieval', retrieval_config, ['top_k_candidates'])
            api_key = self._get_api_key('PINECONE_API_KEY')
            return RetrievalConfig(
                pinecone_index_name=vector_store_config.index_name,
                pinecone_api_key=api_key,
                retrieval_top_k=retrieval_config.top_k_candidates
            )
        except Exception as e:
            logger.error(f"Error loading retrieval configuration: {e}")
            raise LegalRAGException(e)

    def get_reranking_config(self) -> RerankerConfig:
        """Extracts and validates reranking configuration from YAML."""
        try:
            logger.info("Loading reranking configuration")
            reranking_config = self.config.get('reranker')
            if not reranking_config:
                raise ValueError("Configuration error: 'reranker' section missing")
            self._validate_section('reranker', reranking_config, ['model_name', 'top_n'])
            return RerankerConfig(
                model_name=reranking_config.model_name,
                top_n=reranking_config.top_n
            )
        except Exception as e:
            logger.error(f"Error loading reranking configuration: {e}")
            raise LegalRAGException(e)

    def get_llm_config(self) -> LLMConfig:
        """Extracts and validates LLM configuration from YAML."""
        try:
            logger.info("Loading LLM configuration")
            generation_config = self.config.get('generation')
            if not generation_config:
                raise ValueError("Configuration error: 'generation' section missing")
            self._validate_section('generation', generation_config, ['max_tokens', 'providers'])
            providers = generation_config.providers
            for provider in providers:
                if not provider.get('priority'):
                    logger.warning(f"Priority not set for {provider.get('model_name')}, defaulting to 999")
                    provider['priority'] = 999
            return LLMConfig(
                max_tokens=generation_config.max_tokens,
                providers=providers
            )
        except Exception as e:
            logger.error(f"Error loading LLM configuration: {e}")
            raise LegalRAGException(e)

    def get_response_config(self) -> ResponseConfig:
        """Extracts and validates response configuration from YAML."""
        try:
            logger.info("Loading response configuration")
            response_config = self.config.get('response')
            if not response_config:
                raise ValueError("Configuration error: 'response' section missing")
            self._validate_section('response', response_config, ['max_citations', 'cot_template_path'])
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