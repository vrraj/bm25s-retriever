# vrraj-bm25s-retriever

[![PyPI - Version](https://img.shields.io/pypi/v/vrraj-bm25s-retriever?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/vrraj-bm25s-retriever/)
[![GitHub Release](https://img.shields.io/github/v-release/vrraj/bm25s-retriever?label=github%20release&color=orange&logo=github)](https://github.com/vrraj/bm25s-retriever/releases)
![CI Status](https://github.com/vrraj/bm25s-retriever/actions/workflows/ci.yml/badge.svg)

> **Development and Demo UI:**  
> This repository ships with a FastAPI-powered **Interactive Web Interface** for testing BM25S document retrieval, managing document collections, and configuring search parameters. See **[Development And Demo UI](#development-and-demo-ui)** section below for details and setup instructions.

Provider-agnostic BM25S document retrieval service with **web interface + REST API** for semantic document search, indexing, and management with **normalized outputs** (scores, rankings, metadata).

High-performance BM25S-based document retrieval with stemming, softmax scoring, and configurable filtering.

- **PyPI:** https://pypi.org/project/vrraj-bm25s-retriever
- **GitHub:** https://github.com/vrraj/bm25s-retriever
- **Documentation:** https://vrraj.github.io/bm25s-retriever/

## Install

```bash
pip install vrraj-bm25s-retriever
```

## What you get

- **Fast BM25S retrieval** with English stemming and stopwords filtering
- **Web Interface** for document management and search testing
- **REST API** for programmatic access and integration
- **Softmax scoring** with temperature-controlled relevance
- **Configurable filtering** (zero-relevance, cutoff thresholds)
- **Document management** (add, view, delete via API/UI)
- **YAML-based document storage** with hot-reload support
- **Normalized response format** across all interfaces

## Quickstart

> **Default configuration:** Ships with example financial documents and sensible defaults
> 
> **Setup:** The package includes example documents and configuration files

```bash
# Start the server with default configuration
bm25s-server --config settings.yaml

# Access the web interface
open http://localhost:9200
```

### Option A: Ready-to-use example script
Download and run a ready-to-use example script for document management and search:

```bash
curl -L -O https://raw.githubusercontent.com/vrraj/bm25s-retriever/main/examples/bm25s_basic_usage.py

python bm25s_basic_usage.py
```

### Option B: Call the API directly

```python
from bm25s_retriever import BM25SClient

client = BM25SClient("http://localhost:9200")

# Search documents
results = client.retrieve("cryptocurrency data")
print(f"Found {len(results['documents'])} documents")

# Add a document
client.add_document({
    "id": "my_doc",
    "title": "My Document",
    "content": "Document content here...",
    "keywords": ["keyword1", "keyword2"]
})
```

### Discover available documents

The package ships with example documents. To list them:

```python
from bm25s_retriever import BM25SClient

client = BM25SClient("http://localhost:9200")
documents = client.get_documents()

for doc in documents['documents']:
    print(f"{doc['id']}: {doc['title']}")
```

## Interactive Web Interface

The package includes a FastAPI web interface with document management, search testing, and configuration controls.

![BM25S Retriever Web Interface](https://github.com/vrraj/bm25s-retriever/blob/main/images/bm25s_web_interface.png)

## Public API (overview)

- `client.retrieve(...) -> Dict` - Search documents with BM25S scoring
- `client.add_document(...) -> Dict` - Add new document to index
- `client.get_documents() -> Dict` - Get all documents
- `client.delete_document(doc_id) -> Dict` - Remove document from index
- `client.get_settings() -> Dict` - Get current configuration
- `client.update_settings(...) -> Dict` - Update search parameters

>**For complete method signatures, parameter details, and full response structures**, see: [api-reference.md](https://github.com/vrraj/bm25s-retriever/blob/main/docs/api-reference.md)

### Search Response Schema

```python
{
  "success": bool,
  "message": str,
  "documents": List[Dict],
  "total_retrieved": int,
  "cutoff_percentage": float,
  "settings": {
    "temperature": float,
    "ignore_zero": bool,
    "llm_tools_cutoff": float
  }
}
```

### Document Schema

```python
{
  "id": str,
  "title": str,
  "content": str,
  "keywords": List[str],
  "metadata": Dict[str, Any]
}
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

## Documentation & References

- **Complete API Reference:** [api-reference.md](https://github.com/vrraj/bm25s-retriever/blob/main/docs/api-reference.md)
- **Configuration Guide:** [configuration.md](https://github.com/vrraj/bm25s-retriever/blob/main/docs/configuration.md)
- **Ready to use Examples:** [examples](https://github.com/vrraj/bm25s-retriever/tree/main/examples)
- **Dev notes:** [development.md](https://github.com/vrraj/bm25s-retriever/blob/main/docs/development.md)

---

## Usage Examples (PyPI)

Install the package from PyPI, then use these examples for common patterns like search, document management, and configuration.

### Document Search - Basic Pattern

```python
from bm25s_retriever import BM25SClient

client = BM25SClient("http://localhost:9200")

# Simple search
results = client.retrieve("cryptocurrency")
for doc in results['documents']:
    print(f"{doc['title']}: {doc['bm25_score']}")
```

### Document Management

```python
from bm25s_retriever import BM25SClient

client = BM25SClient("http://localhost:9200")

# Add document
result = client.add_document({
    "id": "tax_guide",
    "title": "Tax Guide for ESPP",
    "content": "Complete guide to ESPP tax adjustments...",
    "keywords": ["tax", "ESPP", "broker", "cost basis"],
    "metadata": {"category": "finance", "priority": "high"}
})

# Get all documents
documents = client.get_documents()
print(f"Total documents: {documents['count']}")

# Delete document
client.delete_document("tax_guide")
```

### Advanced Search with Parameters

```python
from bm25s_retriever import BM25SClient

client = BM25SClient("http://localhost:9200")

# Search with custom parameters
results = client.retrieve(
    query="financial data analysis",
    temperature=0.5,        # Lower temperature = more selective
    ignore_zero=True,        # Filter zero-relevance results
    llm_tools_cutoff=5.0     # 5% minimum softmax score
)

print(f"Found {len(results['documents'])} relevant documents")
```

### Direct Library Usage

```python
from bm25s_retriever import BM25SRetriever, Document

# Create retriever instance
retriever = BM25SRetriever()

# Add documents
doc = Document(
    id="research_paper",
    title="Machine Learning Research",
    content="Recent advances in deep learning...",
    keywords=["ML", "AI", "neural networks"],
    metadata={"type": "academic", "year": 2025}
)

retriever.add_documents([doc])

# Search
results = retriever.retrieve_documents("machine learning")
for doc in results['documents']:
    print(f"Score: {doc['bm25_score']:.2f} - {doc['title']}")
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

// Search documents
async function searchDocuments(query) {
  const response = await fetch('/retrieve', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query })
  });
  
  return await response.json();
}
```

### REST API Usage

```bash
# Add document
curl -X POST http://localhost:9200/documents \
  -H "Content-Type: application/json" \
  -d '{
    "id": "financial_report",
    "title": "Q1 Financial Report",
    "content": "Quarterly financial performance...",
    "keywords": ["finance", "quarterly", "report"]
  }'

# Search documents
curl -X POST http://localhost:9200/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "financial performance", "temperature": 0.7}'

# Get all documents
curl http://localhost:9200/documents

# Delete document
curl -X DELETE http://localhost:9200/documents/financial_report
```

## BM25S Algorithm

The retriever uses BM25S with the following features:

- **Stemming**: English stemming for word normalization (e.g., "trading" -> "trade")
- **Stopwords**: Common words filtered out to improve relevance
- **Softmax Scoring**: Temperature-controlled relevance scoring
- **Cutoff Filtering**: Results below threshold are filtered out

### Scoring Formula
```
BM25S Score + Softmax(temperature) + Cutoff Filter
```

### Temperature Control
- **Low temperature (0.1-0.5)**: More selective, higher confidence results
- **High temperature (0.8-2.0)**: More uniform distribution across results

## Development And Demo UI

Run the **demo UI** (runs on port 9200) or **customize** the code.

1. Clone the repository and install dependencies.

```bash
git clone https://github.com/vrraj/bm25s-retriever.git
cd bm25s-retriever
pip install -e ".[dev]"
```

2. Start the application.

```bash
bm25s-server --config settings.yaml
```

3. Open the demo UI:

- http://localhost:9200/

### Manual start (optional)

If you prefer not to use the CLI command:

```bash
uvicorn bm25s_retriever.main:app --reload --port 9200
```

The Web Interface will be available at:

```
http://localhost:9200/
```

### For Developers: Running Tests

#### Install Dev dependencies

```bash
pip install -e ".[dev]"
```

#### Run Tests

```bash
pytest
pytest -m integration
pytest -m "integration or unit"
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
|-- examples/                  # Usage examples
|-- docs/                      # Documentation
```

## Environment Variables

Supported environment variables:

```bash
# Server configuration
BM25S_HOST=0.0.0.0
BM25S_PORT=9200
BM25S_RELOAD=false

# Document configuration
BM25S_DOCUMENTS_PATH=./documents.yaml
BM25S_AUTO_RELOAD=true

# BM25S defaults
BM25S_TEMPERATURE=0.7
BM25S_IGNORE_ZERO=true
BM25S_CUTOFF=8.0
```

## Supported Document Formats

### YAML Format (Primary)
```yaml
documents:
  - id: "unique_doc_id"
    title: "Document Title"
    content: "Full document content here..."
    keywords: ["keyword1", "keyword2"]
    metadata:
      category: "finance"
      author: "John Doe"
```

### JSON API Format
```json
{
  "id": "unique_doc_id",
  "title": "Document Title",
  "content": "Full document content here...",
  "keywords": ["keyword1", "keyword2"],
  "metadata": {
    "category": "finance",
    "author": "John Doe"
  }
}
```

### Python Object Format
```python
from bm25s_retriever import Document

doc = Document(
    id="unique_doc_id",
    title="Document Title",
    content="Full document content here...",
    keywords=["keyword1", "keyword2"],
    metadata={"category": "finance"}
)
```

## Performance Considerations

### Index Size
- **Small (<100 docs)**: <1 second indexing, instant search
- **Medium (100-1000 docs)**: 1-3 seconds indexing, <100ms search
- **Large (1000+ docs)**: 3-10 seconds indexing, 100-500ms search

### Memory Usage
- Documents stored in memory for fast access
- BM25S index also in memory
- Approx. 1KB per document + index overhead

### Optimization Tips
- Use meaningful keywords for better matching
- Keep document content focused and relevant
- Adjust temperature based on use case (exploration vs precision)
- Use cutoff filtering to reduce noise in results

## Adding Custom Documents

### Via Web UI
1. Click "Add Document" button
2. Fill in document details
3. Click "Save Document"

### Via API
```python
client.add_document({
    "id": "custom_doc",
    "title": "Custom Document",
    "content": "Your content here...",
    "keywords": ["tag1", "tag2"]
})
```

### Via YAML File
Add to `documents.yaml` and reload:
```yaml
documents:
  - id: "custom_doc"
    title: "Custom Document"
    content: "Your content here..."
    keywords: ["tag1", "tag2"]
```

## Development

This is a standalone package. Development happens directly in this repo.

```bash
pip install -e .
bm25s-server --config settings.yaml
```

## License

This project is licensed under the MIT License.
