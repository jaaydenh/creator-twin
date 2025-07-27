import sqlite3
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pinecone import Pinecone
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

class Settings(BaseSettings):
    pinecone_namespace: str = "default"
    pinecone_top_k: int = 5
    pinecone_api_key: str
    openai_api_key: str
    
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

class PersonalityChunk(BaseModel):
    chunk_id: str
    video_id: str
    chunk_text: str
    personality_traits: Optional[str] = None
    speaking_style: Optional[str] = None
    topics: Optional[str] = None
    timestamp: Optional[float] = None
    relevance_score: Optional[float] = None

class RAGService:
    def __init__(self):
        self.settings = Settings()
        self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
        self.openai_client = OpenAI(api_key=self.settings.openai_api_key)
        self.dense_index = self.pc.Index(name='character')
        self.sparse_index = self.pc.Index(name='character-sparse')
        
    def setup_enhanced_database(self, db_name: str = 'video_chunks.db'):
        """
        Enhance the existing database schema to include personality information
        """
        conn = None
        try:
            # Ensure we're using the correct path to the database file
            db_path = os.path.join(os.path.dirname(__file__), db_name)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add new columns to existing table (if they don't exist)
            try:
                cursor.execute('ALTER TABLE chunks ADD COLUMN personality_traits TEXT')
                cursor.execute('ALTER TABLE chunks ADD COLUMN speaking_style TEXT')
                cursor.execute('ALTER TABLE chunks ADD COLUMN topics TEXT')
                cursor.execute('ALTER TABLE chunks ADD COLUMN timestamp REAL')
                cursor.execute('ALTER TABLE chunks ADD COLUMN chunk_id TEXT')
                print("Enhanced database schema with personality columns")
            except sqlite3.OperationalError:
                print("Columns may already exist, continuing...")
            
            # Create index on chunk_id for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chunk_id ON chunks(chunk_id)
            ''')
            
            # Update existing rows with chunk_ids if they don't have them
            cursor.execute('''
                UPDATE chunks 
                SET chunk_id = video_id || '-' || rowid 
                WHERE chunk_id IS NULL
            ''')
            
            conn.commit()
            print("Database setup completed successfully")
            
        except Exception as e:
            print(f"Error setting up database: {e}")
        finally:
            if conn:
                conn.close()
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using OpenAI's embedding model
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=1024  # Match your Pinecone index dimension
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    async def semantic_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search using Pinecone dense index
        """
        if top_k is None:
            top_k = self.settings.pinecone_top_k
            
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search in dense index
            results = self.dense_index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=self.settings.pinecone_namespace,
                include_metadata=True
            )
            
            return results.matches
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    async def hybrid_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining dense and sparse results
        """
        if top_k is None:
            top_k = self.settings.pinecone_top_k
            
        try:
            # Get dense results
            dense_results = await self.semantic_search(query, top_k)
            
            # For now, we'll use dense results. In a full hybrid approach,
            # you'd also query the sparse index and combine results
            return dense_results
        except Exception as e:
            print(f"Error in hybrid search: {e}")
            return []
    
    def retrieve_personality_context(self, chunk_ids: List[str], db_name: str = 'video_chunks.db') -> List[PersonalityChunk]:
        """
        Retrieve detailed context from SQLite based on Pinecone results
        """
        if not chunk_ids:
            return []
            
        conn = None
        results = []
        
        try:
            # Ensure we're using the correct path to the database file
            db_path = os.path.join(os.path.dirname(__file__), db_name)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create placeholders for IN clause
            placeholders = ','.join(['?' for _ in chunk_ids])
            
            query = f'''
                SELECT chunk_id, video_id, chunk_text, personality_traits, 
                       speaking_style, topics, timestamp
                FROM chunks 
                WHERE chunk_id IN ({placeholders})
            '''
            
            cursor.execute(query, chunk_ids)
            rows = cursor.fetchall()
            
            for row in rows:
                chunk = PersonalityChunk(
                    chunk_id=row[0] or "",
                    video_id=row[1] or "",
                    chunk_text=row[2] or "",
                    personality_traits=row[3],
                    speaking_style=row[4],
                    topics=row[5],
                    timestamp=row[6]
                )
                results.append(chunk)
                
        except Exception as e:
            print(f"Error retrieving personality context: {e}")
        finally:
            if conn:
                conn.close()
                
        return results
    
    async def get_relevant_context(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """
        Main RAG pipeline: search Pinecone and retrieve personality context
        """
        try:
            # Step 1: Semantic search in Pinecone
            pinecone_results = await self.hybrid_search(query, top_k)
            
            if not pinecone_results:
                return {"context_chunks": [], "personality_summary": ""}
            
            # Step 2: Extract chunk IDs and scores
            chunk_ids = []
            chunk_scores = {}
            
            for match in pinecone_results:
                chunk_id = match.id
                chunk_ids.append(chunk_id)
                chunk_scores[chunk_id] = match.score
            
            # Step 3: Retrieve detailed context from SQLite
            personality_chunks = self.retrieve_personality_context(chunk_ids)
            
            # Step 4: Add relevance scores and sort
            for chunk in personality_chunks:
                chunk.relevance_score = chunk_scores.get(chunk.chunk_id, 0.0)
            
            personality_chunks.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            
            # Step 5: Generate personality summary
            personality_summary = self._generate_personality_summary(personality_chunks)
            
            return {
                "context_chunks": personality_chunks,
                "personality_summary": personality_summary,
                "total_matches": len(personality_chunks)
            }
            
        except Exception as e:
            print(f"Error in RAG pipeline: {e}")
            return {"context_chunks": [], "personality_summary": ""}
    
    def _generate_personality_summary(self, chunks: List[PersonalityChunk]) -> str:
        """
        Generate a personality summary from retrieved chunks
        """
        if not chunks:
            return ""
        
        # Combine personality traits
        traits = []
        styles = []
        relevant_content = []
        
        for chunk in chunks:
            if chunk.personality_traits:
                traits.append(chunk.personality_traits)
            if chunk.speaking_style:
                styles.append(chunk.speaking_style)
            if chunk.chunk_text and chunk.relevance_score and chunk.relevance_score > 0.7:
                relevant_content.append(chunk.chunk_text[:200] + "...")
        
        summary_parts = []
        
        if traits:
            unique_traits = list(set(traits))
            summary_parts.append(f"Personality traits: {', '.join(unique_traits)}")
        
        if styles:
            unique_styles = list(set(styles))
            summary_parts.append(f"Speaking style: {', '.join(unique_styles)}")
        
        if relevant_content:
            summary_parts.append(f"Relevant content examples: {' | '.join(relevant_content[:2])}")
        
        return "\n".join(summary_parts)

# Utility functions for updating personality data
class PersonalityUpdater:
    @staticmethod
    def update_chunk_personality(chunk_id: str, personality_traits: str = None, 
                               speaking_style: str = None, topics: str = None,
                               db_name: str = 'video_chunks.db'):
        """
        Update personality information for a specific chunk
        """
        conn = None
        try:
            # Ensure we're using the correct path to the database file
            db_path = os.path.join(os.path.dirname(__file__), db_name)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            update_fields = []
            values = []
            
            if personality_traits:
                update_fields.append("personality_traits = ?")
                values.append(personality_traits)
            
            if speaking_style:
                update_fields.append("speaking_style = ?")
                values.append(speaking_style)
                
            if topics:
                update_fields.append("topics = ?")
                values.append(topics)
            
            if update_fields:
                values.append(chunk_id)
                query = f"UPDATE chunks SET {', '.join(update_fields)} WHERE chunk_id = ?"
                cursor.execute(query, values)
                conn.commit()
                print(f"Updated personality data for chunk {chunk_id}")
            
        except Exception as e:
            print(f"Error updating personality data: {e}")
        finally:
            if conn:
                conn.close()

# Example usage and testing
async def main():
    rag = RAGService()
    
    # Setup enhanced database
    rag.setup_enhanced_database()
    
    # Example: Update some personality data
    updater = PersonalityUpdater()
    # This would be called for each chunk with appropriate personality data
    # updater.update_chunk_personality(
    #     "KZeIEiBrT_w-0", 
    #     personality_traits="enthusiastic, educational, tech-focused",
    #     speaking_style="casual, explanatory, uses analogies"
    # )
    
    # Example query
    context = await rag.get_relevant_context("How do you approach learning new technologies?")
    print("Retrieved context:", context)

if __name__ == "__main__":
    asyncio.run(main()) 