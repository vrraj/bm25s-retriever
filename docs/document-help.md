# BM25S Retriever Documentation

## Document Management

This guide shows you how to manage documents in the BM25S Retriever system.

### Default Document Location

By default, BM25S Retriever looks for documents in a YAML file located at:
```
documents.yaml
```

This file should be in the root directory of your project or the location specified in your configuration.

### YAML Document Format

Create a `documents.yaml` file with the following structure:

```yaml
documents:
  - id: "doc1"
    title: "Introduction to Machine Learning"
    content: "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
    keywords: ["machine learning", "AI", "algorithms", "data"]
    metadata:
      category: "education"
      difficulty: "beginner"
  
  - id: "doc2"
    title: "Python Programming Basics"
    content: "Python is a high-level programming language known for its simplicity and readability."
    keywords: ["python", "programming", "coding", "development"]
    metadata:
      category: "programming"
      difficulty: "beginner"
  
  - id: "doc3"
    title: "Data Science Fundamentals"
    content: "Data science combines statistics, mathematics, and computer science to extract insights from data."
    keywords: ["data science", "statistics", "analytics", "insights"]
    metadata:
      category: "data science"
      difficulty: "intermediate"
```

### Adding Documents via Web UI

1. **Access the Web Interface**
   - Open your browser and navigate to `http://localhost:9200`
   - Click on the "Documents" tab

2. **Add a New Document**
   - Click the "Add Document" button
   - Fill in the form:
     - **Document ID**: Unique identifier (e.g., "my-doc-1")
     - **Title**: Document title
     - **Content**: Full document content
     - **Keywords**: Comma-separated keywords (e.g., "python, coding, tutorial")
   - Click "Save Document"

3. **Manage Documents**
   - View all documents in the table at the bottom
   - Delete documents using the × button
   - Reload index to refresh the search engine

### Adding Documents via cURL

#### Add a Single Document

```bash
curl -X POST http://localhost:9200/index \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "api-doc-1",
        "title": "REST API Design",
        "content": "REST APIs should be stateless and use standard HTTP methods.",
        "keywords": ["REST", "API", "HTTP", "web services"],
        "metadata": {
          "category": "web development"
        }
      }
    ],
    "rebuild": false
  }'
```

#### Add Multiple Documents

```bash
curl -X POST http://localhost:9200/index \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "api-doc-2",
        "title": "HTTP Methods",
        "content": "GET for retrieving, POST for creating, PUT for updating, DELETE for removing.",
        "keywords": ["HTTP", "GET", "POST", "PUT", "DELETE"],
        "metadata": {}
      },
      {
        "id": "api-doc-3",
        "title": "JSON Format",
        "content": "JSON is a lightweight data interchange format that is easy for humans to read and write.",
        "keywords": ["JSON", "data format", "serialization"],
        "metadata": {}
      }
    ],
    "rebuild": false
  }'
```

#### Rebuild Index

```bash
curl -X POST http://localhost:9200/index \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "new-doc",
        "title": "New Document",
        "content": "This document will rebuild the entire index.",
        "keywords": ["new", "rebuild"],
        "metadata": {}
      }
    ],
    "rebuild": true
  }'
```

#### Get All Documents

```bash
curl -X GET http://localhost:9200/documents
```

#### Delete a Document

```bash
curl -X DELETE http://localhost:9200/documents/api-doc-1
```

#### Reload Documents from YAML

```bash
curl -X POST http://localhost:9200/documents/reload
```

### Searching Documents via API

#### Basic Search

```bash
curl -X POST http://localhost:9200/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "temperature": 0.7,
    "llm_tools_cutoff": 8.0,
    "ignore_zero": true
  }'
```

#### Advanced Search with Custom Parameters

```bash
curl -X POST http://localhost:9200/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python programming",
    "temperature": 1.5,
    "llm_tools_cutoff": 5.0,
    "ignore_zero": false
  }'
```

#### Search via Python

```python
import requests
import json

def search_documents(query, temperature=0.7, cutoff=8.0, ignore_zero=True):
    """Search documents using the BM25S retriever API."""
    
    url = "http://localhost:9200/retrieve"
    
    payload = {
        "query": query,
        "temperature": temperature,
        "llm_tools_cutoff": cutoff,
        "ignore_zero": ignore_zero
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if result["success"]:
            print(f"Found {len(result['documents'])} documents:")
            print(f"Total retrieved: {result['total_retrieved']}")
            print(f"Cutoff percentage: {result['cutoff_percentage']}")
            
            for i, doc in enumerate(result["documents"], 1):
                print(f"\n--- Document {i} ---")
                print(f"ID: {doc['id']}")
                print(f"Title: {doc['title']}")
                print(f"Content: {doc['content'][:100]}...")
                print(f"Keywords: {', '.join(doc['keywords'])}")
                print(f"BM25 Score: {doc['bm25_score']:.3f}")
                print(f"Softmax Score: {doc['softmax_score']:.4f}")
                print(f"Relevance: {doc['softmax_score']*100:.2f}%")
        else:
            print(f"Search failed: {result['message']}")
            
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")

# Example usage
if __name__ == "__main__":
    # Basic search
    search_documents("machine learning")
    
    # Search with custom parameters
    search_documents(
        query="python programming",
        temperature=1.2,
        cutoff=10.0,
        ignore_zero=False
    )
```

#### Search Parameters

- **query** (required): The search query string
- **temperature** (optional, default: 0.7): Controls softmax uniformity (0.1-10.0)
  - Lower values (0.1-1.0): More focused, higher contrast
  - Higher values (1.0-10.0): More uniform distribution
- **llm_tools_cutoff** (optional, default: 8.0): Minimum softmax percentage (0-100)
- **ignore_zero** (optional, default: true): Filter out documents with zero BM25 scores

#### Response Format

```json
{
  "success": true,
  "message": "Documents retrieved successfully",
  "documents": [
    {
      "id": "doc1",
      "title": "Document Title",
      "content": "Document content...",
      "keywords": ["keyword1", "keyword2"],
      "metadata": {},
      "bm25_score": 2.456,
      "softmax_score": 0.1234
    }
  ],
  "total_retrieved": 15,
  "cutoff_percentage": 8.0,
  "settings": {
    "temperature": 0.7,
    "ignore_zero": true,
    "llm_tools_cutoff": 8.0
  }
}
```

### Adding Documents via Python

#### Using the Python API

```python
import requests
import json

# Base URL
base_url = "http://localhost:9200"

# Add a single document
def add_document():
    document = {
        "id": "python-doc-1",
        "title": "Python Lists",
        "content": "Lists are mutable sequences in Python that can hold items of different types.",
        "keywords": ["python", "lists", "mutable", "sequences"],
        "metadata": {
            "language": "python",
            "topic": "data structures"
        }
    }
    
    response = requests.post(
        f"{base_url}/index",
        json={
            "documents": [document],
            "rebuild": False
        }
    )
    
    if response.status_code == 200:
        print("Document added successfully!")
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Add multiple documents
def add_multiple_documents():
    documents = [
        {
            "id": "python-doc-2",
            "title": "Python Dictionaries",
            "content": "Dictionaries are key-value pairs that provide fast lookups.",
            "keywords": ["python", "dictionaries", "key-value", "mappings"],
            "metadata": {}
        },
        {
            "id": "python-doc-3",
            "title": "Python Functions",
            "content": "Functions are reusable blocks of code that perform specific tasks.",
            "keywords": ["python", "functions", "reusable", "code"],
            "metadata": {}
        }
    ]
    
    response = requests.post(
        f"{base_url}/index",
        json={
            "documents": documents,
            "rebuild": False
        }
    )
    
    return response.json()

# Get all documents
def get_all_documents():
    response = requests.get(f"{base_url}/documents")
    return response.json()

# Delete a document
def delete_document(document_id):
    response = requests.delete(f"{base_url}/documents/{document_id}")
    return response.json()

# Example usage
if __name__ == "__main__":
    # Add documents
    add_document()
    result = add_multiple_documents()
    print("Multiple documents added:", result)
    
    # List all documents
    docs = get_all_documents()
    print(f"Total documents: {len(docs['documents'])}")
    
    # Delete a document
    delete_result = delete_document("python-doc-1")
    print("Delete result:", delete_result)
```

#### Using the BM25S Retriever Directly

```python
from bm25s_retriever.core.retriever import BM25SRetriever, Document

# Create retriever instance
retriever = BM25SRetriever()

# Create documents
documents = [
    Document(
        id="direct-doc-1",
        title="Direct API Usage",
        content="You can use the BM25S Retriever directly in Python code.",
        keywords=["BM25S", "retriever", "python", "direct"],
        metadata={"source": "python_api"}
    ),
    Document(
        id="direct-doc-2",
        title="Document Objects",
        content="Document objects encapsulate content and metadata for indexing.",
        keywords=["document", "object", "indexing", "metadata"],
        metadata={"source": "python_api"}
    )
]

# Add documents to index
retriever.add_documents(documents)

# Search documents
results = retriever.retrieve_documents("python programming")
print("Search results:", results)

# Get document count
count = retriever.get_document_count()
print(f"Total documents: {count}")
```

### Best Practices

1. **Document IDs**: Use unique, descriptive IDs that follow a consistent pattern
2. **Content**: Provide meaningful content that accurately represents the document
3. **Keywords**: Include relevant terms that might not appear in the content
4. **Metadata**: Use metadata to categorize and filter documents
5. **Index Management**: Use `rebuild: false` for incremental updates and `rebuild: true` for complete reindexing

### Troubleshooting

- **Documents not appearing**: Check that the document ID is unique
- **Search not working**: Try reloading the index
- **API errors**: Verify JSON format and required fields
- **Performance**: Consider rebuilding the index after many incremental updates

For more information, refer to the main documentation or check the API endpoints at `http://localhost:9200/docs`.
