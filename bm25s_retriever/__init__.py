"""
BM25S Retriever - A standalone document retrieval service.
"""

from .core.retriever import BM25SRetriever, retrieve_documents

try:
    from .api.client import BM25SClient
    from .api.models import Document, RetrieveRequest, RetrieveResponse
    _HAS_API = True
except ImportError:
    _HAS_API = False
    BM25SClient = None
    Document = None
    RetrieveRequest = None
    RetrieveResponse = None

__version__ = "1.0.0"
__all__ = [
    "BM25SRetriever",
    "retrieve_documents", 
    "BM25SClient",
    "Document",
    "RetrieveRequest",
    "RetrieveResponse",
]
