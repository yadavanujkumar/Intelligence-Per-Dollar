"""Dynamic value router for selecting optimal models."""

from typing import Optional, Dict, Any
from ..models import BenchmarkRepository


class ValueRouter:
    """Routes requests to the most cost-efficient model meeting quality thresholds."""
    
    def __init__(
        self,
        repository: BenchmarkRepository,
        default_threshold: float = 0.8,
        min_samples: int = 5,
        fallback_model: str = "gpt-5-2"
    ):
        self.repository = repository
        self.default_threshold = default_threshold
        self.min_samples = min_samples
        self.fallback_model = fallback_model
    
    def select_model(
        self,
        quality_threshold: Optional[float] = None,
        category: Optional[str] = None,
        max_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Select the best model based on quality threshold and constraints.
        
        Args:
            quality_threshold: Minimum intelligence score required (0-1)
            category: Task category (coding, summarization, creative_writing)
            max_cost: Maximum cost per request in USD
            
        Returns:
            Dict with selected model and reasoning
        """
        
        threshold = quality_threshold or self.default_threshold
        
        # Get best model from repository
        best_model = self.repository.get_best_model_for_threshold(
            quality_threshold=threshold,
            category=category
        )
        
        if not best_model:
            return {
                "model_name": self.fallback_model,
                "reasoning": f"No model meets threshold {threshold:.2f}, using fallback",
                "quality_threshold": threshold,
                "category": category
            }
        
        # Get performance details
        performance = self.repository.get_model_performance(
            model_name=best_model,
            category=category
        )
        
        # Check if we have enough data
        if performance and performance["total_samples"] < self.min_samples:
            return {
                "model_name": self.fallback_model,
                "reasoning": f"Insufficient data for {best_model} (only {performance['total_samples']} samples), using fallback",
                "quality_threshold": threshold,
                "category": category
            }
        
        # Check cost constraint
        if max_cost and performance and performance["avg_cost"] > max_cost:
            return {
                "model_name": self.fallback_model,
                "reasoning": f"{best_model} exceeds max cost ${max_cost:.4f}, using fallback",
                "quality_threshold": threshold,
                "category": category
            }
        
        return {
            "model_name": best_model,
            "reasoning": f"Best value: {performance['intelligence_per_dollar']:.2f} intelligence/$",
            "quality_threshold": threshold,
            "category": category,
            "expected_quality": performance["avg_intelligence_score"],
            "expected_cost": performance["avg_cost"],
            "expected_latency": performance["avg_latency"],
            "intelligence_per_dollar": performance["intelligence_per_dollar"]
        }
    
    def get_efficiency_frontier(
        self,
        category: Optional[str] = None
    ) -> list:
        """
        Get all models ordered by efficiency for visualization.
        
        Returns list of models with their performance metrics.
        """
        from sqlalchemy import and_
        from ..models.database import ModelPerformanceCache
        
        query = self.repository.session.query(ModelPerformanceCache)
        
        if category:
            query = query.filter(ModelPerformanceCache.category == category)
        
        results = query.filter(
            ModelPerformanceCache.total_samples >= self.min_samples
        ).all()
        
        frontier = []
        for result in results:
            frontier.append({
                "model_name": result.model_name,
                "category": result.category,
                "avg_intelligence_score": result.avg_intelligence_score,
                "avg_cost": result.avg_cost_per_prompt,
                "avg_latency": result.avg_latency,
                "intelligence_per_dollar": result.intelligence_per_dollar,
                "total_samples": result.total_samples
            })
        
        # Sort by intelligence per dollar (descending)
        frontier.sort(key=lambda x: x["intelligence_per_dollar"], reverse=True)
        
        return frontier
