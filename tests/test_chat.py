def test_chat_sync_returns_reply_and_sources(client, mock_llm):
    response = client.post("/api/chat/sync", json={"message": "Como funcionava o Pac-Man?"})
    assert response.status_code == 200
    body = response.json()
    assert body["reply"].startswith("resposta simulada")
    assert "pac-man-1980" in body["marcos"]


def test_chat_sync_accepts_history(client, mock_llm):
    payload = {
        "message": "E o Deep Blue?",
        "history": [
            {"role": "user", "content": "Quem é você?"},
            {"role": "assistant", "content": "Sou a Histor.IA."},
        ],
    }
    response = client.post("/api/chat/sync", json=payload)
    assert response.status_code == 200


def test_chat_sync_rejects_empty_message(client, mock_llm):
    response = client.post("/api/chat/sync", json={"message": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_chat_sync_rejects_message_too_long(client, mock_llm):
    response = client.post("/api/chat/sync", json={"message": "a" * 2001})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_chat_sync_rejects_missing_message(client, mock_llm):
    response = client.post("/api/chat/sync", json={})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_chat_sync_llm_unavailable(client, mock_llm_unavailable):
    response = client.post("/api/chat/sync", json={"message": "Oi"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_unavailable"


def test_chat_stream_emits_token_sources_and_done(client, mock_llm):
    response = client.post("/api/chat", json={"message": "Como funcionava o Pac-Man?"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert "event: token" in body
    assert '{"text": "Ol\\u00e1"}' in body or "Olá" in body
    assert "event: sources" in body
    assert "pac-man-1980" in body
    assert "event: done" in body


def test_chat_stream_emits_error_event_on_llm_failure(client, mock_llm_unavailable):
    response = client.post("/api/chat", json={"message": "Oi"})
    assert response.status_code == 200
    body = response.text
    assert "event: error" in body
    assert "llm_unavailable" in body
