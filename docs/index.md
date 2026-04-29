---
layout: default
title: "BM25S Retriever: Fast Lexical Retrieval"
description: "A lightweight BM25S-powered lexical retrieval package for Python applications, REST services, LLM systems, and MCP-based tool workflows."
---

# vrraj-bm25s-retriever


<p align="left">
  <a href="https://pypi.org/project/vrraj-bm25s-retriever/">
    <img src="https://img.shields.io/pypi/v/vrraj-bm25s-retriever?color=blue&logo=pypi&logoColor=white" alt="PyPI - Version">
  </a>
  <a href="https://github.com/vrraj/bm25s-retriever/releases">
    <img src="https://img.shields.io/github/v-release/vrraj/bm25s-retriever?label=github%20release&color=orange&logo=github" alt="GitHub Release">
  </a>
  <a href="https://github.com/vrraj/bm25s-retriever/actions">
    <img src="https://github.com/vrraj/bm25s-retriever/actions/workflows/ci.yml/badge.svg" alt="CI Status">
  </a>
</p>

A lightweight **BM25S-powered lexical retrieval package** for Python applications, REST services, LLM systems, and MCP-based tool workflows.

Use it to search documents, route LLM tool calls, filter MCP-discovered tools, and build fast lexical retrieval layers without running a vector database.

## Key Features

- **Fast Lexical Retrieval**: BM25S with PyStemmer for efficient, deterministic text search

- **Softmax Scoring**: Configurable temperature-based scoring with cutoff filtering

- **Multiple Usage Modes**: Python API, REST service, or HTTP client

- **MCP Integration**: Filter MCP-discovered tools before passing to LLM

- **Demo Web UI**: Interactive interface for testing and tuning retrieval parameters

## Install

```bash
pip install vrraj-bm25s-retriever
```

## Quick Example

```python
from bm25s_retriever import BM25SRetriever, Document

retriever = BM25SRetriever()

retriever.add_documents([
    Document(
        id="create_order",
        title="Create Order",
        content="Place a buy or sell order for a stock or equity trade.",
        keywords=["place order", "buy order", "sell order", "stock trade"],
        metadata={"category": "trading", "type": "tool"},
    ),
])

results = retriever.retrieve("place a limit buy order")

for doc in results.documents:
    print(doc.title, doc.softmax_score)
```

## Links

- [Github Repository](https://github.com/vrraj/bm25s-retriever)

- [PyPI Package](https://pypi.org/project/vrraj-bm25s-retriever/)

## Detailed Documentation

- [Full Documentation (README)](https://github.com/vrraj/bm25s-retriever#readme)

- [API Reference](api-reference.html) - Complete API documentation and usage examples

## Interactive Demo UI

The GitHub repo includes a FastAPI-powered **Demo Web UI** for testing retrieval behavior, inspecting ranked results, adding documents, and tuning search parameters.

See setup instructions in the README: [Demo Web UI](https://github.com/vrraj/bm25s-retriever#demo-web-ui)
