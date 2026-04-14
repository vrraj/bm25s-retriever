# BM25S Retriever

A standalone BM25S-based document retrieval service with web UI and REST API.

## Features

- **BM25S Search**: Advanced document retrieval with BM25S algorithm
- **Stemming Support**: English stemming for improved matching
- **Softmax Scoring**: Temperature-controlled relevance scoring
- **Web UI**: Complete document management and search interface
- **REST API**: Full JSON API for programmatic access
- **Document Management**: Add, view, delete documents via API/UI
- **Configuration**: Flexible settings for retrieval parameters

## Installation

```bash
# Clone and install
git clone <repository-url>
cd bm25s-retriever
pip install -e ".[dev]"

# Or install from PyPI (when published)
pip install bm25s-retriever
```

## Quick Start

```bash
# Start the server
bm25s-server --config settings.yaml

# Access web UI
open http://localhost:9200

# Use Python client
from bm25s_retriever import BM25SClient
client = BM25SClient("http://localhost:9200")
results = client.retrieve("cryptocurrency data")
print(f"Found {len(results['documents'])} documents")
```

## Configuration

### settings.yaml
```yaml
bm25s:
  temperature: 0.7          # Softmax temperature control
  ignore_zero: true         # Filter out zero-score results
  llm_tools_cutoff: 8.0     # Softmax cutoff percentage

documents:
  source: "documents.yaml" # Document source file
  auto_reload: true        # Auto-reload on file changes

server:
  host: "0.0.0.0"         # Server host
  port: 9200              # Server port
  reload: false           # Auto-reload on code changes
```

### documents.yaml
```yaml
documents:
  - id: "example_doc"
    title: "Example Document"
    content: "This is an example document for testing BM25S retrieval."
    keywords: ["example", "test", "document"]
    metadata:
      category: "example"
      updated: "2025-04-13"
```

## API Endpoints

### Search
```bash
curl -X POST http://localhost:9200/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "cryptocurrency", "temperature": 0.7}'
```

### Document Management
```bash
# Get all documents
curl http://localhost:9200/documents

# Add document
curl -X POST http://localhost:9200/documents \
  -H "Content-Type: application/json" \
  -d '{
    "id": "new_doc",
    "title": "New Document",
    "content": "Document content here",
    "keywords": ["keyword1", "keyword2"]
  }'

# Delete document
curl -X DELETE http://localhost:9200/documents/new_doc
```

### Settings
```bash
# Get current settings
curl http://localhost:9200/settings

# Update settings
curl -X POST http://localhost:9200/settings \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 0.8,
    "ignore_zero": true,
    "llm_tools_cutoff": 10.0
  }'
```

## Web UI

Access `http://localhost:9200` for:

- **Search Tab**: Test document retrieval with real-time results
- **Documents Tab**: View, add, and delete documents
- **Settings Tab**: Configure BM25S parameters
- **Status Tab**: Monitor system health and statistics

## Python Usage

### Direct Library Usage
```python
from bm25s_retriever import BM25SRetriever, Document

# Create retriever
retriever = BM25SRetriever()

# Add documents
doc = Document(
    id="test_doc",
    title="Test Document",
    content="This is a test document for BM25S retrieval.",
    keywords=["test", "document"]
)
retriever.add_documents([doc])

# Search
results = retriever.retrieve_documents("test query")
for doc in results['documents']:
    print(f"Found: {doc['title']} (score: {doc['bm25_score']})")
```

### Client Usage
```python
from bm25s_retriever import BM25SClient

client = BM25SClient("http://localhost:9200")

# Simple search
results = client.retrieve("market analysis")

# Advanced search with parameters
results = client.retrieve(
    query="financial data",
    temperature=0.5,
    ignore_zero=True,
    llm_tools_cutoff=5.0
)

# Get documents
documents = client.get_documents()

# Add document programmatically
result = client.add_document({
    "id": "new_doc",
    "title": "New Document",
    "content": "Content here...",
    "keywords": ["keyword"]
})
```

### JavaScript/Frontend Usage
```javascript
// Open add document modal
document.getElementById('add-document-modal').style.display = 'block';

// Add document via API
async function addDocument(docData) {
  const response = await fetch('/documents', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(docData)
  });
  
  return await response.json();
}

// Usage
const result = await addDocument({
  id: "my_doc",
  title: "My Document",
  content: "Document content here...",
  keywords: ["keyword1", "keyword2"]
});
```

### REST API Usage
```bash
# Add document via curl
curl -X POST http://localhost:9200/documents \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_doc",
    "title": "My Document",
    "content": "Document content here...",
    "keywords": ["keyword1", "keyword2"]
  }'

# Search documents
curl -X POST http://localhost:9200/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "cryptocurrency", "temperature": 0.7}'
```

## BM25S Algorithm

The retriever uses BM25S with the following features:

- **Stemming**: English stemming for word normalization
- **Stopwords**: Common words filtered out
- **Softmax Scoring**: Temperature-controlled relevance scoring
- **Cutoff Filtering**: Results below threshold are filtered out

### Scoring Formula
```
BM25S Score + Softmax(temperature) + Cutoff Filter
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black bm25s_retriever/
ruff check bm25s_retriever/

# Start development server
bm25s-server --config settings.yaml --reload
```

## Project Structure

```
bm25s-retriever/
|-- bm25s_retriever/
|   |-- core/
|   |   |-- retriever.py      # BM25S retrieval logic
|   |   |-- config.py         # Configuration management
|   |-- api/
|   |   |-- routes.py          # FastAPI endpoints
|   |   |-- models.py          # Pydantic models
|   |-- ui/
|   |   |-- templates/         # HTML templates
|   |   |-- static/           # CSS/JS assets
|   |-- cli.py                # Command-line interface
|-- documents.yaml             # Example documents
|-- settings.yaml              # Configuration
|-- pyproject.toml            # Package metadata
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: See inline code documentation
- **Examples**: Check `examples/` directory for usage samples
