import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from backend.database import get_db
from backend.models.chat import ChatSession, ChatMessage
from backend.schemas.chat import ChatRequest, ChatSessionOut, ChatSessionListOut
from backend.services.chat_service import stream_chat_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message")
async def chat_message(data: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and receive a streamed response via SSE."""
    # Get or create session
    if data.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == data.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(title=data.message[:100])
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=data.message,
    )
    db.add(user_msg)
    db.commit()

    async def event_generator():
        # Send session info first
        yield {
            "event": "session",
            "data": json.dumps({"session_id": session.id}),
        }

        full_response = ""
        queries_executed = []

        try:
            async for chunk in stream_chat_response(data.message, session.id, db):
                if chunk["type"] == "text":
                    full_response += chunk["content"]
                    yield {
                        "event": "text",
                        "data": json.dumps({"content": chunk["content"]}),
                    }
                elif chunk["type"] == "tool_start":
                    yield {
                        "event": "tool_start",
                        "data": json.dumps({"tool": chunk.get("tool", "")}),
                    }
                elif chunk["type"] == "tool_use":
                    queries_executed.append(chunk.get("query", ""))
                    yield {
                        "event": "tool",
                        "data": json.dumps(chunk),
                    }
                elif chunk["type"] == "chart":
                    yield {
                        "event": "chart",
                        "data": json.dumps({"image": chunk["image"]}),
                    }
                elif chunk["type"] == "error":
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": chunk["content"]}),
                    }
        except Exception as e:
            logger.exception("Chat stream error")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

        # Save assistant message
        if full_response:
            assistant_msg = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=full_response,
                queries_executed=json.dumps(queries_executed) if queries_executed else None,
            )
            db.add(assistant_msg)
            db.commit()

        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_generator())


@router.get("/sessions", response_model=list[ChatSessionListOut])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).limit(50).all()
    result = []
    for s in sessions:
        result.append(ChatSessionListOut(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            message_count=len(s.messages),
        ))
    return result


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
