"""Benchmark prompt dataset."""

# Coding Prompts
CODING_PROMPTS = [
    {
        "id": "code_001",
        "category": "coding",
        "prompt": "Write a Python function that implements binary search on a sorted array.",
        "follow_ups": [
            "Now modify it to handle duplicate elements and return all indices.",
            "Add error handling and input validation."
        ]
    },
    {
        "id": "code_002",
        "category": "coding",
        "prompt": "Create a REST API endpoint in Python using FastAPI for user authentication.",
        "follow_ups": [
            "Add JWT token generation and validation.",
            "Implement rate limiting for the endpoint."
        ]
    },
    {
        "id": "code_003",
        "category": "coding",
        "prompt": "Write a JavaScript function to debounce user input in a search box.",
        "follow_ups": [
            "Convert it to TypeScript with proper types.",
            "Add unit tests using Jest."
        ]
    },
    {
        "id": "code_004",
        "category": "coding",
        "prompt": "Implement a LRU cache in Python with O(1) get and put operations.",
        "follow_ups": [
            "Add thread-safety to the implementation.",
            "Extend it to support TTL (time-to-live) for cache entries."
        ]
    },
    {
        "id": "code_005",
        "category": "coding",
        "prompt": "Create a SQL query to find the top 10 customers by total purchase amount.",
        "follow_ups": [
            "Modify it to include customers who made purchases in the last 30 days only.",
            "Add a column showing the percentage contribution of each customer."
        ]
    },
]

# Summarization Prompts
SUMMARIZATION_PROMPTS = [
    {
        "id": "summ_001",
        "category": "summarization",
        "prompt": "Summarize the key points of quantum computing for a business executive in 3 paragraphs.",
        "follow_ups": [
            "Now explain the potential business applications.",
            "What are the main risks and challenges?"
        ]
    },
    {
        "id": "summ_002",
        "category": "summarization",
        "prompt": "Provide a concise summary of the impacts of climate change on global agriculture.",
        "follow_ups": [
            "What are the proposed solutions?",
            "Which regions are most affected?"
        ]
    },
    {
        "id": "summ_003",
        "category": "summarization",
        "prompt": "Summarize the main features of the transformer architecture in machine learning.",
        "follow_ups": [
            "Explain the attention mechanism in simple terms.",
            "What are the advantages over RNNs?"
        ]
    },
    {
        "id": "summ_004",
        "category": "summarization",
        "prompt": "Summarize the key economic indicators that predict a recession.",
        "follow_ups": [
            "Which indicator is most reliable?",
            "How do central banks respond to these indicators?"
        ]
    },
    {
        "id": "summ_005",
        "category": "summarization",
        "prompt": "Provide an executive summary of blockchain technology and its use cases.",
        "follow_ups": [
            "What are the main challenges to adoption?",
            "Compare public vs private blockchains."
        ]
    },
]

# Creative Writing Prompts
CREATIVE_WRITING_PROMPTS = [
    {
        "id": "creative_001",
        "category": "creative_writing",
        "prompt": "Write a short story about a time traveler who accidentally changes history.",
        "follow_ups": [
            "Continue the story showing the consequences.",
            "Write an alternate ending where they fix the timeline."
        ]
    },
    {
        "id": "creative_002",
        "category": "creative_writing",
        "prompt": "Compose a poem about the beauty of artificial intelligence.",
        "follow_ups": [
            "Now write it from the AI's perspective.",
            "Convert it into a haiku."
        ]
    },
    {
        "id": "creative_003",
        "category": "creative_writing",
        "prompt": "Write a product description for a revolutionary smart home device.",
        "follow_ups": [
            "Create a catchy tagline and slogan.",
            "Write a 30-second video script for the ad."
        ]
    },
    {
        "id": "creative_004",
        "category": "creative_writing",
        "prompt": "Create a dialogue between two characters debating the ethics of AI.",
        "follow_ups": [
            "Add a third character who offers a compromise.",
            "Write the closing argument from each side."
        ]
    },
    {
        "id": "creative_005",
        "category": "creative_writing",
        "prompt": "Write an email pitching a startup idea to potential investors.",
        "follow_ups": [
            "Add a section addressing potential objections.",
            "Create a compelling subject line."
        ]
    },
]

# Combine all prompts
ALL_PROMPTS = CODING_PROMPTS + SUMMARIZATION_PROMPTS + CREATIVE_WRITING_PROMPTS


def get_prompts_by_category(category: str):
    """Get all prompts for a specific category."""
    return [p for p in ALL_PROMPTS if p["category"] == category]


def get_all_prompts():
    """Get all benchmark prompts."""
    return ALL_PROMPTS
