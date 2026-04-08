"""
FastAPI routes for BM25S retriever service.
"""

import time
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..core.retriever import BM25SRetriever, Document, get_retriever
from ..core.config import Config, load_config
from .models import (
    Document as DocumentModel,
    RetrieveRequest,
    RetrieveResponse,
    IndexRequest,
    IndexResponse,
    SettingsResponse,
    ErrorResponse,
    RetrievedDocument,
    BM25SSettings as BM25SSettingsModel
)


def create_app(config: Config = None) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="BM25S Retriever",
        description="A BM25S-based document retrieval service",
        version="1.0.0"
    )
    
    config = config or load_config()
    
    # Setup static files and templates
    app.mount("/static", StaticFiles(directory="bm25s_retriever/ui/static"), name="static")
    templates = Jinja2Templates(directory="bm25s_retriever/ui/templates")
    
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """Serve the main UI."""
        return templates.TemplateResponse("tool-router.html", {"request": request})
    
    @app.post("/retrieve", response_model=RetrieveResponse)
    async def retrieve_documents(request: RetrieveRequest):
        """Retrieve documents based on query."""
        try:
            retriever = get_retriever()
            
            # Override settings if provided
            kwargs = {}
            if request.temperature is not None:
                kwargs["temperature"] = request.temperature
            if request.ignore_zero is not None:
                kwargs["ignore_zero"] = request.ignore_zero
            if request.llm_tools_cutoff is not None:
                kwargs["llm_tools_cutoff"] = request.llm_tools_cutoff
            
            result = retriever.retrieve_documents(request.query, **kwargs)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["message"])
            
            # Convert to response model
            documents = []
            for doc in result["documents"]:
                documents.append(RetrievedDocument(
                    id=doc["id"],
                    title=doc["title"],
                    content=doc["content"],
                    keywords=doc["keywords"],
                    metadata=doc["metadata"],
                    bm25_score=doc["bm25_score"],
                    softmax_score=doc["softmax_score"]
                ))
            
            return RetrieveResponse(
                success=result["success"],
                message=result["message"],
                documents=documents,
                total_retrieved=result["total_retrieved"],
                cutoff_percentage=result["cutoff_percentage"],
                settings=result["settings"]
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/index", response_model=IndexResponse)
    async def build_index(request: IndexRequest):
        """Build or rebuild BM25S index."""
        try:
            start_time = time.time()
            
            # Convert to Document objects
            documents = []
            for doc in request.documents:
                documents.append(Document(
                    id=doc.id,
                    title=doc.title,
                    content=doc.content,
                    keywords=doc.keywords,
                    metadata=doc.metadata
                ))
            
            # Build index
            retriever = get_retriever()
            if request.rebuild:
                retriever.rebuild_index(documents)
            else:
                retriever.add_documents(documents)
            
            index_time = (time.time() - start_time) * 1000
            
            return IndexResponse(
                success=True,
                message=f"Index built successfully with {len(documents)} documents",
                document_count=len(documents),
                index_time_ms=index_time
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/settings", response_model=SettingsResponse)
    async def get_settings():
        """Get current settings."""
        try:
            retriever = get_retriever()
            settings = retriever.get_settings()
            
            return SettingsResponse(
                bm25s=BM25SSettingsModel(
                    temperature=settings.temperature,
                    ignore_zero=settings.ignore_zero,
                    llm_tools_cutoff=settings.llm_tools_cutoff
                ),
                documents={
                    "source": config.documents.source,
                    "auto_reload": config.documents.auto_reload,
                    "encoding": config.documents.encoding
                },
                server={
                    "host": config.server.host,
                    "port": config.server.port,
                    "reload": config.server.reload,
                    "log_level": config.server.log_level
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/settings", response_model=SettingsResponse)
    async def update_settings(settings: BM25SSettingsModel):
        """Update BM25S settings."""
        try:
            from ..core.config import BM25SSettings
            
            retriever = get_retriever()
            new_settings = BM25SSettings(
                temperature=settings.temperature,
                ignore_zero=settings.ignore_zero,
                llm_tools_cutoff=settings.llm_tools_cutoff
            )
            retriever.update_settings(new_settings)
            
            # Return updated settings
            updated = retriever.get_settings()
            
            return SettingsResponse(
                bm25s=BM25SSettingsModel(
                    temperature=updated.temperature,
                    ignore_zero=updated.ignore_zero,
                    llm_tools_cutoff=updated.llm_tools_cutoff
                ),
                documents={
                    "source": config.documents.source,
                    "auto_reload": config.documents.auto_reload,
                    "encoding": config.documents.encoding
                },
                server={
                    "host": config.server.host,
                    "port": config.server.port,
                    "reload": config.server.reload,
                    "log_level": config.server.log_level
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/status")
    async def get_status():
        """Get service status."""
        try:
            retriever = get_retriever()
            doc_count = retriever.get_document_count()
            
            return {
                "status": "healthy",
                "document_count": doc_count,
                "retriever_initialized": retriever.retriever is not None,
                "version": "1.0.0"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/reload")
    async def reload_index():
        """Reload the retriever instance."""
        try:
            from ..core.retriever import _retriever_instance
            
            # Clear global instance
            import importlib
            import bm25s_retriever.core.retriever
            importlib.reload(bm25s_retriever.core.retriever)
            
            return {
                "success": True,
                "message": "Retriever reloaded successfully"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        return ErrorResponse(
            error=type(exc).__name__,
            message=str(exc),
            details={"path": str(request.url)}
        )
    
    return app
