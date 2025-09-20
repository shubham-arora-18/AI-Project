from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List
import json
from app.services.log_analyzer import LogAnalyzer
from app.models import AnalysisResponse, HealthResponse

router = APIRouter()
analyzer = LogAnalyzer()


@router.get("/", response_model=dict)
async def root():
    return {"message": "Log Analysis API is running", "version": "1.0.0"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="API is running")


@router.post("/analyze-logs", response_model=AnalysisResponse)
async def analyze_logs(
        file: UploadFile = File(..., description="JSONL log file (one JSON object per line)"),
        prompt: str = Form(..., description="Incident description or query")
):
    """
    Analyze uploaded JSONL logs based on the provided prompt using semantic similarity.
    Expected format: One JSON log object per line (JSONL format).
    """
    try:
        # Parse uploaded logs
        logs = await _parse_log_file(file)

        if not logs:
            raise HTTPException(status_code=400, detail="No valid log entries found")

        # Analyze logs
        result = await analyzer.analyze_logs(logs, prompt)

        return AnalysisResponse(
            prompt=prompt,
            total_logs=result["total_logs"],
            filtered_logs_count=result["filtered_logs_count"],
            analysis=result["analysis"],
            cost_usd=result["cost_usd"],
            top_filtered_logs=result["top_filtered_logs"],
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing logs: {str(e)}")


async def _parse_log_file(file: UploadFile) -> List[dict]:
    """Parse uploaded JSONL (JSON Lines) log file"""
    content = await file.read()
    logs = []

    try:
        # Decode content and split by lines
        text_content = content.decode('utf-8').strip()

        # Handle JSONL format (one JSON object per line)
        for line_num, line in enumerate(text_content.split('\n'), 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            try:
                log_entry = json.loads(line)
                logs.append(log_entry)
            except json.JSONDecodeError as e:
                # Log the error but continue processing other lines
                print(f"Warning: Failed to parse line {line_num}: {e}")
                continue

        # Fallback: try parsing as regular JSON array if JSONL parsing yielded no results
        if not logs:
            try:
                parsed = json.loads(text_content)
                if isinstance(parsed, list):
                    logs = parsed
                elif isinstance(parsed, dict):
                    logs = [parsed]
            except json.JSONDecodeError:
                pass

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8 encoded files.")

    return logs