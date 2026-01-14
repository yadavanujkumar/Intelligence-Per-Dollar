"""FastAPI router API for dynamic model selection."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

from ..models import get_session, BenchmarkRepository
from .value_router import ValueRouter
from ..llm_clients import LLMClientFactory

load_dotenv()

app = FastAPI(
    title="LLM Cost-Efficiency Router",
    description="Dynamic router that selects the most cost-efficient LLM based on quality thresholds",
    version="1.0.0"
)


class RouterRequest(BaseModel):
    """Request model for router API."""
    prompt: str = Field(..., description="The prompt to send to the LLM")
    quality_threshold: Optional[float] = Field(
        0.8, 
        ge=0.0, 
        le=1.0,
        description="Minimum quality score required (0.0-1.0)"
    )
    category: Optional[str] = Field(
        None,
        description="Task category: coding, summarization, or creative_writing"
    )
    max_cost: Optional[float] = Field(
        None,
        ge=0.0,
        description="Maximum cost per request in USD"
    )
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature")


class RouterResponse(BaseModel):
    """Response model for router API."""
    selected_model: str
    reasoning: str
    response: str
    metadata: Dict[str, Any]


# Initialize router
database_url = os.getenv("DATABASE_URL", "sqlite:///./benchmark.db")
session = get_session(database_url)
repository = BenchmarkRepository(session)
router = ValueRouter(repository)


@app.post("/route", response_model=RouterResponse)
async def route_request(request: RouterRequest):
    """
    Route a request to the optimal model based on quality threshold.
    
    The router automatically selects the cheapest model that historically
    meets the specified quality threshold for the given task type.
    """
    
    try:
        # Select the best model
        selection = router.select_model(
            quality_threshold=request.quality_threshold,
            category=request.category,
            max_cost=request.max_cost
        )
        
        model_name = selection["model_name"]
        
        # Here you would actually call the selected model
        # For now, we'll return the selection info
        
        return RouterResponse(
            selected_model=model_name,
            reasoning=selection["reasoning"],
            response=f"[Response from {model_name} would be here]",
            metadata={
                "quality_threshold": request.quality_threshold,
                "category": request.category,
                "selection_details": selection
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/efficiency")
async def get_efficiency_frontier(category: Optional[str] = None):
    """
    Get the efficiency frontier showing all models' performance.
    
    Returns models ordered by intelligence-per-dollar ratio.
    """
    
    try:
        frontier = router.get_efficiency_frontier(category=category)
        return {
            "category": category,
            "models": frontier
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "llm-cost-efficiency-router"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
