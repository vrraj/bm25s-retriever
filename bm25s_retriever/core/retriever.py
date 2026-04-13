"""
BM25S document retriever implementation.
"""

import bm25s
import Stemmer
import math
import yaml
import os
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
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.metadata is None:
            self.metadata = {}
    
    def copy(self) -> Dict[str, Any]:
        """Return a copy of document data as dict."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "keywords": self.keywords,
            "metadata": self.metadata
        }


class BM25SRetriever:
    """BM25S-based document retrieval system with softmax scoring and cutoff filtering."""
    
    def __init__(self, settings: BM25SSettings = None, document_file: str = "documents.yaml"):
        self.settings = settings or BM25SSettings()
        self.stemmer = Stemmer.Stemmer("english")
        self.documents: List[Document] = []
        self.retriever = None
        self.document_file = document_file
        self._load_and_index_documents()
    
    def _load_documents_from_yaml(self, file_path: str) -> List[Document]:
        """Load documents from YAML file."""
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            documents = []
            for doc_data in data.get('documents', []):
                doc = Document(
                    id=doc_data['id'],
                    title=doc_data['title'],
                    content=doc_data['content'],
                    keywords=doc_data.get('keywords', []),
                    metadata=doc_data.get('metadata', {})
                )
                documents.append(doc)
            
            return documents
        except Exception as e:
            print(f"Error loading documents from {file_path}: {e}")
            return []
    
    def _load_and_index_documents(self, documents: List[Document] = None):
        """Load documents and build BM25S index."""
        if documents:
            self.documents = documents
        else:
            # Load from YAML file
            self.documents = self._load_documents_from_yaml(self.document_file)
        
        # If no documents, don't build index yet
        if not self.documents:
            self.retriever = None
            return
        
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
        try:
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
            
            print(f"Debug: Starting retrieval with query: '{query}'")
            
            # Tokenize query
            query_tokens = bm25s.tokenize([query], stopwords="en", stemmer=self.stemmer)[0]
            print(f"Debug: Query tokens: {query_tokens}")
            
            # Retrieve scores
            scores, indices = self.retriever.retrieve(query_tokens, k=len(self.documents))
            print(f"Debug: Retrieved scores type: {type(scores)}, indices type: {type(indices)}")
            print(f"Debug: Scores shape: {getattr(scores, 'shape', 'N/A')}")
            print(f"Debug: Indices shape: {getattr(indices, 'shape', 'N/A')}")
            
            # Handle nested arrays from BM25S
            if hasattr(scores, 'shape') and len(scores.shape) > 1:
                scores = scores[0]  # Take first row if 2D
            if hasattr(indices, 'shape') and len(indices.shape) > 1:
                indices = indices[0]  # Take first row if 2D
            
            # Convert indices to integers (BM25S returns floats)
            indices = indices.astype(int)
                
            print(f"Debug: After unpacking - scores: {scores}, indices: {indices}")
            print(f"Debug: Scores type: {type(scores)}, indices type: {type(indices)}")
            
            # Prepare results
            results = []
            all_scores = []
            retrieved_docs = []
            
            print(f"Debug: Processing {len(scores)} results...")
            for i, (score, idx) in enumerate(zip(scores, indices)):
                print(f"Debug: Processing result {i}: score={score} (type: {type(score)}), idx={idx}")
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    score_float = float(score) if hasattr(score, 'item') else float(score)
                    print(f"Debug: Converted score to float: {score_float}")
                    doc["bm25_score"] = score_float
                    retrieved_docs.append(doc)
                    all_scores.append(score_float)
                else:
                    print(f"Debug: Index {idx} out of range (documents: {len(self.documents)})")
            
            print(f"Debug: Processed {len(all_scores)} scores")
            
            # Apply ignore_zero filter
            if ignore_zero:
                print(f"Debug: Applying ignore_zero filter...")
                filtered_docs = []
                filtered_scores = []
                for doc, score in zip(retrieved_docs, all_scores):
                    print(f"Debug: Checking score: {score} (type: {type(score)})")
                    score_float = float(score) if hasattr(score, 'item') else float(score)
                    if score_float > 0:
                        filtered_docs.append(doc)
                        filtered_scores.append(score_float)
                retrieved_docs = filtered_docs
                all_scores = filtered_scores
                print(f"Debug: After filtering: {len(all_scores)} documents")
            
            # Calculate softmax scores
            print(f"Debug: Calculating softmax with temperature: {temperature}")
            softmax_scores = self._calculate_softmax(all_scores, temperature)
            print(f"Debug: Softmax scores: {softmax_scores}")
            
            # Apply cutoff filtering
            cutoff_percentage = llm_tools_cutoff / 100.0
            print(f"Debug: Applying cutoff: {cutoff_percentage}")
            filtered_results = []
            
            for doc, score, softmax_score in zip(retrieved_docs, all_scores, softmax_scores):
                print(f"Debug: Checking softmax_score: {softmax_score} >= {cutoff_percentage}")
                doc["softmax_score"] = softmax_score
                if softmax_score >= cutoff_percentage:
                    filtered_results.append(doc)
            
            print(f"Debug: Final results: {len(filtered_results)} documents")
            
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
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during retrieval: {str(e)}",
                "documents": [],
                "total_retrieved": 0,
                "cutoff_percentage": 0.0,
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
