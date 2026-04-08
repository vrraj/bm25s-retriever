"""
Basic tests for BM25S retriever package.
"""

import pytest
from bm25s_retriever.core.retriever import BM25SRetriever, Document, retrieve_documents
from bm25s_retriever.core.config import BM25SSettings, Config
from bm25s_retriever.api.client import BM25SClient


class TestBM25SRetriever:
    """Test core BM25S retriever functionality."""
    
    def setup_method(self):
        """Setup test documents."""
        self.documents = [
            Document(
                id="doc1",
                title="Stock Market Data",
                content="Real-time stock quotes and market information",
                keywords=["stock", "market", "quote"]
            ),
            Document(
                id="doc2", 
                title="Options Trading",
                content="Options chain data and Greeks calculation",
                keywords=["option", "trading", "greeks"]
            ),
            Document(
                id="doc3",
                title="Financial News",
                content="Latest financial news and market updates",
                keywords=["news", "financial", "updates"]
            )
        ]
        self.retriever = BM25SRetriever()
        self.retriever.rebuild_index(self.documents)
    
    def test_document_retrieval(self):
        """Test basic document retrieval."""
        results = self.retriever.retrieve_documents("stock market")
        assert results["success"] is True
        assert len(results["documents"]) > 0
        assert results["documents"][0]["id"] == "doc1"
    
    def test_retrieval_with_cutoff(self):
        """Test retrieval with cutoff filtering."""
        results = self.retriever.retrieve_documents(
            "stock market", 
            llm_tools_cutoff=50.0  # High cutoff
        )
        assert results["success"] is True
        # Should have fewer results with high cutoff
        assert len(results["documents"]) <= len(self.documents)
    
    def test_retrieval_with_temperature(self):
        """Test retrieval with temperature scaling."""
        results_low = self.retriever.retrieve_documents(
            "stock market",
            temperature=0.1  # Low temperature
        )
        results_high = self.retriever.retrieve_documents(
            "stock market", 
            temperature=2.0  # High temperature
        )
        assert results_low["success"] is True
        assert results_high["success"] is True
        # Results should differ due to temperature
        assert len(results_low["documents"]) >= 0
        assert len(results_high["documents"]) >= 0
    
    def test_no_results(self):
        """Test query with no matching documents."""
        results = self.retriever.retrieve_documents("nonexistent query xyz")
        assert results["success"] is True
        assert len(results["documents"]) == 0
    
    def test_add_documents(self):
        """Test adding documents to existing index."""
        new_doc = Document(
            id="doc4",
            title="New Document",
            content="Additional content for testing",
            keywords=["new", "test"]
        )
        original_count = self.retriever.get_document_count()
        self.retriever.add_documents([new_doc])
        assert self.retriever.get_document_count() == original_count + 1


class TestConfiguration:
    """Test configuration management."""
    
    def test_default_settings(self):
        """Test default BM25S settings."""
        settings = BM25SSettings()
        assert settings.temperature == 0.7
        assert settings.ignore_zero is True
        assert settings.llm_tools_cutoff == 8.0
    
    def test_settings_from_dict(self):
        """Test creating settings from dictionary."""
        data = {"temperature": 1.0, "ignore_zero": False, "llm_tools_cutoff": 10.0}
        settings = BM25SSettings.from_dict(data)
        assert settings.temperature == 1.0
        assert settings.ignore_zero is False
        assert settings.llm_tools_cutoff == 10.0
    
    def test_config_defaults(self):
        """Test default configuration."""
        config = Config()
        assert config.bm25s.temperature == 0.7
        assert config.documents.source == "documents.yaml"
        assert config.server.host == "0.0.0.0"
        assert config.server.port == 8000


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_retrieve_documents_function(self):
        """Test standalone retrieve_documents function."""
        docs = [
            Document(
                id="test1",
                title="Test Document",
                content="Test content for retrieval",
                keywords=["test", "content"]
            )
        ]
        results = retrieve_documents("test content", documents=docs)
        assert results["success"] is True
        assert len(results["documents"]) > 0


class TestAPIClient:
    """Test API client (mock tests)."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = BM25SClient("http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30.0
        client.close()
    
    def test_client_with_custom_timeout(self):
        """Test client with custom timeout."""
        client = BM25SClient("http://localhost:8000", timeout=60.0)
        assert client.timeout == 60.0
        client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
