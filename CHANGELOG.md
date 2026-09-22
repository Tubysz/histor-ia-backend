# Changelog

Todas as mudanças relevantes de rotas, payloads ou formato de resposta da
API são registradas aqui, no mesmo commit em que acontecem — junto com a
atualização correspondente em [`docs/API.md`](docs/API.md).

## [Não lançado]

### Alterado

- **Provedor de LLM trocado de Anthropic (API paga, em nuvem) para Ollama
  local** (`app/services/llm.py`). Motivo: projeto escolar sem orçamento
  para API paga — Ollama roda local, de graça, sem depender de internet.
  `OLLAMA_MODEL` no `.env` escolhe o modelo (padrão: `qwen2.5:3b`; troque por
  um modelo menor se `qwen2.5:3b` for lento demais para o hardware do dia da
  apresentação).
  - **O contrato da API não muda**: rotas, payloads e formato de resposta de
    `/api/chat` e `/api/chat/sync` são exatamente os mesmos — só a
    implementação interna de `llm.py` mudou. Nada a atualizar em
    `docs/API.md` por causa disso.
  - `.env.example` trocou `ANTHROPIC_API_KEY`/`ANTHROPIC_MODEL` por
    `OLLAMA_HOST`/`OLLAMA_MODEL`.
  - `requirements.txt` perdeu a dependência `anthropic`.
  - `knowledge.search_relevant` reduziu o número padrão de marcos injetados
    no prompt de 5 para 3, pra manter o prompt menor e a resposta mais
    rápida em hardware sem GPU.
- Adicionado `run.sh`: sobe o backend com um único comando (`./run.sh`) —
  cria `.venv`, instala dependências, cria `.env` se faltar, avisa se o
  Ollama ou o modelo configurado não estiverem prontos, e inicia o servidor.

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
