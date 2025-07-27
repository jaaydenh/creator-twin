# Creator Twin RAG System Setup

## Overview
This RAG (Retrieval-Augmented Generation) system combines Pinecone vector search with SQLite personality data to create personalized LLM responses that maintain consistent character traits and speaking styles.

## Architecture
- **Pinecone**: Stores embeddings for semantic search
- **SQLite**: Stores content chunks with personality metadata
- **FastAPI**: Provides RAG search endpoints
- **Next.js**: Frontend with integrated knowledge base search

## Prerequisites

1. **Environment Variables**
   Create a `.env` file in the `fast-api` directory:
   ```bash
   PINECONE_API_KEY=your_pinecone_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

2. **Pinecone Setup**
   - Create two indexes in Pinecone:
     - `character` (dense embeddings)
     - `character-sparse` (sparse embeddings)
   - Use dimension 1536 for OpenAI embeddings

## Installation & Setup

### 1. Install Python Dependencies
```bash
cd fast-api
pip install -r requirements.txt
```

### 2. Set Up Enhanced Database
```bash
cd services
python enhanced_rag_service.py
```

### 3. Populate Personality Data
```bash
python populate_personality_data.py
```

### 4. Start FastAPI Server
```bash
# From fast-api directory
python main.py
# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Next.js Frontend
```bash
cd ../site
npm install  # or pnpm install
npm run dev  # or pnpm dev
```

## Usage

### Adding New Content

1. **Add video chunks to database:**
   ```python
   from pinecone_upsert_service import store_video_chunks_in_db, upsert_video_chunks_to_pinecone
   
   # Store chunks in SQLite
   store_video_chunks_in_db(video_id="YOUR_VIDEO_ID")
   
   # Upload embeddings to Pinecone
   upsert_video_chunks_to_pinecone(video_id="YOUR_VIDEO_ID")
   ```

2. **Add personality information:**
   ```python
   from enhanced_rag_service import PersonalityUpdater
   
   PersonalityUpdater.update_chunk_personality(
       chunk_id="YOUR_VIDEO_ID-0",
       personality_traits="enthusiastic, educational, tech-focused",
       speaking_style="casual explanatory, uses examples",
       topics="technology, programming, tutorials"
   )
   ```

### Testing the System

1. **Test RAG endpoints:**
   ```bash
   curl -X POST "http://localhost:8000/rag/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "How do you approach learning?", "top_k": 5}'
   ```

2. **Test in chat interface:**
   - Visit http://localhost:3000
   - Ask questions like "What's your teaching style?"
   - The LLM will automatically search the knowledge base

## API Endpoints

- `POST /rag/search` - Search knowledge base
- `POST /personality/update` - Update personality data
- `GET /health` - Health check

## Personality Data Schema

The enhanced SQLite schema includes:
- `chunk_id`: Unique identifier for each chunk
- `video_id`: Source video identifier
- `chunk_text`: Original content
- `personality_traits`: Comma-separated traits (e.g., "enthusiastic, educational")
- `speaking_style`: Communication style (e.g., "casual explanatory, uses analogies")
- `topics`: Content topics (e.g., "technology, programming")
- `timestamp`: Optional timestamp within video
