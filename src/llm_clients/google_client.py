"""Google Generative AI (Gemini) client implementation."""

import time
from typing import Optional, Dict, Any
import google.generativeai as genai
from .base import BaseLLMClient, LLMResponse


class GoogleClient(BaseLLMClient):
    """Client for Google Gemini models."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str,
        input_cost_per_1k: float,
        output_cost_per_1k: float,
        **kwargs
    ):
        super().__init__(model_name, input_cost_per_1k, output_cost_per_1k, **kwargs)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate a response using Google Gemini API."""
        start_time = time.time()
        time_to_first_token = None
        
        try:
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            response_text = ""
            first_token = True
            
            # Stream response
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            async for chunk in response:
                if first_token and chunk.text:
                    time_to_first_token = time.time() - start_time
                    first_token = False
                if chunk.text:
                    response_text += chunk.text
            
            total_latency = time.time() - start_time
            
            # Get token counts (approximate)
            input_tokens = len(prompt.split()) * 1.3
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
                metadata={"model": self.model_name, "provider": "google"}
            )
            
        except Exception as e:
            total_latency = time.time() - start_time
            raise Exception(f"Google API error: {str(e)}")
