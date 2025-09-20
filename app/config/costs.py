"""
Centralized cost configuration for OpenAI models.
All pricing is per 1,000 tokens and based on OpenAI's official pricing.
Last updated: September 2025 - Based on official OpenAI documentation
"""

from typing import Dict


class ModelCosts:
    """Centralized cost configuration for all OpenAI models"""

    # Embedding models (cost per 1K tokens) - VERIFIED FROM SEARCH
    EMBEDDING_COSTS = {
        "text-embedding-3-small": 0.00002,
        "text-embedding-3-large": 0.00013,
        "text-embedding-ada-002": 0.0001,
    }

    CHAT_COMPLETION_COSTS = {
        "gpt-3.5-turbo": {
            "input": 0.0005,
            "output": 0.0015
        },
        "gpt-3.5-turbo-0125": {  # Latest version
            "input": 0.0005,
            "output": 0.0015
        },
        "gpt-3.5-turbo-instruct": {
            "input": 0.0015,
            "output": 0.002
        },
        "gpt-4": {
            "input": 0.03,
            "output": 0.06
        },
        "gpt-4-32k": {
            "input": 0.06,
            "output": 0.12
        },
        "gpt-4-turbo": {
            "input": 0.01,
            "output": 0.03
        },
        "gpt-4-turbo-preview": {
            "input": 0.01,
            "output": 0.03
        },
        "gpt-4o": {
            "input": 0.005,
            "output": 0.015
        },
        "gpt-4o-mini": {
            "input": 0.00015,
            "output": 0.0006
        }
    }

    @classmethod
    def get_embedding_cost(cls, model: str) -> float:
        """Get cost per 1K tokens for embedding model"""
        return cls.EMBEDDING_COSTS.get(model, 0.0)

    @classmethod
    def get_chat_completion_cost(cls, model: str) -> Dict[str, float]:
        """Get input/output costs per 1K tokens for chat completion model"""
        return cls.CHAT_COMPLETION_COSTS.get(model, {"input": 0.0, "output": 0.0})

    @classmethod
    def calculate_embedding_cost(cls, model: str, token_count: int) -> float:
        """Calculate total embedding cost"""
        cost_per_1k = cls.get_embedding_cost(model)
        return (token_count * cost_per_1k) / 1000

    @classmethod
    def calculate_chat_completion_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate total chat completion cost"""
        costs = cls.get_chat_completion_cost(model)
        input_cost = (input_tokens * costs["input"]) / 1000
        output_cost = (output_tokens * costs["output"]) / 1000
        return input_cost + output_cost

    @classmethod
    def estimate_token_count(cls, text: str) -> int:
        """
        Estimate token count for text.

        OpenAI's rule: ~1 token per 0.75 words
        Therefore: 1 word ≈ 1/0.75 = 1.33 tokens

        For more accuracy, consider using tiktoken library in production.
        """
        word_count = len(text.split())
        # Convert words to tokens: words * (1 token / 0.75 words) = words / 0.75
        return int(word_count / 0.75)  # Correct calculation: words ÷ 0.75


# For convenience, create an instance
model_costs = ModelCosts()
