import sqlite3
import time
from typing import List


def create_chat_messages_table(db_name: str = 'user_data.db', table_name: str = 'chat_messages'):
    """
    Creates a table to store individual chat messages in an SQLite database.

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
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message_content TEXT,
                timestamp REAL
            )
        ''')
        conn.commit()
        print(f"Table '{table_name}' created or already exists.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# Example usage:
# create_chat_messages_table()


def store_chat_message(user_id: str, message_content: str, db_name: str = 'user_data.db', table_name: str = 'chat_messages'):
    """
    Inserts a single chat message into the chat_messages table.

    Args:
        user_id (str): The unique identifier for the user.
        message_content (str): The content of the chat message.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        current_timestamp = time.time()

        cursor.execute(f'''
            INSERT INTO {table_name} (user_id, message_content, timestamp)
            VALUES (?, ?, ?)
        ''', (user_id, message_content, current_timestamp))
        conn.commit()
        print(f"Inserted message for user '{user_id}'.")

    except Exception as e:
        print(f"An error occurred during message insertion: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


def get_recent_chat_history_from_db(user_id: str, num_messages: int = 20, db_name: str = 'user_data.db', table_name: str = 'chat_messages') -> List[str]:
    """
    Retrieves a user's recent chat messages from the chat_messages table.

    Args:
        user_id (str): The unique identifier for the user.
        num_messages (int): The maximum number of recent messages to retrieve.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.

    Returns:
        List[str]: A list of strings, where each string represents a message content.
                   Returns an empty list if no messages are found or an error occurs.
    """
    conn = None
    messages = []
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        cursor.execute(f'''
            SELECT message_content
            FROM {table_name}
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, num_messages))

        rows = cursor.fetchall()

        if rows:
            messages = [row[0] for row in rows]
            print(f"Retrieved {len(messages)} recent messages for user '{user_id}'.")
        else:
            print(f"No recent messages found for user '{user_id}'.")

    except Exception as e:
        print(f"An error occurred during message retrieval: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

    # Reverse the list to get messages in chronological order
    messages.reverse()
    return messages

def clear_old_chat_messages(user_id: str, db_name: str = 'user_data.db', table_name: str = 'chat_messages'):
    """
    Removes old individual chat messages for a specific user from the chat_messages table.
    For simplicity, this function deletes all messages for the given user.

    Args:
        user_id (str): The unique identifier for the user.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        cursor.execute(f'''
            DELETE FROM {table_name}
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

        deleted_count = cursor.rowcount
        print(f"Deleted {deleted_count} old messages for user '{user_id}'.")

    except Exception as e:
        print(f"An error occurred during message deletion: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# Example usage :
# test_user_id_clear = "clear_messages_test_user"
# add_user(test_user_id_clear) # Ensure the user exists

# # Add some messages to be cleared
# store_chat_message(test_user_id_clear, "Message to be deleted 1.")
# store_chat_message(test_user_id_clear, "Message to be deleted 2.")
# store_chat_message(test_user_id_clear, "Message to be deleted 3.")

# # Verify messages were added
# print("\n--- Messages before clearing ---")
# messages_before = get_recent_chat_history_from_db(test_user_id_clear, num_messages=10)
# if messages_before:
#     for msg in messages_before:
#         print(msg)
# else:
#     print("No messages found before clearing.")

# # Clear the messages
# print("\n--- Clearing messages ---")
# clear_old_chat_messages(test_user_id_clear)

# # Verify messages were deleted
# print("\n--- Messages after clearing ---")
# messages_after = get_recent_chat_history_from_db(test_user_id_clear, num_messages=10)
# if messages_after:
#     for msg in messages_after:
#         print(msg)
# else:
#     print("No messages found after clearing.")