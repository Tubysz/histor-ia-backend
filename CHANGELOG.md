# Changelog

Todas as mudanças relevantes de rotas, payloads ou formato de resposta da
API são registradas aqui, no mesmo commit em que acontecem — junto com a
atualização correspondente em [`docs/API.md`](docs/API.md).

## [Não lançado]

### Adicionado

- Seção "Expor pela internet" no README: como rodar o backend numa máquina
  e consumir de um frontend publicado em outra rede, via túnel (Cloudflare
  Tunnel) + `CORS_ORIGINS` + o parâmetro `?api=` do frontend.

### Alterado

- `run.sh` agora sobe o uvicorn em `--host 0.0.0.0` (antes: só `localhost`),
  necessário pra ser alcançável por um túnel ou pela rede local.

- Respostas mais curtas ainda: persona limitada a 2 frases (antes: 2
  parágrafos / 3-4 frases) e `MAX_TOKENS` de 400 para 150. Motivo: o
  frontend é uma assistente só de voz (TTS lê a resposta em voz alta), então
  resposta longa = espera longa pro visitante ouvir tudo, em cima do tempo
  de geração já lento no hardware local.

- **Provedor de LLM trocado de Anthropic (API paga, em nuvem) para Ollama
  local** (`app/services/llm.py`). Motivo: projeto escolar sem orçamento
  para API paga — Ollama roda local, de graça, sem depender de internet.
  `OLLAMA_MODEL` no `.env` escolhe o modelo (padrão: `llama3.2:1b`).
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
- **Escolha e ajuste do modelo local, com benchmark real em hardware fraco**
  (CPU só, 4 núcleos, ~8GB RAM — sem GPU). Testado em CPU-only, 4 núcleos,
  ~8GB RAM, nesse hardware:
  - `qwen2.5:3b` (3B, Q4): >120s por resposta (chegou a estourar timeout de
    120s do cliente HTTP). Descartado — grande demais pro hardware.
  - Um modelo Q8_0 de 1B testado: ~120-180s por resposta. A quantização Q8
    (menos compressão) pesa mais que o tamanho do modelo sugere.
  - `llama3.2:1b` (Q4, o padrão da biblioteca do Ollama): ~20-35s por
    resposta já com o modelo "aquecido" (carregado uma vez na memória — a
    primeira chamada depois de trocar de modelo é mais lenta, ~40s, por
    causa do carregamento). **Virou o padrão.**
  - `MAX_TOKENS` baixado de 1024 para 400: um teto baixo sozinho cortava
    respostas no meio da frase quando o modelo ignorava o limite de
    tamanho pedido no prompt — o que resolveu de verdade foi deixar a
    instrução de tamanho no `prompt.py` mais concreta ("no máximo 2
    parágrafos curtos, 3-4 frases", sem listas) em vez de "até ~4
    parágrafos", que modelos pequenos seguem mal.
  - Pra apresentação ao vivo: vale "esquentar" o modelo com uma pergunta
    de teste antes da plateia chegar — a primeira chamada depois de subir
    o servidor é sempre mais lenta.

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
