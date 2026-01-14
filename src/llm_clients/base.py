"""Abstract base class for LLM clients."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time


@dataclass
class LLMResponse:
    """Standardized response from an LLM."""
    text: str
    input_tokens: int
    output_tokens: int
    total_cost: float
    time_to_first_token: Optional[float]
    total_latency: float
    tokens_per_second: float
    metadata: Dict[str, Any]


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(
        self, 
        model_name: str, 
        input_cost_per_1k: float,
        output_cost_per_1k: float,
        **kwargs
    ):
        self.model_name = model_name
        self.input_cost_per_1k = input_cost_per_1k
        self.output_cost_per_1k = output_cost_per_1k
        self.kwargs = kwargs
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost of a request."""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost
    
    def calculate_tokens_per_second(
        self, 
        output_tokens: int, 
        latency: float
    ) -> float:
        """Calculate tokens per second."""
        if latency > 0:
            return output_tokens / latency
        return 0.0
