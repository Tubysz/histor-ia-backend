"""Única camada que fala com o provedor de LLM. Rotas nunca importam httpx/Ollama diretamente.

Usa a API local do Ollama (http://localhost:11434 por padrão) — sem custo, sem
internet, sem chave de API. Troque `OLLAMA_MODEL` no `.env` para usar outro
modelo já baixado (`ollama list` mostra os disponíveis)."""

import json
from collections.abc import AsyncIterator

import httpx

from app.config import get_settings
from app.errors import LLMUnavailableError


def _to_ollama_messages(system_prompt: str, history: list[dict], message: str) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": item["role"], "content": item["content"]} for item in history]
    messages.append({"role": "user", "content": message})
    return messages


def _payload(system_prompt: str, history: list[dict], message: str, *, stream: bool) -> dict:
    settings = get_settings()
    return {
        "model": settings.OLLAMA_MODEL,
        "messages": _to_ollama_messages(system_prompt, history, message),
        "stream": stream,
        "options": {"num_predict": settings.MAX_TOKENS},
    }


async def generate_reply(system_prompt: str, history: list[dict], message: str) -> str:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(base_url=settings.OLLAMA_HOST, timeout=120.0) as client:
            response = await client.post("/api/chat", json=_payload(system_prompt, history, message, stream=False))
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMUnavailableError() from exc

    return response.json()["message"]["content"]


async def stream_reply(system_prompt: str, history: list[dict], message: str) -> AsyncIterator[str]:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(base_url=settings.OLLAMA_HOST, timeout=120.0) as client:
            async with client.stream(
                "POST", "/api/chat", json=_payload(system_prompt, history, message, stream=True)
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    text = chunk.get("message", {}).get("content", "")
                    if text:
                        yield text
                    if chunk.get("done"):
                        break
    except httpx.HTTPError as exc:
        raise LLMUnavailableError() from exc
