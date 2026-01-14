"""OpenAI LLM client implementation."""

import time
from typing import Optional, Dict, Any
import openai
from .base import BaseLLMClient, LLMResponse


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI models (GPT-5, etc.)."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str,
        input_cost_per_1k: float,
        output_cost_per_1k: float,
        **kwargs
    ):
        super().__init__(model_name, input_cost_per_1k, output_cost_per_1k, **kwargs)
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate a response using OpenAI API."""
        start_time = time.time()
        time_to_first_token = None
        
        try:
            # Use streaming to capture TTFT
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            response_text = ""
            first_token = True
            
            async for chunk in stream:
                if first_token and chunk.choices:
                    time_to_first_token = time.time() - start_time
                    first_token = False
                
                if chunk.choices and chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content
            
            total_latency = time.time() - start_time
            
            # Get token counts (approximate for streaming)
            # In production, use tiktoken for accurate counting
            input_tokens = len(prompt.split()) * 1.3  # Rough approximation
            output_tokens = len(response_text.split()) * 1.3
            
            input_tokens = int(input_tokens)
            output_tokens = int(output_tokens)
            
            total_cost = self.calculate_cost(input_tokens, output_tokens)
            tokens_per_second = self.calculate_tokens_per_second(
                output_tokens, 
                total_latency
            )
            
            return LLMResponse(
                text=response_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_cost=total_cost,
                time_to_first_token=time_to_first_token,
                total_latency=total_latency,
                tokens_per_second=tokens_per_second,
                metadata={"model": self.model_name, "provider": "openai"}
            )
            
        except Exception as e:
            total_latency = time.time() - start_time
            raise Exception(f"OpenAI API error: {str(e)}")
