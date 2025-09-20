from typing import List
import openai
from fastapi import HTTPException
from app.config import settings


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

    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
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

    def estimate_embedding_cost(self, total_tokens: int) -> float:
        """Estimate cost for embeddings (text-embedding-3-small: $0.00002 per 1K tokens)"""
        return (total_tokens * 0.00002) / 1000
