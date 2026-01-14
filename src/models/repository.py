"""Data access layer for benchmark storage and retrieval."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from .database import BenchmarkRun, BenchmarkResult, ModelPerformanceCache


class BenchmarkRepository:
    """Repository for managing benchmark data."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_run(self, total_prompts: int) -> BenchmarkRun:
        """Create a new benchmark run."""
        run = BenchmarkRun(
            started_at=datetime.utcnow(),
            status="running",
            total_prompts=total_prompts
        )
        self.session.add(run)
        self.session.commit()
        return run
    
    def complete_run(self, run_id: int):
        """Mark a benchmark run as completed."""
        run = self.session.query(BenchmarkRun).filter_by(id=run_id).first()
        if run:
            run.completed_at = datetime.utcnow()
            run.status = "completed"
            self.session.commit()
    
    def save_result(self, result_data: Dict[str, Any]) -> BenchmarkResult:
        """Save a benchmark result."""
        result = BenchmarkResult(**result_data)
        self.session.add(result)
        self.session.commit()
        return result
    
    def get_model_performance(
        self, 
        model_name: str, 
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated performance metrics for a model."""
        query = self.session.query(
            func.avg(BenchmarkResult.intelligence_score).label("avg_intelligence"),
            func.avg(BenchmarkResult.total_cost).label("avg_cost"),
            func.avg(BenchmarkResult.total_latency).label("avg_latency"),
            func.count(BenchmarkResult.id).label("total_samples")
        ).filter(BenchmarkResult.model_name == model_name)
        
        if category:
            query = query.filter(BenchmarkResult.prompt_category == category)
        
        result = query.first()
        
        if result and result.avg_intelligence and result.avg_cost:
            return {
                "model_name": model_name,
                "category": category,
                "avg_intelligence_score": float(result.avg_intelligence),
                "avg_cost": float(result.avg_cost),
                "avg_latency": float(result.avg_latency or 0),
                "total_samples": result.total_samples,
                "intelligence_per_dollar": float(result.avg_intelligence) / float(result.avg_cost) if result.avg_cost > 0 else 0
            }
        
        return None
    
    def get_all_results(
        self, 
        limit: int = 1000,
        model_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[BenchmarkResult]:
        """Get benchmark results with optional filtering."""
        query = self.session.query(BenchmarkResult)
        
        if model_name:
            query = query.filter(BenchmarkResult.model_name == model_name)
        if category:
            query = query.filter(BenchmarkResult.prompt_category == category)
        
        return query.order_by(BenchmarkResult.timestamp.desc()).limit(limit).all()
    
    def update_performance_cache(self):
        """Update the performance cache for all models and categories."""
        # Get all unique combinations of model and category
        combinations = self.session.query(
            BenchmarkResult.model_name,
            BenchmarkResult.prompt_category
        ).distinct().all()
        
        for model_name, category in combinations:
            perf = self.get_model_performance(model_name, category)
            
            if perf:
                # Check if cache entry exists
                cache = self.session.query(ModelPerformanceCache).filter(
                    and_(
                        ModelPerformanceCache.model_name == model_name,
                        ModelPerformanceCache.category == category
                    )
                ).first()
                
                if cache:
                    # Update existing cache
                    cache.avg_intelligence_score = perf["avg_intelligence_score"]
                    cache.avg_cost_per_prompt = perf["avg_cost"]
                    cache.avg_latency = perf["avg_latency"]
                    cache.total_samples = perf["total_samples"]
                    cache.intelligence_per_dollar = perf["intelligence_per_dollar"]
                    cache.last_updated = datetime.utcnow()
                else:
                    # Create new cache entry
                    cache = ModelPerformanceCache(
                        model_name=model_name,
                        category=category,
                        avg_intelligence_score=perf["avg_intelligence_score"],
                        avg_cost_per_prompt=perf["avg_cost"],
                        avg_latency=perf["avg_latency"],
                        total_samples=perf["total_samples"],
                        intelligence_per_dollar=perf["intelligence_per_dollar"],
                        last_updated=datetime.utcnow()
                    )
                    self.session.add(cache)
        
        self.session.commit()
    
    def get_best_model_for_threshold(
        self, 
        quality_threshold: float,
        category: Optional[str] = None
    ) -> Optional[str]:
        """Get the cheapest model that meets the quality threshold."""
        query = self.session.query(ModelPerformanceCache).filter(
            ModelPerformanceCache.avg_intelligence_score >= quality_threshold
        )
        
        if category:
            query = query.filter(ModelPerformanceCache.category == category)
        
        # Order by cost (ascending) to get cheapest first
        result = query.order_by(ModelPerformanceCache.avg_cost_per_prompt.asc()).first()
        
        return result.model_name if result else None
