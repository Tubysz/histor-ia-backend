import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.errors import LLMUnavailableError
from app.schemas.chat import ChatRequest, ChatSyncResponse
from app.services import knowledge, llm, prompt

router = APIRouter(tags=["chat"])


def _trim_history(payload: ChatRequest) -> list[dict]:
    history = [{"role": m.role, "content": m.content} for m in (payload.history or [])]
    limit = get_settings().MAX_HISTORY_MESSAGES
    return history[-limit:] if limit > 0 else history


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(payload: ChatRequest) -> StreamingResponse:
    marcos = knowledge.search_relevant(payload.message)
    system_prompt = prompt.build_system_prompt(marcos)
    history = _trim_history(payload)

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for delta in llm.stream_reply(system_prompt, history, payload.message):
                yield _sse_event("token", {"text": delta})
            yield _sse_event("sources", {"marcos": [m["id"] for m in marcos]})
            yield _sse_event("done", {})
        except LLMUnavailableError as exc:
            yield _sse_event("error", {"code": exc.code, "message": exc.message})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat/sync", response_model=ChatSyncResponse)
async def chat_sync(payload: ChatRequest) -> ChatSyncResponse:
    marcos = knowledge.search_relevant(payload.message)
    system_prompt = prompt.build_system_prompt(marcos)
    history = _trim_history(payload)

    reply = await llm.generate_reply(system_prompt, history, payload.message)
    return ChatSyncResponse(reply=reply, marcos=[m["id"] for m in marcos])
