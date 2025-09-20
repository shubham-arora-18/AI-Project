# Log Analysis Backend

A FastAPI-based backend service that uses semantic similarity and LLM analysis to identify relevant log entries for incident investigation. Built with flexibility, cost optimization in mind.

## 🚀 Features

- **📁 Universal Log Support**: Flexible JSONL parser that works with any log format as long as it is in json format
- **🧠 Semantic Filtering**: Uses OpenAI embeddings for intelligent log relevance detection
- **🤖 LLM Analysis**: GPT-powered incident analysis with actionable insights
- **💰 Cost Optimization**: Transparent cost tracking with embedding + LLM breakdown
- **⚡ High Performance**: Async processing with configurable batch sizes
- **📚 Auto Documentation**: Interactive OpenAPI docs at `/docs`

## 🏗️ Architecture & Design Decisions

### Core Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File Upload   │ -> │  Semantic Filter │ -> │   LLM Analysis  │
│    (JSONL)      │    │   (Embeddings)   │    │      (GPT)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         v                       v                       v
    Parse Any JSON         Find Relevant Logs      Generate Insights
    Log Format            (Top N Similar)         (Root Cause + Actions)
```

### 🎯 Design Decisions & Tradeoffs

#### 1. **Two-Stage Processing Pipeline**
- **Decision**: Embedding-based filtering → LLM analysis
- **Rationale**: Cost optimization - only send relevant logs to expensive LLM
- **Tradeoff**: Additional latency for embedding calls vs. massive cost savings

#### 2. **Flexible Schema-Free Design**
- **Decision**: No rigid log models, dynamic field extraction
- **Rationale**: Support any log format (Kubernetes, nginx, custom apps)
- **Tradeoff**: Additional cost for embeddings vs. Maximum flexibility

#### 3. **Centralized Cost Management**
- **Decision**: Single `costs.py` file for all pricing
- **Rationale**: Easy maintenance when OpenAI updates pricing
- **Tradeoff**: Slight complexity vs. single source of truth

#### 4. **Async-First Architecture**
- **Decision**: All I/O operations are async
- **Rationale**: Better concurrency and resource utilization
- **Tradeoff**: Code complexity vs. performance

#### 5. **Configurable Processing Limits**
- **Decision**: Environment-based limits for logs processed/returned
- **Rationale**: Cost control and response size management
- **Tradeoff**: Potential information loss vs. predictable costs

## 🤖 Model Selection & Rationale

### Embedding Model: `text-embedding-3-small`
- **Why**: Best cost/performance ratio at $0.00002 per 1K tokens
- **Alternative**: `text-embedding-3-large` for higher accuracy (6.5x more expensive)
- **Use Case**: Perfect for log similarity matching where speed > precision

### LLM Model: `gpt-3.5-turbo` (Default)
- **Why**: Excellent cost/performance for log analysis
- **Cost**: $0.0005 input / $0.0015 output per 1K tokens
- **Alternative**: `gpt-4o-mini` for complex reasoning (3x more expensive)
- **Configurable**: Can switch via `ANALYSIS_MODEL` environment variable

### Model Comparison

| Model | Input Cost | Output Cost | Best For |
|-------|------------|-------------|----------|
| gpt-3.5-turbo | $0.0005 | $0.0015 | General log analysis |
| gpt-4o-mini | $0.00015 | $0.0006 | High-volume, simple tasks |
| gpt-4o | $0.005 | $0.015 | Complex incident analysis |

## 🎯 Semantic Similarity vs. Keyword Filtering

### Why Embeddings Over Keywords

#### Traditional Keyword Approach ❌
```python
# Brittle - misses semantic matches
if "error" in log or "crash" in log or "fail" in log:
    return True  # Only catches exact words
```

#### Our Embedding Approach ✅
```python
# Intelligent - understands meaning
similarity = cosine_similarity(prompt_embedding, log_embedding)
# Catches: "timeout", "exception", "service unavailable", etc.
```

### Semantic Understanding Examples

| Prompt | Traditional Match | Embedding Match |
|--------|------------------|-----------------|
| "cart service error" | ❌ "cart timeout" | ✅ "cart timeout" |
| "database issues" | ❌ "connection refused" | ✅ "connection refused" |
| "payment failure" | ❌ "transaction declined" | ✅ "transaction declined" |

### Flexible Log Format Support

The embedding approach automatically adapts to any log structure:

```json
// Kubernetes logs
{"level": "ERROR", "message": "Pod crashed", "namespace": "prod"}

// Nginx logs  
{"status": 500, "request": "GET /api", "error": "upstream timeout"}

// Custom app logs
{"severity": "high", "component": "billing", "description": "Payment failed"}
```

All get intelligently processed without code changes!

## ⚡ Performance Optimizations

### Current Implementation
- **Batch Processing**: 200 logs per embedding API call
- **Sequential Batches**: Process batches one after another
- **Memory Efficient**: Stream processing for large files

### 🚀 Potential Improvements

#### **Parallel Embedding Calls**
```python
# Current: Sequential batches
for batch in batches:
    embeddings = await get_embeddings_batch(batch)

# Optimized: Parallel batches
import asyncio
tasks = [get_embeddings_batch(batch) for batch in batches]
all_embeddings = await asyncio.gather(*tasks)
```

**Benefits**: 3-5x faster for large log files
**Limitation**: OpenAI rate limits (varies by account tier)

## 📊 Cost Analysis & Optimization

### Cost Breakdown Example
For 1,000 logs with 50-word average length:

```
Embedding Cost:
- Tokens: 1,000 logs × 67 tokens = 67,000 tokens
- Cost: 67K × $0.00002 / 1K = $0.00134

LLM Analysis (top 100 logs):
- Input: 5,000 tokens × $0.0005 / 1K = $0.0025
- Output: 300 tokens × $0.0015 / 1K = $0.00045
- Total: $0.00295

Total Cost: $0.00429 (~$0.004 per 1,000 logs)
```

### Cost Optimization Strategies
1. **Intelligent Filtering**: Only process top N similar logs
2. **Batch Optimization**: Reduce API calls through batching
3. **Model Selection**: Choose appropriate model for task complexity

## 🔧 Configuration & Environment

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your-api-key

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-small      # Embedding model choice
ANALYSIS_MODEL=gpt-3.5-turbo               # LLM model choice

# Processing Limits
TOP_N_SIMILAR_LOGS=100                     # Logs to consider for LLM
MAX_LOGS_FOR_ANALYSIS=50                   # Logs sent to LLM
MAX_RETURNED_LOGS=20                       # Logs in API response

# Performance Tuning
EMBEDDING_BATCH_SIZE=200                   # Batch size for embeddings
```

### Feature Additions
1. **Multi-file Analysis**: Compare logs across multiple files
2. **Time Series Analysis**: Detect patterns over time
3. **Alert Integration**: Connect to monitoring systems

### Enterprise Features
1. **Authentication**: API key management
2. **Rate Limiting**: Per-user quotas
3. **Audit Logging**: Track all analysis requests
4. **Multi-tenancy**: Isolated log processing

## 🛡️ Security Considerations

### Data Privacy
- Logs are processed in memory only
- No persistent storage of log data
- OpenAI API respects data retention policies

### API Security
- Input validation on all endpoints
- File size limits to prevent DoS
- Rate limiting (production deployment)

## 🐛 Troubleshooting

### Common Issues

1. **High Costs**
   - Reduce `MAX_LOGS_FOR_ANALYSIS`
   - Switch to `gpt-4o-mini`
   - Implement better filtering

2. **Slow Performance**
   - Increase `EMBEDDING_BATCH_SIZE`
   - Use better tier account's open api key  

3. **Poor Results**
   - Increase `TOP_N_SIMILAR_LOGS`
   - Use `gpt-4o` for complex analysis
   - Improve prompt engineering

### Performance Benchmarks
- 10,000 logs(considering, log file shared in assignment, 10000*250 = 2.5Mil Input Tokens): ~240 seconds, ~$0.025