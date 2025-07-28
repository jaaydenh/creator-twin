from config.gemini_config import generate
from typing import List

def summarize_chat_history(chat_history: List[str]) -> str:
    """
    Summarizes a list of chat messages using the generate function.

    Args:
        chat_history (List[str]): A list of strings representing the chat history.

    Returns:
        str: A concise summary of the chat history.
    """
    if not chat_history:
        return "No chat history to summarize."

    concatenated_history = "\n".join(chat_history)

    prompt = "Please summarize the following chat history:\n"
    text_to_summarize = prompt + concatenated_history

    summary = generate(text_to_summarize)

    return summary

# Example usage:
# sample_history_for_summary = [
#     "User: What is the weather like today?",
#     "Agent: The weather today is sunny with a high of 75 degrees Fahrenheit.",
#     "User: That sounds nice. Is there any chance of rain?",
#     "Agent: No, there is no chance of rain today.",
#     "User: Great, thanks!"
# ]

# chat_summary = summarize_chat_history(sample_history_for_summary)
# print("\n--- Chat Summary ---")
# print(chat_summary)

# # Example with empty history
# empty_history_summary = summarize_chat_history([])
# print("\n--- Empty History Summary ---")
# print(empty_history_summary)
