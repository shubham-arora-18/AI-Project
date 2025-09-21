# Log Analysis Backend

A FastAPI-based backend service that uses semantic similarity and LLM analysis to identify relevant log entries for incident investigation. Built with flexibility, cost optimization, and production readiness in mind.

## Documentation

- [📋 Design Decisions and Tradeoffs](DESIGN_DECISIONS.md)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key
- 8GB+ RAM (for large log files)

### Installation
```bash
# Clone repository
git clone https://github.com/shubham-arora-18/AI-Project.git
cd AI-Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp sample.env .env
# Edit .env with your OpenAI API key
# Run the application
python -m app.main
# Once the server is started, the documentation can be found here: http://localhost:8000/docs
```

### Testing
```bash
# Using curl
curl --request POST \
  --url http://localhost:8000/analyze-logs \
  --header 'Content-Type: multipart/form-data' \
  --form file=@test_logs.jsonl \
  --form 'prompt=cart service is crashing'
```
