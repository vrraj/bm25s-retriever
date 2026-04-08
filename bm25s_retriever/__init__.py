"""
BM25S Retriever - A standalone document retrieval service.
"""

from .core.retriever import BM25SRetriever, retrieve_documents
from .api.client import BM25SClient
from .api.models import Document, RetrieveRequest, RetrieveResponse

__version__ = "1.0.0"
__all__ = [
    "BM25SRetriever",
    "retrieve_documents", 
    "BM25SClient",
    "Document",
    "RetrieveRequest",
    "RetrieveResponse",
]
