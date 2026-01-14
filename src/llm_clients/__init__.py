"""LLM client factory and initialization."""

from typing import Dict, Any
from .base import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .google_client import GoogleClient


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(
        provider: str,
        model_name: str,
        api_key: str,
        input_cost_per_1k: float,
        output_cost_per_1k: float,
        **kwargs
    ) -> BaseLLMClient:
        """Create an LLM client based on provider."""
        
        if provider == "openai":
            return OpenAIClient(
                api_key=api_key,
                model_name=model_name,
                input_cost_per_1k=input_cost_per_1k,
                output_cost_per_1k=output_cost_per_1k,
                **kwargs
            )
        elif provider == "anthropic":
            return AnthropicClient(
                api_key=api_key,
                model_name=model_name,
                input_cost_per_1k=input_cost_per_1k,
                output_cost_per_1k=output_cost_per_1k,
                **kwargs
            )
        elif provider == "google":
            return GoogleClient(
                api_key=api_key,
                model_name=model_name,
                input_cost_per_1k=input_cost_per_1k,
                output_cost_per_1k=output_cost_per_1k,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")


__all__ = [
    "BaseLLMClient",
    "OpenAIClient",
    "AnthropicClient",
    "GoogleClient",
    "LLMClientFactory"
]
