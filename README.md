# Log Analysis Backend

A FastAPI-based backend service for analyzing JSON log files using LLM (OpenAI GPT) to identify relevant incidents and calculate usage costs.

## Features

- 📁 **File Upload**: Supports JSON and JSONL log file formats
- 🔍 **Smart Filtering**: Two-stage filtering (keyword + LLM-based relevance)
- 🤖 **LLM Analysis**: Uses OpenAI GPT to analyze log relevance to incidents
- 💰 **Cost Tracking**: Calculates and displays LLM API usage costs
- 📚 **Auto Documentation**: FastAPI generates interactive API docs
- ⚡ **Async Processing**: Fast, non-blocking file processing

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone/Download the project**
   ```bash
   mkdir log-analysis-backend
   cd log-analysis-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Create the directory structure**
   ```
   log-analysis-backend/
   ├── app/
   │   ├── __init__.py (empty file)
   │   ├── main.py
   │   ├── models.py
   │   ├── services/
   │   │   ├── __init__.py (empty file)
   │   │   ├── log_processor.py
   │   │   └── llm_service.py
   │   └── utils/
   │       ├── __init__.py (empty file)
   │       └── cost_calculator.py
   ├── requirements.txt
   ├── .env
   ├── .gitignore
   ├── test_logs.jsonl
   └── README.md
   ```

6. **Run the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Usage

### API Endpoints

- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Testing the API

1. **Via Swagger UI** (Recommended)
   - Go to http://localhost:8000/docs
   - Click on `/analyze-logs` endpoint
   - Upload `test_logs.jsonl` and enter prompt: "cart service is crashing"

2. **Via cURL**
   ```bash
   curl -X POST "http://localhost:8000/analyze-logs" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_logs.jsonl" \
     -F "prompt=cart service is crashing, check logs"
   ```

### Expected Response Format

```json
{
  "filtered_logs": [
    {
      "log_entry": {
        "clusterUid": "111de5db-ce60-429a-9b8b-d7e9652ef3c2",
        "containerId": "abc123",
        "containerName": "cartservice",
        "log": "2025-09-02 23:12:42 - cartservice - ERROR: Database connection failed",
        "namespace": "oteldemo",
        "podName": "oteldemo-cartservice-xyz",
        "stream": "stderr",
        "timestamp": "1756854762000000000"
      },
      "relevance_score": 0.9,
      "relevance_reason": "Shows database connection error in cart service"
    }
  ],
  "total_logs_processed": 5,
  "filtered_logs_count": 3,
  "highlighted_logs_count": 2,
  "llm_cost": 0.001234,
  "analysis_summary": "Found 2 critical issues in cart service: database connection failure and memory overflow crash"
}
```

## Architecture

### Components

- **FastAPI App** (`app/main.py`): Main application with endpoints
- **Models** (`app/models.py`): Pydantic data models for validation
- **Log Processor** (`app/services/log_processor.py`): Handles file parsing and basic filtering
- **LLM Service** (`app/services/llm_service.py`): OpenAI integration for log analysis
- **Cost Calculator** (`app/utils/cost_calculator.py`): Calculates LLM usage costs

### Processing Flow

1. **File Upload**: User uploads JSON/JSONL log file
2. **Parsing**: Convert file content to structured LogEntry objects
3. **Pre-filtering**: Basic keyword filtering to reduce LLM costs
4. **LLM Analysis**: OpenAI analyzes filtered logs for incident relevance
5. **Response**: Return highlighted logs with relevance scores and costs

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Cost Control

The application limits LLM processing to 50 logs maximum to control costs. You can adjust this in `app/main.py`:

```python
max_logs_for_llm = 50  # Adjust as needed
```

## Development

### Adding New Log Formats

Extend `LogProcessor.parse_json_logs()` in `app/services/log_processor.py` to support additional formats.

### Customizing LLM Analysis

Modify the prompt in `LLMService.analyze_logs()` in `app/services/llm_service.py` to change analysis behavior.

### Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Malformed JSON data
- OpenAI API errors
- Missing environment variables

## Deployment Considerations

- Set up proper authentication/rate limiting for production
- Consider async processing for large files
- Implement proper logging and monitoring
- Use environment-specific API keys
- Add database storage for analysis history

## Cost Management

- Pre-filtering reduces unnecessary LLM calls
- Configurable limits on logs sent to LLM
- Real-time cost calculation and display
- Uses cost-effective GPT-3.5-turbo by default

## Support

For issues or questions:
1. Check the interactive API docs at `/docs`
2. Verify your OpenAI API key is set correctly
3. Test with the provided `test_logs.jsonl` file
4. Check server logs for detailed error messages