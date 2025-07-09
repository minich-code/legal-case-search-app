import os
import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from groq import AsyncGroq, GroqError
from together import Together
from backend.src.utils.common import read_yaml
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.constants import CONFIG_FILEPATH
from tenacity import retry, stop_after_attempt, wait_exponential

# Load .env file
load_dotenv()


# --- 1. LLM Config ---
@dataclass
class LLMConfig:
    """Configuration for LLM providers and generation parameters."""
    max_tokens: int
    providers: List[Dict[str, Any]] = field(default_factory=list)


# --- 2. Config Manager ---
class ConfigManager:
    """Manages loading and validation of configuration from YAML and environment variables."""
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        try:
            logger.info(f"Initializing ConfigurationManager with config file: {config_path}")
            self.config_path = Path(config_path)
            self.config = read_yaml(self.config_path)
            if not self.config or 'generation' not in self.config:
                raise ValueError("Configuration error: 'vector_store' section missing in config file")
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error initializing ConfigurationManager: {e}")
            raise LegalRAGException(e)

    def get_llm_config(self) -> LLMConfig:
        """Extracts and validates LLM configuration from YAML."""
        try:
            generation_config = self.config['generation']
            if not hasattr(generation_config, 'max_tokens'):
                raise ValueError("Max tokens not found in configuration.")
            if not hasattr(generation_config, 'providers'):
                raise ValueError("Providers not found in configuration.")

            # Validate provider priorities
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


# --- 3. LLM Service ---
class LLMService:
    """Service for generating responses from a single LLM provider with prioritized fallback."""
    def __init__(self, config: LLMConfig):
        try:
            if not isinstance(config, LLMConfig):
                raise TypeError("config must be an instance of LLMConfig")
            self.config = config
            self.providers = []
            self.clients = {}
            self._initialize_clients()
            if not self.providers:
                raise ValueError("No valid LLM providers configured. Check .env and config.yaml.")
            logger.info(f"Initialized LLMService with {len(self.providers)} providers")
        except Exception as e:
            logger.error(f"Failed to initialize LLMService: {e}")
            raise LegalRAGException(e)

    def _initialize_clients(self):
        """Initializes clients for configured providers."""
        for provider_config in self.config.providers:
            model_name = provider_config.get('model_name')
            provider = provider_config.get('provider')
            priority = provider_config.get('priority', 999)
            api_key = os.getenv(f"{provider.upper()}_API_KEY")

            if provider in ['openai', 'anthropic'] and not api_key:
                logger.warning(f"Skipping {provider} ({model_name}) due to missing API key (placeholder for production)")
                continue
            if not api_key:
                logger.warning(f"Skipping {provider} ({model_name}) due to missing {provider.upper()}_API_KEY")
                continue

            try:
                if provider == 'groq':
                    self.clients[provider] = AsyncGroq(api_key=api_key)
                elif provider == 'together':
                    self.clients[provider] = Together(api_key=api_key)
                else:
                    logger.warning(f"Unsupported provider: {provider}")
                    continue
                self.providers.append({'model_name': model_name, 'provider': provider, 'priority': priority})
                logger.info(f"Initialized {provider} with model: {model_name} (priority: {priority})")
            except Exception as e:
                logger.error(f"Error initializing {provider} ({model_name}): {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, model_id: str, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a response using the highest-priority provider for the specified model.

        Args:
            model_id: The model name (e.g., 'llama-3.3-70b-versatile').
            system_prompt: System prompt for the LLM.
            user_prompt: User query or prompt.

        Returns:
            Generated response as a string.
        """
        try:
            start_time = time.time()
            providers = [p for p in self.providers if p['model_name'] == model_id]
            if not providers:
                raise ValueError(f"No provider found for model: {model_id}")

            # Select provider with lowest priority number (highest priority)
            provider_config = min(providers, key=lambda x: x['priority'])
            provider = provider_config['provider']
            model_name = provider_config['model_name']
            logger.info(f"Using {provider} with model {model_name} (priority: {provider_config['priority']})")

            if provider == 'groq':
                completion = await self.clients[provider].chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=self.config.max_tokens
                )
                response = completion.choices[0].message.content
            elif provider == 'together':
                completion = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.clients[provider].chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.1,
                        max_tokens=self.config.max_tokens
                    )
                )
                response = completion.choices[0].message.content
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            if not response:
                raise ValueError(f"Empty response from {provider} ({model_name})")

            elapsed_time = time.time() - start_time
            logger.info(f"Generated response from {provider} in {elapsed_time:.2f} seconds: {response[:100]}...")
            return response

        except Exception as e:
            logger.error(f"Error with {provider} ({model_name}): {e}")
            raise LegalRAGException(f"Generation failed for {model_id}: {e}")


# --- 4. Main Test Function ---
async def main():
    """Tests LLM generation with legal-specific queries across configured providers."""
    try:
        logger.info("Loading LLM configuration")
        config_manager = ConfigManager()
        config = config_manager.get_llm_config()
        llm_service = LLMService(config)
        system_prompt = "You are a legal assistant specializing in case law analysis."

        # Test queries
        queries = [
            "What is the exception to the rule in Foss v Harbottle?",
            "Explain the standard for a preliminary objection in legal proceedings."
        ]
        model_ids = [p['model_name'] for p in llm_service.providers if p['provider'] in ['groq', 'together']]

        for model_id in model_ids:
            for query in queries:
                logger.info(f"Testing model {model_id} with query: {query}")
                response = await llm_service.generate(model_id, system_prompt, query)
                logger.info(f"Query: {query}")
                logger.info(f"Response: {response[:200]}...")
    except Exception as e:
        logger.error(f"Error in LLM test: {e}")
        raise LegalRAGException(e)


# --- 5. Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())