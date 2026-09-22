import pytest
from fastapi.testclient import TestClient

from app.errors import LLMUnavailableError
from app.main import app
from app.services import llm as llm_service


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def mock_llm(monkeypatch):
    """Substitui app/services/llm.py por um fake. Testes nunca chamam a API de verdade."""

    async def fake_generate_reply(system_prompt: str, history: list[dict], message: str) -> str:
        return f"resposta simulada para: {message}"

    async def fake_stream_reply(system_prompt: str, history: list[dict], message: str):
        for chunk in ["Olá", ", ", "mundo!"]:
            yield chunk

    monkeypatch.setattr(llm_service, "generate_reply", fake_generate_reply)
    monkeypatch.setattr(llm_service, "stream_reply", fake_stream_reply)


@pytest.fixture()
def mock_llm_unavailable(monkeypatch):
    async def fake_generate_reply(system_prompt: str, history: list[dict], message: str) -> str:
        raise LLMUnavailableError()

    async def fake_stream_reply(system_prompt: str, history: list[dict], message: str):
        raise LLMUnavailableError()
        yield  # pragma: no cover - necessário para ser um async generator

    monkeypatch.setattr(llm_service, "generate_reply", fake_generate_reply)
    monkeypatch.setattr(llm_service, "stream_reply", fake_stream_reply)
