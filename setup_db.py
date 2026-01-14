#!/usr/bin/env python3
"""Setup script to initialize the database."""

import sys
from src.models import create_tables
from src.utils import get_database_url

def main():
    """Initialize the database with required tables."""
    print("🔧 Initializing database...")
    
    database_url = get_database_url()
    print(f"Database URL: {database_url}")
    
    try:
        create_tables(database_url)
        print("✅ Database initialized successfully!")
        print("\nCreated tables:")
        print("  - benchmark_runs")
        print("  - benchmark_results")
        print("  - model_performance_cache")
        print("\n📊 You can now run benchmarks with: python run_benchmark.py")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
