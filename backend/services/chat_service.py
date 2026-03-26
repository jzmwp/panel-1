"""Chat service that manages conversation history and streams responses."""

import json
import logging
from typing import AsyncGenerator

from sqlalchemy.orm import Session

from backend.models.chat import ChatMessage
from backend.ai.client import chat_with_tools

logger = logging.getLogger(__name__)


async def stream_chat_response(
    user_message: str,
    session_id: int,
    db: Session,
) -> AsyncGenerator[dict, None]:
    """Stream a chat response, loading conversation history from the database."""

    # Load recent conversation history (last 20 messages for context)
    history_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.desc())
        .limit(20)
        .all()
    )
    history_msgs.reverse()  # oldest first

    # Build conversation history for Claude (exclude the current user message we just saved)
    conversation_history = []
    for msg in history_msgs[:-1]:  # exclude last message (the one we just saved)
        conversation_history.append({
            "role": msg.role,
            "content": msg.content,
        })

    async for chunk in chat_with_tools(user_message, conversation_history):
        yield chunk
