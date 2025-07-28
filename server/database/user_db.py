import sqlite3
import time

def create_user_table(db_name: str = 'user_data.db', table_name: str = 'users'):
    """
    Creates a table to store user information, including rate limiting and chat history summary,
    in an SQLite database.

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
                user_id TEXT PRIMARY KEY,
                last_chat_timestamp REAL,
                chat_count_24h INTEGER DEFAULT 0,
                chat_history_summary TEXT
            )
        ''')
        print(f"Table '{table_name}' created or already exists.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# Example usage:
# create_user_table()


def add_user(user_id: str, db_name: str = 'user_data.db', table_name: str = 'users'):
    """
    Adds a new user to the users table if they don't already exist.

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
            INSERT OR IGNORE INTO {table_name} (user_id, last_chat_timestamp, chat_count_24h, chat_history_summary)
            VALUES (?, ?, ?, ?)
        ''', (user_id, None, 0, None))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"User '{user_id}' added successfully.")
        else:
            print(f"User '{user_id}' already exists in the database.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")



def update_user_chat_info(user_id: str, db_name: str = 'user_data.db', table_name: str = 'users'):
    """
    Updates a user's chat information, including the last chat timestamp and increments the chat count.

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

        current_timestamp = time.time()

        cursor.execute(f'''
            UPDATE {table_name}
            SET last_chat_timestamp = ?,
                chat_count_24h = chat_count_24h + 1
            WHERE user_id = ?
        ''', (current_timestamp, user_id))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Updated chat info for user '{user_id}'.")
        else:
            print(f"User '{user_id}' not found. Please add the user first.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")



def get_user_info(user_id: str, db_name: str = 'user_data.db', table_name: str = 'users'):
    """
    Retrieves a user's information from the users table.

    Args:
        user_id (str): The unique identifier for the user.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.

    Returns:
        tuple: A tuple containing the user's information (user_id, last_chat_timestamp, chat_count_24h, chat_history_summary)
               or None if the user is not found.
    """
    conn = None
    user_info = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        cursor.execute(f'''
            SELECT user_id, last_chat_timestamp, chat_count_24h, chat_history_summary
            FROM {table_name}
            WHERE user_id = ?
        ''', (user_id,))
        user_info = cursor.fetchone()

        if user_info:
            print(f"Retrieved info for user '{user_id}'.")
        else:
            print(f"User '{user_id}' not found.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

    return user_info




def check_rate_limit(user_id: str, chat_limit_24h: int = 100, db_name: str = 'user_data.db', table_name: str = 'users'):
    """
    Checks if a user has exceeded the rate limit based on their chat count and last chat timestamp.

    Args:
        user_id (str): The unique identifier for the user.
        chat_limit_24h (int): The maximum number of chats allowed within a 24-hour period.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.

    Returns:
        bool: True if the user has exceeded the rate limit, False otherwise.
    """
    user_info = get_user_info(user_id, db_name, table_name)

    if user_info:
        user_id, last_chat_timestamp, chat_count_24h, chat_history_summary = user_info
        current_timestamp = time.time()
        hours_since_last_chat = (current_timestamp - (last_chat_timestamp if last_chat_timestamp else current_timestamp)) / 3600

        # Reset chat count if more than 24 hours have passed since the last chat
        if hours_since_last_chat >= 24:
            reset_user_chat_count(user_id, db_name, table_name)
            chat_count_24h = 0 # Reset locally for this check

        if chat_count_24h >= chat_limit_24h:
            print(f"Rate limit exceeded for user '{user_id}'.")
            return True
        else:
            print(f"User '{user_id}' is within the rate limit.")
            return False
    else:
        print(f"User '{user_id}' not found. Rate limit check skipped.")
        return False # Cannot check rate limit for a non-existent user

def reset_user_chat_count(user_id: str, db_name: str = 'user_data.db', table_name: str = 'users'):
    """
    Resets the chat count for a user.

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
            UPDATE {table_name}
            SET chat_count_24h = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Chat count reset for user '{user_id}'.")
        else:
            print(f"User '{user_id}' not found for chat count reset.")

    except Exception as e:
        print(f"An error occurred during chat count reset: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# Example usage (you can run this cell to test):
# # Define a test user ID and a rate limit
# test_user_id = "rate_limit_test_user"
# add_user(test_user_id) # Add the test user first
# reset_user_chat_count(test_user_id) # Reset the chat count
# update_user_chat_info(test_user_id) # Simulate a chat

# # Check the rate limit
# if check_rate_limit(test_user_id, chat_limit_24h=2):
#     print("User hit the rate limit.")
# else:
#     print("User is good to go.")

# # Simulate another chat and check again
# update_user_chat_info(test_user_id)
# if check_rate_limit(test_user_id, chat_limit_24h=2):
#     print("User hit the rate limit.")
# else:
#     print("User is good to go.")



def update_chat_summary_in_db(user_id: str, summary: str, db_name: str = 'user_data.db', table_name: str = 'users'):
    """
    Updates the chat_history_summary column for a specific user in the users table.

    Args:
        user_id (str): The unique identifier for the user.
        summary (str): The chat history summary to store.
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table within the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")

        cursor.execute(f'''
            UPDATE {table_name}
            SET chat_history_summary = ?
            WHERE user_id = ?
        ''', (summary, user_id))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Updated chat history summary for user '{user_id}'.")
        else:
            print(f"User '{user_id}' not found. Summary not updated.")

    except Exception as e:
        print(f"An error occurred during database update: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# Example usage :
# # Ensure the user exists first
# add_user("summary_test_user")
# # Update the summary for the test user
# update_chat_summary_in_db("summary_test_user", "This is a test summary of the chat history.")

# # Verify the update (optional, using the get_user_info function from a previous cell)
# user_data_after_update = get_user_info("summary_test_user")
# if user_data_after_update:
#     print(f"\nUser ID: {user_data_after_update[0]}")
#     print(f"Last Chat Timestamp: {user_data_after_update[1]}")
#     print(f"Chat Count (24h): {user_data_after_update[2]}")
#     print(f"Chat History Summary: {user_data_after_update[3]}")