from fastapi import APIRouter, Body
from typing import List
from services.summary import summarize_chat_history
from database.messages_db import (
    store_chat_message,
    get_recent_chat_history_from_db,
    clear_old_chat_messages,
)
from database.user_db import add_user
from database.messages_db import create_chat_messages_table
from database.user_db import create_user_table, get_user_info

router = APIRouter(prefix="/user_db", tags=["user_db"])

@router.post("/summarize_chat_history")
def summarize_history_endpoint(chat_history: List[str] = Body(...)):
    summary = summarize_chat_history(chat_history)
    return {"summary": summary}

@router.post("/store_chat_message")
def store_message_endpoint(user_id: str = Body(...), message_content: str = Body(...)):
    store_chat_message(user_id, message_content)
    return {"message": "Message stored."}

@router.get("/get_recent_chat_history")
def get_history_endpoint(user_id: str, num_messages: int = 20):
    messages = get_recent_chat_history_from_db(user_id, num_messages)
    return {"messages": messages}

@router.post("/clear_old_chat_messages")
def clear_messages_endpoint(user_id: str = Body(...)):
    clear_old_chat_messages(user_id)
    return {"message": "Old messages cleared."}

@router.post("/add_user")
def add_user_endpoint(user_id: str = Body(...)):
    add_user(user_id)
    return {"message": f"User '{user_id}' added."}

@router.post("/create_tables")
def create_tables_endpoint():
    create_chat_messages_table()
    create_user_table()
    return {"message": "Tables created."}

@router.get("/get_user_info")
def get_user_info_endpoint(user_id: str):
    user_info = get_user_info(user_id)
    if user_info:
        return {"user_info": user_info}
    else:
        return {"message": f"No information found for user '{user_id}'."}

