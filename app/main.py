from fastapi import FastAPI
from app.api.routes import router
import uvicorn


def create_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="Log Analysis API",
        description="Analyze log files using semantic similarity and LLM analysis",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Include API routes
    fastapi_app.include_router(router)

    return fastapi_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
