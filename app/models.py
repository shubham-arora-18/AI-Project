from pydantic import BaseModel
from typing import List, Dict, Any, Optional


# Remove rigid LogEntry model, use flexible dict instead
class AnalysisRequest(BaseModel):
    prompt: str
    logs: List[Dict[str, Any]]  # Flexible - any JSON structure


class AnalysisResponse(BaseModel):
    prompt: str
    total_logs: int
    filtered_logs_count: int
    analysis: str
    embedding_cost_usd: float
    llm_cost_usd: float
    total_cost_usd: float
    top_filtered_logs: List[Dict[str, Any]]  # Flexible - any JSON structure
    success: bool


class HealthResponse(BaseModel):
    status: str
    message: str


class EmbeddingCost(BaseModel):
    embedding_tokens: int
    embedding_cost: float
    analysis_tokens: int
    analysis_cost: float
    total_cost: float
