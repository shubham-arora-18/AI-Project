from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import json

from app.models import AnalysisResponse, FilteredLog
from app.services.log_processor import LogProcessor
from app.services.llm_service import LLMService

app = FastAPI(
    title="Log Analysis API",
    description="API for analyzing log files using LLM",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Log Analysis API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/analyze-logs", response_model=AnalysisResponse)
async def analyze_logs(
        file: UploadFile = File(..., description="JSON log file to analyze"),
        prompt: str = Form(..., description="Incident description or analysis prompt")
):
    """
    Upload a JSON log file and analyze it based on the provided prompt
    """

    # Validate file type
    if not file.filename.endswith(('.json', '.jsonl')):
        raise HTTPException(
            status_code=400,
            detail="File must be a JSON or JSONL file"
        )

    try:
        # Read and parse the uploaded file
        file_content = await file.read()
        logs = LogProcessor.parse_json_logs(file_content)

        if not logs:
            raise HTTPException(
                status_code=400,
                detail="No valid log entries found in the uploaded file"
            )

        # Basic filtering to reduce LLM processing cost
        filtered_logs = LogProcessor.basic_filter_logs(logs, prompt)

        # Limit the number of logs sent to LLM to control costs
        # In production, you might want to implement smarter sampling
        max_logs_for_llm = 50
        if len(filtered_logs) > max_logs_for_llm:
            filtered_logs = filtered_logs[:max_logs_for_llm]

        # Analyze logs using LLM
        llm_service = LLMService()
        highlighted_logs, llm_cost, analysis_summary = llm_service.analyze_logs(
            filtered_logs, prompt
        )

        # Prepare response
        response = AnalysisResponse(
            filtered_logs=highlighted_logs,
            total_logs_processed=len(logs),
            filtered_logs_count=len(filtered_logs),
            highlighted_logs_count=len(highlighted_logs),
            llm_cost=llm_cost,
            analysis_summary=analysis_summary
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing logs: {str(e)}"
        )


@app.get("/api-info")
async def api_info():
    """Get information about the API endpoints"""
    return {
        "endpoints": {
            "/analyze-logs": "POST - Upload log file and prompt for analysis",
            "/health": "GET - Health check",
            "/docs": "GET - Interactive API documentation",
            "/openapi.json": "GET - OpenAPI specification"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)