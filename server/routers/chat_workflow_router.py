from fastapi import APIRouter, Body
from services.process_user_message import handle_chat_message

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/process_message")
def process_message(
    user_id: str = Body(...),
    message_content: str = Body(...),
    summarization_threshold: int = Body(3)
):
    """
    Main workflow endpoint: processes a user message, triggers summarization and clearing as needed.
    """
    handle_chat_message(user_id, message_content, summarization_threshold)
    return {"message": "Message processed and workflow executed."}