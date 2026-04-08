"""
BM25S document retriever implementation.
"""

import bm25s
import Stemmer
import math
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from .config import BM25SSettings


@dataclass
class Document:
    """Document representation for BM25S indexing."""
    id: str
    title: str
    content: str
    keywords: List[str] = None
    metadata: Dict[str, Any] = None


class BM25SRetriever:
    """BM25S-based document retrieval system with softmax scoring and cutoff filtering."""
    
    def __init__(self, settings: BM25SSettings = None):
        self.settings = settings or BM25SSettings()
        self.stemmer = Stemmer.Stemmer("english")
        self.documents: List[Document] = []
        self.retriever = None
        self._load_and_index_documents()
    
    def _load_and_index_documents(self, documents: List[Document] = None):
        """Load documents and build BM25S index."""
        if documents:
            self.documents = documents
        
        corpus = []
        formatted_docs = []
        
        for doc in self.documents:
            # Build description for BM25S indexing
            desc_parts = []
            if doc.title:
                desc_parts.append(doc.title)
            
            if doc.content:
                desc_parts.append(doc.content)
            
            if doc.keywords:
                desc_parts.extend([f"keyword: {kw}" for kw in doc.keywords])
            
            full_desc = " ".join(desc_parts)
            
            doc_data = {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "keywords": doc.keywords or [],
                "metadata": doc.metadata or {},
                "desc": full_desc
            }
            
            formatted_docs.append(doc_data)
            corpus.append(full_desc)
        
        self.documents = formatted_docs
        
        # Build BM25S index
        if corpus:
            corpus_tokens = bm25s.tokenize(corpus, stopwords="en", stemmer=self.stemmer)
            self.retriever = bm25s.BM25(method="lucene")
            self.retriever.index(corpus_tokens)
    
    def _calculate_softmax(self, scores: List[float], temperature: float = 1.0) -> List[float]:
        """Calculate softmax probabilities with temperature scaling."""
        if not scores:
            return []
        
        # Scale scores by temperature
        scaled_scores = [score / temperature for score in scores]
        
        # Subtract max for numerical stability
        max_score = max(scaled_scores)
        exp_scores = [math.exp(score - max_score) for score in scaled_scores]
        
        # Calculate softmax probabilities
        sum_exp = sum(exp_scores)
        if sum_exp == 0:
            return [0.0] * len(scores)
        
        return [exp_score / sum_exp for exp_score in exp_scores]
    
    def retrieve_documents(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Retrieve documents based on query using BM25S with softmax scoring.
        
        Args:
            query: Search query
            **kwargs: Optional overrides for settings
            
        Returns:
            Dictionary with retrieval results and metadata
        """
        if not self.retriever:
            return {
                "success": False,
                "message": "No documents indexed",
                "documents": [],
                "scores": [],
                "softmax_scores": []
            }
        
        # Override settings with kwargs
        temperature = kwargs.get("temperature", self.settings.temperature)
        ignore_zero = kwargs.get("ignore_zero", self.settings.ignore_zero)
        llm_tools_cutoff = kwargs.get("llm_tools_cutoff", self.settings.llm_tools_cutoff)
        
        # Tokenize query
        query_tokens = bm25s.tokenize([query], stopwords="en", stemmer=self.stemmer)[0]
        
        # Retrieve scores
        scores, indices = self.retriever.retrieve(query_tokens, k=len(self.documents))
        
        # Prepare results
        results = []
        all_scores = []
        retrieved_docs = []
        
        for i, (score, idx) in enumerate(zip(scores, indices)):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["bm25_score"] = float(score)
                retrieved_docs.append(doc)
                all_scores.append(float(score))
        
        # Apply ignore_zero filter
        if ignore_zero:
            filtered_docs = []
            filtered_scores = []
            for doc, score in zip(retrieved_docs, all_scores):
                if score > 0:
                    filtered_docs.append(doc)
                    filtered_scores.append(score)
            retrieved_docs = filtered_docs
            all_scores = filtered_scores
        
        # Calculate softmax scores
        softmax_scores = self._calculate_softmax(all_scores, temperature)
        
        # Apply cutoff filtering
        cutoff_percentage = llm_tools_cutoff / 100.0
        filtered_results = []
        
        for doc, score, softmax_score in zip(retrieved_docs, all_scores, softmax_scores):
            doc["softmax_score"] = softmax_score
            if softmax_score >= cutoff_percentage:
                filtered_results.append(doc)
        
        # Sort by softmax score (descending)
        filtered_results.sort(key=lambda x: x["softmax_score"], reverse=True)
        
        return {
            "success": True,
            "message": f"Retrieved {len(filtered_results)} documents",
            "documents": filtered_results,
            "total_retrieved": len(retrieved_docs),
            "cutoff_percentage": cutoff_percentage,
            "settings": {
                "temperature": temperature,
                "ignore_zero": ignore_zero,
                "llm_tools_cutoff": llm_tools_cutoff
            }
        }
    
    def add_documents(self, documents: List[Document]):
        """Add new documents and rebuild index."""
        self.documents.extend(documents)
        self._load_and_index_documents()
    
    def rebuild_index(self, documents: List[Document] = None):
        """Rebuild the BM25S index."""
        self._load_and_index_documents(documents)
    
    def get_document_count(self) -> int:
        """Get number of indexed documents."""
        return len(self.documents)
    
    def get_settings(self) -> BM25SSettings:
        """Get current settings."""
        return self.settings
    
    def update_settings(self, settings: BM25SSettings):
        """Update settings."""
        self.settings = settings


# Global retriever instance
_retriever_instance: Optional[BM25SRetriever] = None


def get_retriever() -> BM25SRetriever:
    """Get the global retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = BM25SRetriever()
    return _retriever_instance


def retrieve_documents(query: str, documents: List[Document] = None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to retrieve documents based on query.
    
    Args:
        query: Search query
        documents: Optional document list (if provided, creates new retriever)
        **kwargs: Optional settings overrides
        
    Returns:
        Dictionary with retrieval results
    """
    if documents:
        retriever = BM25SRetriever()
        retriever.rebuild_index(documents)
        return retriever.retrieve_documents(query, **kwargs)
    else:
        retriever = get_retriever()
        return retriever.retrieve_documents(query, **kwargs)
