from config.pinecone_config import settings
import sqlite3
from pinecone import Pinecone
from database.charachter_db import insert_video_creator

def upsert_video_chunks_to_pinecone(video_id: str):
    """
    Retrieves text chunks for a given video ID from the SQLite database,
    fetches the creator ID, and upserts them into both dense and sparse
    Pinecone indexes with video_id, chunk_index, and creator_id in metadata.

    Args:
        video_id (str): The YouTube video ID.
    """
    if not settings:
        print("Settings not loaded. Cannot proceed with Pinecone upsert.")
        return

    conn = None
    chunks_data = []
    creator_id = None

    try:
        conn = sqlite3.connect('video_chunks.db')
        cursor = conn.cursor()
        print(f"Connected to database: video_chunks.db")

        cursor.execute("SELECT creator_id FROM video_creators WHERE video_id = ?", (video_id,))
        creator_row = cursor.fetchone()
        if creator_row:
            creator_id = creator_row[0]
            print(f"Retrieved creator ID: {creator_id} for video ID: {video_id}")
        else:
            print(f"No creator ID found for video ID: {video_id}. Cannot proceed with upsert.")
            return

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
        insert_video_creator(video_id=video_id, creator_id=creator_id)
    except Exception as e:
        print(f"An error occurred during video creator insertion: {e}")

    try:
        pc = Pinecone(api_key=settings.pinecone_api_key)

        try:
            records_to_upsert_dense = []
            for i, text in enumerate(chunks_data):
                record_id = f"{video_id}-{i}"
                records_to_upsert_dense.append({
                    "_id": record_id,
                    "text": text,
                    "video_id": video_id,
                    "chunk_index": i,
                    "creator_id": creator_id
                })
            print(f"Prepared {len(records_to_upsert_dense)} records for dense index upsert.")

            index = pc.Index(name='character')
            index.upsert_records(records=records_to_upsert_dense, namespace=settings.pinecone_namespace)
            print(f"Successfully attempted to upsert {len(records_to_upsert_dense)} records to the dense Pinecone index.")
        except Exception as e:
            print(f"An error occurred during dense index upsert: {e}")

        try:
            records_to_upsert_sparse = []
            for i, text in enumerate(chunks_data):
                record_id = f"{video_id}-{i}"
                records_to_upsert_sparse.append({
                    "_id": record_id,
                    "text": text,
                    "video_id": video_id,
                    "chunk_index": i,
                    "creator_id": creator_id
                })
            print(f"Prepared {len(records_to_upsert_sparse)} records for sparse index upsert.")

            sparse_index = pc.Index(name='character-sparse')
            sparse_index.upsert_records(records=records_to_upsert_sparse, namespace=settings.pinecone_namespace)
            print(f"Successfully attempted to upsert {len(records_to_upsert_sparse)} records to the sparse Pinecone index.")
        except Exception as e:
            print(f"An error occurred during sparse index upsert: {e}")

    except Exception as e:
        print(f"An error occurred during Pinecone operations: {e}")