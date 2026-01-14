# Example API requests for the Router

## Health Check

```bash
curl http://localhost:8000/health
```

## Route Request with Quality Threshold

```bash
curl -X POST http://localhost:8000/route \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to implement bubble sort",
    "quality_threshold": 0.85,
    "category": "coding",
    "max_tokens": 1000
  }'
```

## Get Efficiency Frontier

```bash
# All models
curl http://localhost:8000/models/efficiency

# Specific category
curl http://localhost:8000/models/efficiency?category=coding
```

## Route Request with Cost Constraint

```bash
curl -X POST http://localhost:8000/route \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize the benefits of cloud computing",
    "quality_threshold": 0.75,
    "category": "summarization",
    "max_cost": 0.03
  }'
```

## Using Python Requests

```python
import requests

# Route a prompt
response = requests.post(
    "http://localhost:8000/route",
    json={
        "prompt": "Write a short poem about AI",
        "quality_threshold": 0.8,
        "category": "creative_writing",
        "max_tokens": 500
    }
)

result = response.json()
print(f"Selected Model: {result['selected_model']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Response: {result['response']}")

# Get efficiency frontier
frontier = requests.get("http://localhost:8000/models/efficiency").json()
for model in frontier['models'][:5]:
    print(f"{model['model_name']}: {model['intelligence_per_dollar']:.2f} intelligence/$")
```

## Using JavaScript/Fetch

```javascript
// Route a prompt
fetch('http://localhost:8000/route', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'Explain quantum computing in simple terms',
    quality_threshold: 0.8,
    category: 'summarization',
    max_tokens: 800
  })
})
.then(response => response.json())
.then(data => {
  console.log('Selected Model:', data.selected_model);
  console.log('Reasoning:', data.reasoning);
  console.log('Response:', data.response);
});

// Get efficiency frontier
fetch('http://localhost:8000/models/efficiency?category=coding')
  .then(response => response.json())
  .then(data => {
    console.log('Top Models:', data.models.slice(0, 3));
  });
```
