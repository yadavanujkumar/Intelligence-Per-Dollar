"""Example usage of the Intelligence-Per-Dollar system."""

import asyncio
from src.utils import load_config, get_api_keys, get_database_url
from src.models import get_session, BenchmarkRepository
from src.router import ValueRouter


async def example_router_usage():
    """Example: Using the Value Router programmatically."""
    
    print("=" * 60)
    print("Example: Smart Model Selection with Value Router")
    print("=" * 60)
    
    # Initialize router
    database_url = get_database_url()
    session = get_session(database_url)
    repository = BenchmarkRepository(session)
    router = ValueRouter(repository)
    
    # Example 1: High quality requirement
    print("\n1. High Quality Requirement (0.9):")
    selection = router.select_model(quality_threshold=0.9)
    print(f"   Selected: {selection['model_name']}")
    print(f"   Reasoning: {selection['reasoning']}")
    
    # Example 2: Budget-conscious selection
    print("\n2. Budget-Conscious (0.7 quality, max $0.02):")
    selection = router.select_model(
        quality_threshold=0.7,
        max_cost=0.02
    )
    print(f"   Selected: {selection['model_name']}")
    print(f"   Reasoning: {selection['reasoning']}")
    
    # Example 3: Category-specific
    print("\n3. Coding Tasks (0.85 quality):")
    selection = router.select_model(
        quality_threshold=0.85,
        category="coding"
    )
    print(f"   Selected: {selection['model_name']}")
    print(f"   Reasoning: {selection['reasoning']}")
    
    # Example 4: Get efficiency frontier
    print("\n4. Efficiency Frontier (All Models):")
    frontier = router.get_efficiency_frontier()
    for idx, model in enumerate(frontier[:3], 1):
        print(f"   {idx}. {model['model_name']}: "
              f"{model['intelligence_per_dollar']:.2f} intelligence/$")


def example_metrics_query():
    """Example: Querying benchmark metrics."""
    
    print("\n" + "=" * 60)
    print("Example: Querying Benchmark Metrics")
    print("=" * 60)
    
    database_url = get_database_url()
    session = get_session(database_url)
    repository = BenchmarkRepository(session)
    
    # Get performance for specific model
    print("\n1. Model Performance:")
    performance = repository.get_model_performance("gpt-5-2", category="coding")
    
    if performance:
        print(f"   Model: {performance['model_name']}")
        print(f"   Avg Intelligence: {performance['avg_intelligence_score']:.3f}")
        print(f"   Avg Cost: ${performance['avg_cost']:.4f}")
        print(f"   Intelligence/$: {performance['intelligence_per_dollar']:.2f}")
        print(f"   Total Samples: {performance['total_samples']}")
    else:
        print("   No data available. Run a benchmark first!")
    
    # Get recent results
    print("\n2. Recent Results (Last 10):")
    results = repository.get_all_results(limit=10)
    
    for result in results:
        print(f"   [{result.timestamp.strftime('%Y-%m-%d %H:%M')}] "
              f"{result.model_name} - {result.prompt_category}: "
              f"Score={result.intelligence_score:.2f}, "
              f"Cost=${result.total_cost:.4f}")


def example_config_loading():
    """Example: Loading and displaying configuration."""
    
    print("\n" + "=" * 60)
    print("Example: Configuration Management")
    print("=" * 60)
    
    config = load_config()
    
    print("\n1. Available Models:")
    for model_name, model_config in config["models"].items():
        print(f"   - {model_name}:")
        print(f"     Provider: {model_config['provider']}")
        print(f"     Input: ${model_config['input_cost_per_1k']}/1K tokens")
        print(f"     Output: ${model_config['output_cost_per_1k']}/1K tokens")
    
    print("\n2. Judge Configuration:")
    judge = config["judge_model"]
    print(f"   Provider: {judge['provider']}")
    print(f"   Model: {judge['model_name']}")
    
    print("\n3. Benchmark Settings:")
    benchmark = config["benchmark"]
    print(f"   Prompts per category: {benchmark['prompts_per_category']}")
    print(f"   Categories: {', '.join(benchmark['categories'])}")
    print(f"   Multi-turn depth: {benchmark['multi_turn_depth']}")


def main():
    """Run all examples."""
    print("\n🚀 Intelligence-Per-Dollar System Examples\n")
    
    # Example 1: Config loading
    example_config_loading()
    
    # Example 2: Metrics query
    example_metrics_query()
    
    # Example 3: Router usage (async)
    asyncio.run(example_router_usage())
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("\nNext steps:")
    print("  1. Run benchmark: python run_benchmark.py")
    print("  2. View dashboard: streamlit run src/dashboard/app.py")
    print("  3. Start API: python -m uvicorn src.router.api:app --reload")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
