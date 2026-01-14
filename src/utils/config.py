"""Configuration management utilities."""

import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_api_keys() -> Dict[str, str]:
    """Get API keys from environment variables."""
    return {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY")
    }


def get_database_url() -> str:
    """Get database URL from environment."""
    return os.getenv("DATABASE_URL", "sqlite:///./benchmark.db")
