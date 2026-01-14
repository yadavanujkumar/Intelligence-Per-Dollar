"""Main benchmarking orchestrator."""

import asyncio
from typing import List, Dict, Any
from datetime import datetime

from ..models import BenchmarkRepository, get_session
from ..llm_clients import BaseLLMClient
from .judge import LLMJudge


class BenchmarkOrchestrator:
    """Orchestrates the benchmarking process across multiple models."""
    
    def __init__(
        self,
        models: Dict[str, BaseLLMClient],
        judge: LLMJudge,
        repository: BenchmarkRepository
    ):
        self.models = models
        self.judge = judge
        self.repository = repository
    
    async def run_benchmark(
        self,
        prompts: List[Dict[str, Any]],
        include_follow_ups: bool = True
    ) -> int:
        """Run benchmark across all models and prompts."""
        
        # Calculate total prompts
        total_prompts = len(prompts) * len(self.models)
        if include_follow_ups:
            total_prompts += sum(
                len(p.get("follow_ups", [])) for p in prompts
            ) * len(self.models)
        
        # Create benchmark run
        run = self.repository.create_run(total_prompts=total_prompts)
        print(f"Started benchmark run {run.id} with {total_prompts} total prompts")
        
        # Run benchmarks for each model
        tasks = []
        for model_name, client in self.models.items():
            task = self._benchmark_model(
                run_id=run.id,
                model_name=model_name,
                client=client,
                prompts=prompts,
                include_follow_ups=include_follow_ups
            )
            tasks.append(task)
        
        # Run all model benchmarks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Complete the run
        self.repository.complete_run(run.id)
        
        # Update performance cache
        self.repository.update_performance_cache()
        
        print(f"Completed benchmark run {run.id}")
        return run.id
    
    async def _benchmark_model(
        self,
        run_id: int,
        model_name: str,
        client: BaseLLMClient,
        prompts: List[Dict[str, Any]],
        include_follow_ups: bool
    ):
        """Benchmark a single model across all prompts."""
        
        print(f"Starting benchmark for {model_name}")
        
        for prompt_data in prompts:
            await self._benchmark_prompt(
                run_id=run_id,
                model_name=model_name,
                client=client,
                prompt_data=prompt_data,
                turn_number=1
            )
            
            # Handle follow-up prompts for multi-turn conversations
            if include_follow_ups and "follow_ups" in prompt_data:
                for turn_idx, follow_up in enumerate(prompt_data["follow_ups"], start=2):
                    await self._benchmark_prompt(
                        run_id=run_id,
                        model_name=model_name,
                        client=client,
                        prompt_data={
                            **prompt_data,
                            "prompt": follow_up
                        },
                        turn_number=turn_idx
                    )
        
        print(f"Completed benchmark for {model_name}")
    
    async def _benchmark_prompt(
        self,
        run_id: int,
        model_name: str,
        client: BaseLLMClient,
        prompt_data: Dict[str, Any],
        turn_number: int
    ):
        """Benchmark a single prompt for a model."""
        
        prompt_text = prompt_data["prompt"]
        prompt_id = prompt_data["id"]
        category = prompt_data["category"]
        
        try:
            # Generate response
            response = await client.generate(prompt_text, max_tokens=1000)
            
            # Evaluate response using judge
            evaluation = await self.judge.evaluate(
                prompt=prompt_text,
                response=response.text,
                category=category
            )
            
            # Save result
            result_data = {
                "run_id": run_id,
                "model_name": model_name,
                "provider": response.metadata.get("provider"),
                "prompt_id": prompt_id,
                "prompt_text": prompt_text,
                "prompt_category": category,
                "turn_number": turn_number,
                "response_text": response.text,
                "intelligence_score": evaluation["intelligence_score"],
                "judge_reasoning": evaluation["judge_reasoning"],
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "total_cost": response.total_cost,
                "time_to_first_token": response.time_to_first_token,
                "total_latency": response.total_latency,
                "tokens_per_second": response.tokens_per_second,
                "raw_metadata": response.metadata,
                "timestamp": datetime.utcnow()
            }
            
            self.repository.save_result(result_data)
            
            print(f"✓ {model_name} - {prompt_id} (Turn {turn_number}): "
                  f"Score={evaluation['intelligence_score']:.2f}, "
                  f"Cost=${response.total_cost:.4f}, "
                  f"Latency={response.total_latency:.2f}s")
        
        except Exception as e:
            # Save error result
            result_data = {
                "run_id": run_id,
                "model_name": model_name,
                "provider": client.kwargs.get("provider", "unknown"),
                "prompt_id": prompt_id,
                "prompt_text": prompt_text,
                "prompt_category": category,
                "turn_number": turn_number,
                "response_text": None,
                "intelligence_score": 0.0,
                "judge_reasoning": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_cost": 0.0,
                "time_to_first_token": None,
                "total_latency": 0.0,
                "tokens_per_second": 0.0,
                "error_message": str(e),
                "raw_metadata": {},
                "timestamp": datetime.utcnow()
            }
            
            self.repository.save_result(result_data)
            
            print(f"✗ {model_name} - {prompt_id} (Turn {turn_number}): Error - {str(e)}")
