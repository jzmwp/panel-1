from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    queries_executed: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ChatSessionOut(BaseModel):
    id: int
    title: str | None = None
    created_at: datetime
    messages: list[ChatMessageOut] = []
    model_config = {"from_attributes": True}


class ChatSessionListOut(BaseModel):
    id: int
    title: str | None = None
    created_at: datetime
    message_count: int = 0
    model_config = {"from_attributes": True}
