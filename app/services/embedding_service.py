from typing import List
import openai
from fastapi import HTTPException
from app.config.settings import settings
from app.config.costs import model_costs


class EmbeddingService:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.model = settings.embedding_model

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            response = await openai.Embedding.acreate(
                model=self.model,
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting embedding: {str(e)}")

    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 200) -> List[List[float]]:
        """Get embeddings for multiple texts in batches"""
        try:
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = await openai.Embedding.acreate(
                    model=self.model,
                    input=batch
                )
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)

            return all_embeddings
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting batch embeddings: {str(e)}")

    def calculate_embedding_cost(self, texts: List[str], prompt: str = None) -> float:
        """Calculate actual embedding cost based on text content using centralized costs"""
        total_tokens = 0

        # Count tokens for all log texts
        for text in texts:
            total_tokens += model_costs.estimate_token_count(text)

        # Count tokens for prompt if provided
        if prompt:
            total_tokens += model_costs.estimate_token_count(prompt)

        # Use centralized cost calculation
        return round(model_costs.calculate_embedding_cost(self.model, total_tokens), 6)

    def estimate_embedding_cost(self, total_tokens: int) -> float:
        """Estimate cost for embeddings using centralized costs"""
        return model_costs.calculate_embedding_cost(self.model, total_tokens)