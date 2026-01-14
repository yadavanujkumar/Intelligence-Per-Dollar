# Development Setup

## Quick Start for Development

### 1. Install in Development Mode

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

### 2. Set Up Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
# Optional: LANGCHAIN_API_KEY for tracing
```

### 3. Initialize Database

```bash
# For SQLite (quick testing)
export DATABASE_URL="sqlite:///./benchmark.db"
python setup_db.py

# For PostgreSQL (production)
export DATABASE_URL="postgresql://user:password@localhost:5432/llm_benchmarks"
python setup_db.py
```

### 4. Run Examples

```bash
python examples.py
```

## Development Workflow

### Running Tests

```bash
# Run all tests (when implemented)
pytest

# Run with coverage
pytest --cov=src
```

### Running the Benchmark

```bash
# Quick test with limited prompts
python run_benchmark.py --num-prompts 2

# Test specific category
python run_benchmark.py --category coding

# Full benchmark
python run_benchmark.py
```

### Starting Services

```bash
# Terminal 1: Router API
python -m uvicorn src.router.api:app --reload --port 8000

# Terminal 2: Dashboard
streamlit run src/dashboard/app.py --server.port 8501
```

## Project Structure Details

### Database Models (`src/models/`)
- `database.py`: SQLAlchemy models
- `repository.py`: Data access layer with business logic

### LLM Clients (`src/llm_clients/`)
- `base.py`: Abstract base class
- `openai_client.py`: OpenAI/GPT implementation
- `anthropic_client.py`: Anthropic/Claude implementation
- `google_client.py`: Google/Gemini implementation

### Benchmarking (`src/benchmarking/`)
- `judge.py`: LLM-as-a-Judge evaluation
- `orchestrator.py`: Benchmark execution coordinator

### Router (`src/router/`)
- `value_router.py`: Model selection logic
- `api.py`: FastAPI REST endpoints

### Dashboard (`src/dashboard/`)
- `app.py`: Streamlit application

## Adding New Features

### Adding a New LLM Provider

1. Create new client in `src/llm_clients/`:

```python
from .base import BaseLLMClient, LLMResponse

class NewProviderClient(BaseLLMClient):
    async def generate(self, prompt, max_tokens, temperature):
        # Implementation
        pass
```

2. Register in `src/llm_clients/__init__.py`

3. Update `config.yaml` with model configuration

### Adding New Prompts

Edit `data/prompts/benchmark_prompts.py`:

```python
NEW_PROMPTS = [
    {
        "id": "new_001",
        "category": "your_category",
        "prompt": "Your prompt here",
        "follow_ups": ["Follow-up question"]
    }
]
```

### Customizing Evaluation

Modify `src/benchmarking/judge.py` to adjust the evaluation prompt or scoring logic.

## Troubleshooting

### API Key Issues

```bash
# Verify environment variables are loaded
python -c "from src.utils import get_api_keys; print(get_api_keys())"
```

### Database Connection Issues

```bash
# Test database connection
python -c "from src.models import get_session; from src.utils import get_database_url; session = get_session(get_database_url()); print('Connected!')"
```

### Import Issues

```bash
# Ensure you're in the project root
pwd
# Should show: .../Intelligence-Per-Dollar

# Verify PYTHONPATH
echo $PYTHONPATH
```

## Performance Tips

1. **Use PostgreSQL for production**: SQLite is fine for testing but PostgreSQL performs better with concurrent access
2. **Rate limiting**: Be mindful of API rate limits when benchmarking multiple models
3. **Batch processing**: Process prompts in batches to avoid overwhelming APIs
4. **Caching**: The system caches performance metrics to speed up router queries

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions focused and single-purpose

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (if applicable)
5. Submit a pull request

## Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review example code in `examples.py`
