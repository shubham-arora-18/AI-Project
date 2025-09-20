import time
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.config.settings import settings


class LogAnalyzer:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    def flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        Recursively flattens nested dicts into dot-notation keys.
        Example:
        {"a": {"b": 1}} -> {"a.b": 1}
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def extract_text_from_log(self, orig_log: Dict[str, Any]) -> str:
        """
        Flexibly extract text from any log format for embedding.
        This function tries to intelligently combine all text fields.
        """
        text_parts = []
        text_parts_2 = []

        log_attr = self.flatten_dict(orig_log)

        # Common field names to prioritize (order matters for relevance)
        priority_fields = [
            'message', 'msg', 'log', 'content', 'description',
            'error', 'exception', 'stacktrace', 'stack_trace',
            'level', 'severity', 'priority',
            'service', 'component', 'module', 'source',
            'containerName', 'container_name', 'pod', 'podName',
            'namespace', 'cluster', 'host', 'hostname',
            'stream', 'logger', 'category', 'body'
        ]

        included_log_attrs = dict()

        # First, add priority fields if they exist
        for key, value in log_attr.items():
            for field in priority_fields:
                if key in included_log_attrs:
                    break
                if field in key and isinstance(value, (str, int, float)):
                    text_parts.append(f"{key}:{str(value)}")
                    included_log_attrs[key] = value

        un_included_log_attrs = {k: v for k, v in log_attr.items() if k not in included_log_attrs}

        # Second, add non priority fields
        for key, value in un_included_log_attrs.items():
            for field in priority_fields:
                if key in included_log_attrs:
                    break
                if value and field not in key and not self._is_id_or_timestamp_field(key):
                    text_parts_2.append(f"{key}:{str(value)}")
                    included_log_attrs[key] = value

        text_parts.extend(text_parts_2)

        return ' | '.join(text_parts) if text_parts else str(log_attr)

    def _is_id_or_timestamp_field(self, field_name: str) -> bool:
        """Check if field is likely an ID or timestamp (less useful for semantic search)"""
        id_indicators = ['id', 'uid', 'guid', 'uuid', 'hash', 'time', 'stamp', 'date']
        return any(indicator in field_name.lower() for indicator in id_indicators)

    def prepare_log_texts(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Prepare log entries for embedding by extracting meaningful text"""
        return [self.extract_text_from_log(log) for log in logs]

    async def filter_logs_by_similarity(
            self,
            logs: List[Dict[str, Any]],
            prompt: str,
            top_n: int = None
    ) -> (List[Dict[str, Any]], float):
        """Filter logs based on semantic similarity to the prompt"""
        if not logs:
            return []

        top_n = top_n or settings.top_n_similar_logs

        # Prepare texts for embedding
        log_texts = self.prepare_log_texts(logs)

        embedding_cost = self.embedding_service.calculate_embedding_cost(log_texts, prompt)

        # Get embeddings
        prompt_embedding = await self.embedding_service.get_embedding(prompt)
        log_embeddings = await self.embedding_service.get_embeddings_batch(log_texts)

        # Calculate cosine similarity
        similarities = self._calculate_similarities(prompt_embedding, log_embeddings)

        # Get top N most similar logs
        top_indices = np.argsort(similarities)[::-1][:top_n]

        # Add similarity scores to logs and return
        filtered_logs = []
        for idx in top_indices:
            log_with_score = logs[idx].copy()
            log_with_score['_similarity_score'] = float(similarities[idx])
            log_with_score['_extracted_text'] = log_texts[idx]  # For debugging
            filtered_logs.append(log_with_score)

        return filtered_logs, embedding_cost

    def _calculate_similarities(self, prompt_embedding: List[float], log_embeddings: List[List[float]]) -> np.ndarray:
        """Calculate cosine similarity between prompt and log embeddings"""
        prompt_embedding_array = np.array(prompt_embedding).reshape(1, -1)
        # converts array to 2d array for cosine comparison
        log_embeddings_array = np.array(log_embeddings)  # already a 2d array

        similarities = cosine_similarity(prompt_embedding_array, log_embeddings_array)[0]
        return similarities

    async def analyze_logs(self, logs: List[Dict[str, Any]], prompt: str) -> Dict[str, Any]:
        """Complete log analysis pipeline with detailed timing"""

        # Time the filtering stage
        filter_start = time.time()
        filtered_logs, embedding_cost = await self.filter_logs_by_similarity(logs, prompt)
        filter_time = time.time() - filter_start

        # Time the LLM analysis stage
        llm_start = time.time()
        llm_result = await self.llm_service.analyze_logs(filtered_logs, prompt)
        llm_time = time.time() - llm_start

        # Calculate total cost (embedding + LLM)
        total_cost = embedding_cost + llm_result["cost"]

        return {
            "total_logs": len(logs),
            "filtered_logs_count": len(filtered_logs),
            "analysis": llm_result["analysis"],
            "total_cost_usd": total_cost,
            "embedding_cost_usd": embedding_cost,
            "llm_cost_usd": llm_result["cost"],
            "logs_analyzed": llm_result["logs_analyzed"],
            "top_filtered_logs": filtered_logs[:settings.max_returned_logs],
            # Optional: Add stage timing breakdown
            "timing_breakdown": {
                "embedding_filter_seconds": round(filter_time, 3),
                "llm_analysis_seconds": round(llm_time, 3)
            }
        }
