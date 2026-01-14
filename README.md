# 💡 Intelligence-Per-Dollar

## LLM Cost-Efficiency Benchmarking & Routing Engine

A comprehensive system that evaluates multiple Large Language Models (LLMs) to determine the highest "Intelligence-per-Dollar" for various tasks. This engine helps you automatically route requests to the most cost-efficient model that meets your quality requirements.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### 1. **Automated Benchmarking Suite**
- Runs standardized prompts across 5+ LLM APIs (GPT, Gemini, Claude, Llama)
- Supports multi-turn conversations for realistic testing
- Three categories: Coding, Summarization, Creative Writing
- Extensible prompt dataset

### 2. **Efficiency Metrics Calculation**
- **Intelligence Score**: LLM-as-a-Judge evaluation (0-1 scale)
- **Financial Cost**: Exact cost tracking based on input/output tokens
- **Latency Metrics**: Time-to-First-Token (TTFT) and tokens/second
- **Value Calculation**: Intelligence-per-Dollar ratio

### 3. **Dynamic Value-Router**
- REST API for intelligent model selection
- Automatically selects the cheapest model meeting quality thresholds
- Category-aware routing for task-specific optimization
- Historical performance analysis

### 4. **Observability Dashboard**
- Interactive Streamlit interface
- Efficiency Frontier visualization (Value Kings vs. Overpriced)
- Real-time model rankings
- Multi-metric radar charts
- Smart router interface

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL (optional, SQLite works for testing)
- API Keys for LLM providers (OpenAI, Anthropic, Google)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yadavanujkumar/Intelligence-Per-Dollar.git
cd Intelligence-Per-Dollar
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Initialize database**
```bash
python -c "from src.models import create_tables; from src.utils import get_database_url; create_tables(get_database_url())"
```

### Running the Benchmark

```bash
# Run full benchmark
python run_benchmark.py

# Test specific category
python run_benchmark.py --category coding

# Limit number of prompts
python run_benchmark.py --num-prompts 5
```

### Launch Dashboard

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

### Start Router API

```bash
python -m uvicorn src.router.api:app --reload
```

API documentation available at `http://localhost:8000/docs`

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Benchmark Orchestrator                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   GPT-5.2    │  │  Gemini 3    │  │  Claude 4.5  │ ...  │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  LLM-as-a-Judge    │
                    │   (Evaluation)     │
                    └────────────────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   PostgreSQL DB    │
                    │  (Metrics Storage) │
                    └────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  │                       │
                  ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │  Value Router    │    │    Dashboard     │
        │    (FastAPI)     │    │   (Streamlit)    │
        └──────────────────┘    └──────────────────┘
```

## 🔧 Configuration

Edit `config.yaml` to customize:

- **Model pricing** (2026 rates)
- **Benchmark parameters**
- **Router defaults**
- **Dashboard settings**

Example model configuration:
```yaml
models:
  gpt-5-2:
    provider: openai
    model_name: gpt-5.2
    input_cost_per_1k: 0.015
    output_cost_per_1k: 0.060
    max_tokens: 128000
```

## 📖 Usage Examples

### Using the Router API

```python
import requests

response = requests.post("http://localhost:8000/route", json={
    "prompt": "Write a Python function to sort a list",
    "quality_threshold": 0.85,
    "category": "coding",
    "max_cost": 0.05
})

print(response.json())
```

### Programmatic Usage

```python
from src.models import get_session, BenchmarkRepository
from src.router import ValueRouter
from src.utils import get_database_url

# Initialize
session = get_session(get_database_url())
repository = BenchmarkRepository(session)
router = ValueRouter(repository)

# Select best model
selection = router.select_model(
    quality_threshold=0.8,
    category="coding"
)

print(f"Selected: {selection['model_name']}")
print(f"Reasoning: {selection['reasoning']}")
```

## 📁 Project Structure

```
Intelligence-Per-Dollar/
├── src/
│   ├── benchmarking/       # Benchmark orchestration
│   │   ├── judge.py        # LLM-as-a-Judge evaluator
│   │   └── orchestrator.py # Main benchmark runner
│   ├── llm_clients/        # LLM API clients
│   │   ├── openai_client.py
│   │   ├── anthropic_client.py
│   │   └── google_client.py
│   ├── models/             # Database models
│   │   ├── database.py     # SQLAlchemy models
│   │   └── repository.py   # Data access layer
│   ├── router/             # Dynamic routing
│   │   ├── value_router.py # Selection logic
│   │   └── api.py          # FastAPI endpoints
│   ├── dashboard/          # Streamlit UI
│   │   └── app.py
│   └── utils/              # Utilities
│       └── config.py
├── data/
│   └── prompts/            # Benchmark prompts
│       └── benchmark_prompts.py
├── run_benchmark.py        # Main entry point
├── requirements.txt
├── config.yaml
└── README.md
```

## 🎯 Key Metrics

The system tracks and optimizes for:

1. **Intelligence Score** (0-1): Quality rating from LLM-as-a-Judge
2. **Cost per Request** ($): Total cost based on token usage
3. **Intelligence-per-Dollar**: Primary optimization metric
4. **Latency**: Response time and TTFT
5. **Tokens/Second**: Throughput measurement

## 🛠️ Tech Stack

- **Python 3.9+**: Core language
- **LangChain/LangSmith**: LLM orchestration and tracing
- **PostgreSQL/SQLite**: Benchmark storage
- **FastAPI**: Router API
- **Streamlit**: Dashboard UI
- **Plotly**: Interactive visualizations
- **SQLAlchemy**: Database ORM

## 📈 Roadmap

- [ ] Add support for more LLM providers
- [ ] Implement A/B testing framework
- [ ] Add automated cost alerting
- [ ] Support for custom evaluation criteria
- [ ] Multi-language prompt support
- [ ] Cost prediction models

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI, Anthropic, Google for LLM APIs
- LangChain community
- Streamlit team

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for cost-conscious AI development**