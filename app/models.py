from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class LogEntry(BaseModel):
    clusterUid: str
    containerId: str
    containerName: str
    log: str
    namespace: str
    podName: str
    stream: str
    timestamp: str

class AnalysisRequest(BaseModel):
    prompt: str

class FilteredLog(BaseModel):
    log_entry: LogEntry
    relevance_score: float
    relevance_reason: str

class AnalysisResponse(BaseModel):
    filtered_logs: List[FilteredLog]
    total_logs_processed: int
    filtered_logs_count: int
    highlighted_logs_count: int
    llm_cost: float
    analysis_summary: str