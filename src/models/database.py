"""Database models for LLM benchmark storage."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, 
    ForeignKey, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class BenchmarkRun(Base):
    """Represents a complete benchmarking run."""
    
    __tablename__ = "benchmark_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(50), nullable=False, default="running")
    total_prompts = Column(Integer)
    
    # Relationships
    results = relationship("BenchmarkResult", back_populates="run")


class BenchmarkResult(Base):
    """Stores individual LLM response results."""
    
    __tablename__ = "benchmark_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("benchmark_runs.id"), nullable=False)
    
    # Model Information
    model_name = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    
    # Prompt Information
    prompt_id = Column(String(100), nullable=False, index=True)
    prompt_text = Column(Text, nullable=False)
    prompt_category = Column(String(50), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False, default=1)
    
    # Response
    response_text = Column(Text)
    
    # Intelligence Metrics
    intelligence_score = Column(Float)  # 0-1 score from LLM-as-a-Judge
    judge_reasoning = Column(Text)
    
    # Cost Metrics
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)  # USD
    
    # Performance Metrics
    time_to_first_token = Column(Float)  # seconds
    total_latency = Column(Float, nullable=False)  # seconds
    tokens_per_second = Column(Float)
    
    # Metadata
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    error_message = Column(Text)
    raw_metadata = Column(JSON)
    
    # Relationships
    run = relationship("BenchmarkRun", back_populates="results")


class ModelPerformanceCache(Base):
    """Cached aggregated performance metrics per model and category."""
    
    __tablename__ = "model_performance_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    
    # Aggregated Metrics
    avg_intelligence_score = Column(Float)
    avg_cost_per_prompt = Column(Float)
    avg_latency = Column(Float)
    avg_tokens_per_second = Column(Float)
    
    # Statistics
    total_samples = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Value Metrics
    intelligence_per_dollar = Column(Float)  # intelligence_score / cost


def create_tables(database_url: str):
    """Create all database tables."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(database_url: str):
    """Get a database session."""
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()
