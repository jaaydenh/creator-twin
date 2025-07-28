from services.summary import summarize_chat_history
from database.user_db import (
    get_user_info, add_user, update_chat_summary_in_db,
    update_user_chat_info, check_rate_limit
)
from database.messages_db import (
    store_chat_message, get_recent_chat_history_from_db, clear_old_chat_messages
)
from services.summary import summarize_chat_history

def handle_chat_message(user_id: str, message_content: str, summarization_threshold: int = 3):
    """
    Processes an incoming chat message, checks rate limit, stores it, updates user info,
    and triggers summarization and clearing of old messages based on a message count threshold.
    """
    print(f"\n--- Processing message for user '{user_id}' ---")
    print(f"Message: {message_content}")

    # Ensure user exists
    add_user(user_id)

    # Check rate limit
    if check_rate_limit(user_id = user_id, chat_limit_24h= 10):
        print(f"Rate limit exceeded for user '{user_id}'. Message not processed.")
        return "Rate limit exceeded."

    # Store the incoming message
    store_chat_message(user_id, message_content)
    print(f"Stored message for user '{user_id}'.")

    # Update user chat info (timestamp, count)
    update_user_chat_info(user_id)
    print(f"Updated chat info for user '{user_id}'.")

    # Retrieve all messages for the user to check the count.
    all_user_messages = get_recent_chat_history_from_db(user_id, num_messages=1000000)

    if len(all_user_messages) > 0 and len(all_user_messages) % summarization_threshold == 0:
        print(f"\n--- Triggering summarization for user '{user_id}' after {len(all_user_messages)} messages ---")
        relevant_history = all_user_messages

        if relevant_history:
            print("Generating summary...")
            summary = summarize_chat_history(relevant_history)
            print("Generated Summary:")
            print(summary)

            print("Updating database with summary...")
            update_chat_summary_in_db(user_id, summary)
            print("Database update attempted.")

            print("Clearing old chat messages...")
            clear_old_chat_messages(user_id)
            print("Old chat messages clearing attempted.")
        else:
            print("No history to summarize.")

    print(f"--- Finished processing message for user '{user_id}' ---")
    return "Message processed."

# 5. Execute the modified handle_chat_message function
# test_user_id_workflow = "workflow_test_user"
# add_user(test_user_id_workflow) # Ensure the user exists and is added to the users table

# # Clear any previous messages for this user to start fresh for the test
# clear_old_chat_messages(test_user_id_workflow)

# # Simulate a chat conversation to trigger summarization and clearing
# print("\n--- Simulating chat conversation to trigger workflow ---")
# handle_chat_message(test_user_id_workflow, "User: I have an issue with my account settings.")
# handle_chat_message(test_user_id_workflow, "Agent: Could you please describe the problem in more detail?")
# handle_chat_message(test_user_id_workflow, "User: I cannot find the option to change my email address.") # This should trigger summarization and clearing
# handle_chat_message(test_user_id_workflow, "Agent: I see. Let me guide you through the steps.")
# handle_chat_message(test_user_id_workflow, "User: Okay, I'm ready.")
# handle_chat_message(test_user_id_workflow, "Agent: Great. First, navigate to the profile section.") # This should trigger summarization and clearing

# print("\n--- Conversation simulation finished ---")

# # Verify the final state
# final_user_data = get_user_info(test_user_id_workflow)
# if final_user_data:
#     print(f"\n--- Final User Info after Workflow Simulation ---")
#     print(f"User ID: {final_user_data[0]}")
#     print(f"Final Chat History Summary: {final_user_data[3]}")

# # Verify chat messages table state for this user
# print("\n--- Messages in chat_messages table after workflow ---")
# messages_after_workflow = get_recent_chat_history_from_db(test_user_id_workflow, num_messages=10)
# if messages_after_workflow:
#     for msg in messages_after_workflow:
#         print(msg)
# else:
#     print("No messages found in chat_messages table after workflow.")
