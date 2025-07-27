#!/usr/bin/env python3
"""
Script to populate personality data for existing video chunks.
This is an example of how you might add personality information to your knowledge base.
"""

import sqlite3
import asyncio
from enhanced_rag_service import PersonalityUpdater, RAGService
from typing import Dict, List

def get_all_chunks(db_name: str = 'video_chunks.db') -> List[Dict[str, str]]:
    """
    Retrieve all chunks from the database
    """
    conn = None
    chunks = []
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chunk_id, video_id, chunk_text
            FROM chunks
            WHERE chunk_id IS NOT NULL
        ''')
        
        rows = cursor.fetchall()
        
        for row in rows:
            chunks.append({
                'chunk_id': row[0],
                'video_id': row[1],
                'chunk_text': row[2]
            })
            
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
    finally:
        if conn:
            conn.close()
    
    return chunks

def analyze_content_for_personality(content: str) -> Dict[str, str]:
    """
    Analyze content to extract personality traits and speaking style.
    In a real implementation, you might use an LLM for this analysis.
    """
    content_lower = content.lower()
    
    # Example personality detection based on content analysis
    traits = []
    styles = []
    topics = []
    
    # Detect enthusiasm and teaching style
    if any(word in content_lower for word in ['exciting', 'amazing', 'incredible', 'fantastic']):
        traits.append('enthusiastic')
    
    if any(word in content_lower for word in ['let me explain', 'you see', 'basically', 'simply put']):
        styles.append('explanatory')
        traits.append('educational')
    
    if any(word in content_lower for word in ['like when', 'imagine', 'think of it as', 'similar to']):
        styles.append('uses analogies')
    
    # Detect technical focus
    if any(word in content_lower for word in ['code', 'programming', 'development', 'software', 'algorithm']):
        topics.append('technology')
        traits.append('technical')
    
    # Detect casual speaking style
    if any(word in content_lower for word in ['you know', 'right?', 'okay so', 'alright']):
        styles.append('casual conversational')
    
    # Detect motivational content
    if any(word in content_lower for word in ['you can do', 'believe', 'achieve', 'success', 'grow']):
        traits.append('motivational')
        styles.append('encouraging')
    
    # Detect storytelling
    if any(word in content_lower for word in ['story', 'experience', 'happened', 'remember when']):
        styles.append('storytelling')
    
    return {
        'personality_traits': ', '.join(traits) if traits else None,
        'speaking_style': ', '.join(styles) if styles else None,
        'topics': ', '.join(topics) if topics else None
    }

async def populate_personality_data():
    """
    Main function to populate personality data for all chunks
    """
    print("Starting personality data population...")
    
    # Initialize RAG service to ensure database is set up
    rag_service = RAGService()
    rag_service.setup_enhanced_database()
    
    # Get all chunks
    chunks = get_all_chunks()
    print(f"Found {len(chunks)} chunks to analyze")
    
    updated_count = 0
    
    for chunk in chunks:
        try:
            # Analyze content for personality traits
            personality_data = analyze_content_for_personality(chunk['chunk_text'])
            
            # Update only if we found some personality information
            if any(personality_data.values()):
                PersonalityUpdater.update_chunk_personality(
                    chunk_id=chunk['chunk_id'],
                    personality_traits=personality_data['personality_traits'],
                    speaking_style=personality_data['speaking_style'],
                    topics=personality_data['topics']
                )
                updated_count += 1
                print(f"Updated chunk {chunk['chunk_id']}: {personality_data}")
        
        except Exception as e:
            print(f"Error updating chunk {chunk['chunk_id']}: {e}")
    
    print(f"\nCompleted! Updated {updated_count} out of {len(chunks)} chunks")

# Example manual personality assignments for specific video content
def add_manual_personality_examples():
    """
    Add some manual personality examples for demonstration
    """
    print("Adding manual personality examples...")
    
    # Example personality data - you would customize this based on your actual content
    manual_examples = [
        {
            'chunk_id': 'KZeIEiBrT_w-0',
            'personality_traits': 'enthusiastic, educational, tech-focused, approachable',
            'speaking_style': 'casual explanatory, uses examples, encouraging',
            'topics': 'technology, learning, programming'
        },
        {
            'chunk_id': 'KZeIEiBrT_w-1', 
            'personality_traits': 'analytical, detail-oriented, helpful',
            'speaking_style': 'methodical, step-by-step, clear',
            'topics': 'problem-solving, tutorials'
        }
    ]
    
    for example in manual_examples:
        try:
            PersonalityUpdater.update_chunk_personality(
                chunk_id=example['chunk_id'],
                personality_traits=example['personality_traits'],
                speaking_style=example['speaking_style'],
                topics=example['topics']
            )
            print(f"Added manual example for {example['chunk_id']}")
        except Exception as e:
            print(f"Error adding manual example: {e}")

async def test_rag_system():
    """
    Test the RAG system with some example queries
    """
    print("\n" + "="*50)
    print("Testing RAG System")
    print("="*50)
    
    rag_service = RAGService()
    
    test_queries = [
        "How do you approach learning new technologies?",
        "What's your teaching style?",
        "Tell me about programming",
        "How do you explain complex concepts?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        try:
            context = await rag_service.get_relevant_context(query, top_k=3)
            
            print(f"Found {context['total_matches']} relevant chunks")
            
            if context['personality_summary']:
                print(f"Personality Summary:\n{context['personality_summary']}")
            
            print("\nTop relevant chunks:")
            for i, chunk in enumerate(context['context_chunks'][:2], 1):
                print(f"{i}. Score: {chunk.relevance_score:.3f}")
                print(f"   Content: {chunk.chunk_text[:150]}...")
                if chunk.personality_traits:
                    print(f"   Traits: {chunk.personality_traits}")
                if chunk.speaking_style:
                    print(f"   Style: {chunk.speaking_style}")
                print()
        
        except Exception as e:
            print(f"Error testing query: {e}")

if __name__ == "__main__":
    print("Creator Twin - Personality Data Population")
    print("==========================================")
    
    # Step 1: Populate personality data automatically
    asyncio.run(populate_personality_data())
    
    # Step 2: Add some manual examples
    add_manual_personality_examples()
    
    # Step 3: Test the system
    asyncio.run(test_rag_system()) 