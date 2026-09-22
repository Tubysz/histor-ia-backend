"""Única camada que fala com o provedor de LLM. Rotas nunca importam `anthropic` diretamente."""

from collections.abc import AsyncIterator

import anthropic

from app.config import get_settings
from app.errors import LLMUnavailableError

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=get_settings().ANTHROPIC_API_KEY)
    return _client


def _to_api_messages(history: list[dict], message: str) -> list[dict]:
    messages = [{"role": item["role"], "content": item["content"]} for item in history]
    messages.append({"role": "user", "content": message})
    return messages


async def generate_reply(system_prompt: str, history: list[dict], message: str) -> str:
    settings = get_settings()
    try:
        response = await _get_client().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.MAX_TOKENS,
            system=system_prompt,
            messages=_to_api_messages(history, message),
        )
    except anthropic.APIError as exc:
        raise LLMUnavailableError() from exc

    return "".join(block.text for block in response.content if block.type == "text")


async def stream_reply(system_prompt: str, history: list[dict], message: str) -> AsyncIterator[str]:
    settings = get_settings()
    try:
        async with _get_client().messages.stream(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.MAX_TOKENS,
            system=system_prompt,
            messages=_to_api_messages(history, message),
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except anthropic.APIError as exc:
        raise LLMUnavailableError() from exc
