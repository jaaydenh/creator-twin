from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import TokenTextSplitter
from typing import List

def video_to_chunks(id: str = "iv-5mZ_9CPY") -> List[str]:
  ytt_api = YouTubeTranscriptApi()
  trans=ytt_api.fetch(id)
  s = ""
  for i in trans:
    s+= i.text
  text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=60)

  texts = text_splitter.split_text(s)
  return texts




import sqlite3
from typing import List

def store_video_chunks_in_db(video_id: str = "iv-5mZ_9CPY", db_name: str = 'video_chunks.db', table_name: str = 'chunks'):
    """
    Fetches video transcript chunks and stores them in an SQLite database.
    Checks if chunks for the video ID already exist before inserting.

    Args:
        video_id (str): The ID of the YouTube video.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.
    """
    conn = None # Initialize conn to None
    try:
        # Connect to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        # Create table if it doesn't exist
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                video_id TEXT,
                chunk_text TEXT
            )
        ''')
        print(f"Table '{table_name}' created or already exists.")

        # Check if chunks for the video ID already exist
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE video_id = ?", (video_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"Chunks for video ID: {video_id} already exist. Skipping insertion.")
        else:
            # Fetch video chunks
            chunks_data = video_to_chunks(video_id)
            print(f"Number of chunks retrieved: {len(chunks_data)}")

            # Insert data
            for chunk in chunks_data:
                cursor.execute(f'''
                    INSERT INTO {table_name} (video_id, chunk_text)
                    VALUES (?, ?)
                ''', (video_id, chunk))
            conn.commit()
            print(f"Inserted {len(chunks_data)} chunks for video ID: {video_id}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close connection
        if conn: # Check if conn is not None before closing
            conn.close()
            print("Database connection closed.")




import sqlite3
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from google.colab import userdata
from pinecone import Pinecone
import os

class Settings(BaseSettings):
    pinecone_namespace: str = "default"
    pinecone_top_k: int = 10
    pinecone_api_key: str

try:
    settings = Settings(pinecone_api_key=userdata.get('PINECONE_API_KEY'))
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Please ensure 'PINECONE_API_KEY' is set in Colab secrets.")
    settings = None

def upsert_video_chunks_to_pinecone(video_id: str):
    """
    Retrieves text chunks for a given video ID from the SQLite database
    and upserts them into both dense and sparse Pinecone indexes.

    Args:
        video_id (str): The YouTube video ID.
    """
    if not settings:
        print("Settings not loaded. Cannot proceed with Pinecone upsert.")
        return

    conn = None
    chunks_data = []
    try:
        # Connect to the database
        conn = sqlite3.connect('video_chunks.db')
        cursor = conn.cursor()
        print(f"Connected to database: video_chunks.db")

        # Execute a SQL query to select the chunk_text
        cursor.execute("SELECT chunk_text FROM chunks WHERE video_id = ?", (video_id,))

        # Fetch all the results
        rows = cursor.fetchall()

        # Extract the text chunks
        chunks_data = [row[0] for row in rows]
        print(f"Retrieved {len(chunks_data)} chunks for video ID: {video_id}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during database operations: {e}")
    finally:
        # Close connection
        if conn:
            conn.close()
            print("Database connection closed.")

    if not chunks_data:
        print("No chunks found for the given video ID. Aborting Pinecone upsert.")
        return

    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)

        # Prepare and upsert to dense index
        try:
            records_to_upsert_dense = []
            for i, text in enumerate(chunks_data):
                record_id = f"{video_id}-{i}"
                records_to_upsert_dense.append({
                    "_id": record_id,
                    "text": text,
                })
            print(f"Prepared {len(records_to_upsert_dense)} records for dense index upsert.")

            index = pc.Index(name='character')
            index.upsert_records(records=records_to_upsert_dense, namespace=settings.pinecone_namespace)
            print(f"Successfully attempted to upsert {len(records_to_upsert_dense)} records to the dense Pinecone index.")
        except Exception as e:
            print(f"An error occurred during dense index upsert: {e}")

        # Prepare and upsert to sparse index
        try:
            records_to_upsert_sparse = []
            for i, text in enumerate(chunks_data):
                record_id = f"{video_id}-{i}"
                records_to_upsert_sparse.append({
                    "_id": record_id,
                    "text": text,
                })
            print(f"Prepared {len(records_to_upsert_sparse)} records for sparse index upsert.")

            sparse_index = pc.Index(name='character-sparse')
            sparse_index.upsert_records(records=records_to_upsert_sparse, namespace=settings.pinecone_namespace)
            print(f"Successfully attempted to upsert {len(records_to_upsert_sparse)} records to the sparse Pinecone index.")
        except Exception as e:
            print(f"An error occurred during sparse index upsert: {e}")

    except Exception as e:
        print(f"An error occurred during Pinecone operations: {e}")




if name == "main":
    store_video_chunks_in_db(video_id = "KZeIEiBrT_w")
    upsert_video_chunks_to_pinecone(video_id = "KZeIEiBrT_w")
