

import os
import asyncio
import time
from dotenv import load_dotenv
from groq import AsyncGroq, GroqError
from together import Together
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.src.config_entity.config_params import LLMConfig

# Load .env file
load_dotenv()

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


