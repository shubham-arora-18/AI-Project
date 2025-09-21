import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_batch_size: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "200"))
    analysis_model: str = os.getenv("ANALYSIS_MODEL", "gpt-4o-mini")
    top_n_similar_logs: int = int(os.getenv("TOP_N_SIMILAR_LOGS", "100"))
    max_logs_for_analysis: int = int(os.getenv("MAX_LOGS_FOR_ANALYSIS", "100"))
    max_returned_logs: int = int(os.getenv("MAX_RETURNED_LOGS", "20"))  # NEW: configurable max returned logs

    class Config:
        env_file = ".env"


settings = Settings()