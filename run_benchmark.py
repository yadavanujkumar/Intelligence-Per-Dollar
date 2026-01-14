"""Main entry point for running benchmarks."""

import asyncio
import argparse
from typing import List

from src.utils import load_config, get_api_keys, get_database_url
from src.models import create_tables, get_session, BenchmarkRepository
from src.llm_clients import LLMClientFactory
from src.benchmarking import LLMJudge, BenchmarkOrchestrator
from data.prompts.benchmark_prompts import get_all_prompts, get_prompts_by_category


async def run_benchmark(
    config_path: str = "config.yaml",
    category: str = None,
    num_prompts: int = None
):
    """Run the benchmarking suite."""
    
    print("🚀 Starting LLM Cost-Efficiency Benchmark")
    print("=" * 60)
    
    # Load configuration
    config = load_config(config_path)
    api_keys = get_api_keys()
    database_url = get_database_url()
    
    # Initialize database
    print("\n📊 Initializing database...")
    create_tables(database_url)
    session = get_session(database_url)
    repository = BenchmarkRepository(session)
    
    # Create LLM clients
    print("\n🤖 Initializing LLM clients...")
    models = {}
    
    for model_key, model_config in config["models"].items():
        provider = model_config["provider"]
        api_key = api_keys.get(provider)
        
        if not api_key:
            print(f"⚠️  Skipping {model_key}: No API key for {provider}")
            continue
        
        try:
            client = LLMClientFactory.create_client(
                provider=provider,
                model_name=model_config["model_name"],
                api_key=api_key,
                input_cost_per_1k=model_config["input_cost_per_1k"],
                output_cost_per_1k=model_config["output_cost_per_1k"]
            )
            models[model_key] = client
            print(f"✓ Initialized {model_key}")
        except Exception as e:
            print(f"✗ Failed to initialize {model_key}: {e}")
    
    if not models:
        print("\n❌ No models initialized. Please check your API keys.")
        return
    
    # Initialize judge
    print("\n⚖️  Initializing LLM-as-a-Judge...")
    judge_config = config["judge_model"]
    judge_api_key = api_keys.get(judge_config["provider"])
    
    if not judge_api_key:
        print(f"❌ No API key for judge model ({judge_config['provider']})")
        return
    
    judge_client = LLMClientFactory.create_client(
        provider=judge_config["provider"],
        model_name=judge_config["model_name"],
        api_key=judge_api_key,
        input_cost_per_1k=0.030,  # Judge model pricing
        output_cost_per_1k=0.120
    )
    judge = LLMJudge(judge_client)
    
    # Load prompts
    print("\n📝 Loading prompts...")
    if category:
        prompts = get_prompts_by_category(category)
        print(f"Loaded {len(prompts)} prompts for category '{category}'")
    else:
        prompts = get_all_prompts()
        print(f"Loaded {len(prompts)} prompts across all categories")
    
    if num_prompts:
        prompts = prompts[:num_prompts]
        print(f"Limited to {num_prompts} prompts")
    
    # Create orchestrator and run benchmark
    print("\n🎯 Starting benchmark execution...")
    print(f"Testing {len(models)} models with {len(prompts)} prompts")
    print("=" * 60)
    
    orchestrator = BenchmarkOrchestrator(
        models=models,
        judge=judge,
        repository=repository
    )
    
    run_id = await orchestrator.run_benchmark(prompts, include_follow_ups=True)
    
    print("\n" + "=" * 60)
    print(f"✅ Benchmark completed! Run ID: {run_id}")
    print("\n💡 View results:")
    print("   - Dashboard: streamlit run src/dashboard/app.py")
    print("   - API: python -m src.router.api")


def main():
    """Command-line interface for benchmark."""
    parser = argparse.ArgumentParser(
        description="Run LLM Cost-Efficiency Benchmark"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--category",
        choices=["coding", "summarization", "creative_writing"],
        help="Only test specific category"
    )
    parser.add_argument(
        "--num-prompts",
        type=int,
        help="Limit number of prompts to test"
    )
    
    args = parser.parse_args()
    
    asyncio.run(run_benchmark(
        config_path=args.config,
        category=args.category,
        num_prompts=args.num_prompts
    ))


if __name__ == "__main__":
    main()
