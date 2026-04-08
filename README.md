# BM25S Retriever

A standalone BM25S-based document retrieval service with web UI and REST API.

## Features

- **Semantic Search**: BM25S algorithm with softmax scoring
- **Configurable**: Temperature, cutoff, and filtering settings
- **Web UI**: Document management and search testing interface
- **REST API**: JSON endpoints for integration
- **Hot Reload**: Dynamic index rebuilding without restart

## Quick Start

```bash
# Install
pip install bm25s-retriever

# Run server
bm25s-server --config settings.yaml --port 8000

# Use client
from bm25s_retriever import BM25SClient
client = BM25SClient("http://localhost:8000")
results = client.retrieve("stock market data")
```

## Configuration

```yaml
# settings.yaml
bm25s:
  temperature: 0.7
  ignore_zero: true
  llm_tools_cutoff: 8.0
  
documents:
  source: "documents.yaml"
  auto_reload: true
```

## API Endpoints

- `POST /retrieve` - Search documents
- `POST /index` - Build/rebuild index
- `GET /settings` - Get configuration
- `POST /settings` - Update configuration

## Web UI

Access `http://localhost:8000` for:
- Document management
- Search testing
- Settings configuration
- Real-time results visualization
