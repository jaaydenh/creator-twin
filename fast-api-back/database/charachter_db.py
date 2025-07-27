import sqlite3
from tools.transcript import video_to_chunks

def store_video_chunks_in_db(video_id: str = "iv-5mZ_9CPY", db_name: str = 'character_db.db', table_name: str = 'chunks'):
    """
    Fetches video transcript chunks and stores them in an SQLite database.
    Checks if chunks for the video ID already exist before inserting.

    Args:
        video_id (str): The ID of the YouTube video.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                video_id TEXT,
                chunk_text TEXT
            )
        ''')
        print(f"Table '{table_name}' created or already exists.")

        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE video_id = ?", (video_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"Chunks for video ID: {video_id} already exist. Skipping insertion.")
        else:
            chunks_data = video_to_chunks(video_id)
            print(f"Number of chunks retrieved: {len(chunks_data)}")

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
        if conn:
            conn.close()
            print("Database connection closed.")



def create_video_creator_table(db_name: str = 'character_db.db', table_name: str = 'video_creators'):
    """
    Creates a table to store video IDs and creator IDs in an SQLite database.

    Args:
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                video_id TEXT PRIMARY KEY,
                creator_id TEXT
            )
        ''')
        print(f"Table '{table_name}' created or already exists.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

def insert_video_creator(video_id: str, creator_id: str, db_name: str = 'video_chunks.db', table_name: str = 'video_creators'):
    """
    Inserts a video ID and creator ID into the video_creators table.
    If the video ID already exists, it will be ignored due to the PRIMARY KEY constraint.

    Args:
        video_id (str): The ID of the YouTube video.
        creator_id (str): The ID of the creator.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        cursor.execute(f'''
            INSERT OR IGNORE INTO {table_name} (video_id, creator_id)
            VALUES (?, ?)
        ''', (video_id, creator_id))
        conn.commit()
        print(f"Inserted video ID: {video_id} with creator ID: {creator_id} (if not already exists).")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")