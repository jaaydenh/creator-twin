from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import sys
import os
from contextlib import asynccontextmanager

# Add the services directory to the path so we can import our RAG service
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from enhanced_rag_service import RAGService, PersonalityChunk

# Initialize RAG service
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rag_service
    try:
        rag_service = RAGService()
        # Setup enhanced database on startup
        rag_service.setup_enhanced_database()
        print("RAG service initialized successfully")
    except Exception as e:
        print(f"Failed to initialize RAG service: {e}")
    
    yield
    
    # Shutdown
    # Add any cleanup code here if needed
    pass

app = FastAPI(title="Creator Twin RAG API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware to allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SearchResponse(BaseModel):
    context_chunks: List[Dict[str, Any]]
    personality_summary: str
    total_matches: int

@app.post("/rag/search", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest):
    """
    Search the knowledge base using RAG to find relevant personality information
    """
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        context = await rag_service.get_relevant_context(request.query, request.top_k)
        
        # Convert PersonalityChunk objects to dicts for JSON serialization
        context_chunks = []
        for chunk in context["context_chunks"]:
            chunk_dict = {
                "chunk_id": chunk.chunk_id,
                "video_id": chunk.video_id,
                "chunk_text": chunk.chunk_text,
                "personality_traits": chunk.personality_traits,
                "speaking_style": chunk.speaking_style,
                "topics": chunk.topics,
                "timestamp": chunk.timestamp,
                "relevance_score": chunk.relevance_score
            }
            context_chunks.append(chunk_dict)
        
        return SearchResponse(
            context_chunks=context_chunks,
            personality_summary=context["personality_summary"],
            total_matches=context["total_matches"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/personality/update")
async def update_personality_data(
    chunk_id: str,
    personality_traits: Optional[str] = None,
    speaking_style: Optional[str] = None,
    topics: Optional[str] = None
):
    """
    Update personality information for a specific chunk
    """
    try:
        from enhanced_rag_service import PersonalityUpdater
        
        PersonalityUpdater.update_chunk_personality(
            chunk_id=chunk_id,
            personality_traits=personality_traits,
            speaking_style=speaking_style,
            topics=topics
        )
        
        return {"message": f"Successfully updated personality data for chunk {chunk_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "rag_service_initialized": rag_service is not None
    }

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Creator Twin RAG API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/rag/search",
            "update_personality": "/personality/update",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 