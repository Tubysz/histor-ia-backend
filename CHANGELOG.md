# Changelog

Todas as mudanças relevantes de rotas, payloads ou formato de resposta da
API são registradas aqui, no mesmo commit em que acontecem — junto com a
atualização correspondente em [`docs/API.md`](docs/API.md).

## [0.1.0] — 2026-09-22

Primeira versão do backend.

### Adicionado

- `GET /api/health` — checagem de disponibilidade do servidor.
- `GET /api/eras` — lista as eras da linha do tempo.
- `GET /api/timeline` (com filtro opcional `?era=`) — lista os marcos históricos em ordem cronológica, versão resumida.
- `GET /api/timeline/{id}` — marco completo, com `404 not_found` se não existir.
- `POST /api/chat` — chat com streaming via SSE (eventos `token`, `sources`, `done`, `error`).
- `POST /api/chat/sync` — mesmo chat, sem streaming, para testes de integração.
- Formato padrão de erro (`{"error": {"code", "message"}}`) para `validation_error`, `not_found`, `llm_unavailable` e `internal_error`.
- Base de conhecimento inicial em `data/timeline.json`, com 6 eras e 17 marcos (Nimrod 1951 → agentes generativos/NPCs com LLM, 2023).
- Suíte de testes (`pytest`) cobrindo todas as rotas, com o LLM sempre mockado.
