# Histor.ia — Backend

## Sobre o projeto

Histor.ia é um projeto escolar: uma IA conversacional que conta a história da inteligência artificial nos jogos, desde os primeiros oponentes controlados por computador e NPCs até as IAs modernas (aprendizado por reforço, NPCs com LLM etc.).

O usuário faz perguntas ("como funcionavam os fantasmas do Pac-Man?", "o que mudou com o F.E.A.R.?") e a IA responde como uma narradora/guia de museu, usando uma linha do tempo curada como base de conhecimento.

## Divisão de responsabilidades (IMPORTANTE)

- **Eu (dono deste repositório) cuido só do BACKEND.**
- **O frontend é feito por um colega**, em outro repositório/pasta. Ele vai consumir esta API.
- Portanto: **não crie frontend, HTML, React, telas ou CSS aqui.** Toda decisão deve facilitar a vida de quem vai consumir a API: contrato estável, documentação clara, CORS liberado, exemplos de requisição/resposta.
- O arquivo `docs/API.md` é o **contrato oficial** com o frontend. Qualquer mudança em rota, payload ou formato de resposta DEVE ser refletida nele e registrada no `CHANGELOG.md` no mesmo commit.

## Stack

- **Python 3.11+**
- **FastAPI** (gera OpenAPI/Swagger automaticamente em `/docs` — o colega do front usa isso pra testar)
- **Uvicorn** como servidor
- **Pydantic v2** para schemas de request/response
- **Ollama local** (API HTTP em `http://localhost:11434`, via `httpx`) para o modelo de linguagem, isolado em `app/services/llm.py` (se um dia trocar de provedor, só esse arquivo muda). Sem custo, sem internet, sem chave de API — só precisa do `ollama serve` rodando e o modelo baixado (`ollama pull <modelo>`)
- **pytest** + `httpx` para testes
- Base de conhecimento em **JSON** (`data/timeline.json`) — sem banco de dados por enquanto
- Configuração via `.env` com `pydantic-settings`

## Estrutura de pastas

```
histor-ia-backend/
├── CLAUDE.md
├── CHANGELOG.md
├── README.md
├── .env.example
├── requirements.txt
├── data/
│   └── timeline.json          # marcos históricos (base de conhecimento)
├── docs/
│   └── API.md                 # contrato com o frontend
├── app/
│   ├── main.py                # cria o app, CORS, inclui routers
│   ├── config.py              # Settings (lê .env)
│   ├── routers/
│   │   ├── health.py
│   │   ├── timeline.py
│   │   └── chat.py
│   ├── schemas/               # modelos Pydantic (request/response)
│   ├── services/
│   │   ├── llm.py             # única camada que fala com o modelo
│   │   ├── knowledge.py       # carrega e busca marcos no timeline.json
│   │   └── prompt.py          # monta o system prompt da persona
│   └── errors.py              # formato padrão de erro
└── tests/
```

## Comandos

```bash
# setup (uma vez)
ollama pull qwen2.5:3b           # ou o modelo que estiver em OLLAMA_MODEL no .env

# rodar em dev — ./run.sh cuida de venv, deps, .env e sobe o servidor
./run.sh

# testes
pytest -q
```

Documentação interativa: http://localhost:8000/docs

## Variáveis de ambiente (`.env.example`)

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
MAX_TOKENS=1024
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_HISTORY_MESSAGES=20
```

Nunca commitar `.env`. `.env` deve estar no `.gitignore`. Como o modelo roda
local via Ollama, não existe chave de API pra proteger — mas `.env` continua
sendo o lugar certo pra configuração específica de máquina (host, modelo).

## Contrato da API (resumo — detalhes em `docs/API.md`)

Prefixo de todas as rotas: `/api`. Tudo em JSON, UTF-8, campos em `snake_case`.

### `GET /api/health`
```json
{ "status": "ok", "version": "0.1.0" }
```

### `GET /api/eras`
Lista as eras para o front montar filtros/abas.
```json
[
  { "id": "pioneiros", "nome": "Pioneiros", "periodo": "1950–1970", "descricao": "..." }
]
```

### `GET /api/timeline?era={id_opcional}`
Lista os marcos em ordem cronológica (versão resumida, para cards).
```json
[
  {
    "id": "pac-man-1980",
    "ano": 1980,
    "titulo": "Pac-Man",
    "era": "arcade",
    "resumo": "Cada fantasma tem um comportamento de perseguição diferente.",
    "tags": ["arcade", "maquina-de-estados"]
  }
]
```

### `GET /api/timeline/{id}`
Marco completo (para página de detalhe). Retorna 404 no formato de erro padrão se não existir.

### `POST /api/chat` (streaming via SSE)
Request:
```json
{
  "message": "Como funcionava a IA dos fantasmas do Pac-Man?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```
- `history` é opcional. **O backend não guarda sessão**: o front manda o histórico a cada requisição.
- O backend corta o histórico para as últimas `MAX_HISTORY_MESSAGES`.

Resposta: `Content-Type: text/event-stream`, eventos neste formato:
```
event: token
data: {"text": "Os fantasmas"}

event: token
data: {"text": " do Pac-Man..."}

event: sources
data: {"marcos": ["pac-man-1980"]}

event: done
data: {}
```
Em caso de erro no meio do stream:
```
event: error
data: {"code": "llm_unavailable", "message": "..."}
```

### `POST /api/chat/sync` (sem streaming)
Mesmo request. Resposta única — útil pro front testar antes de implementar o streaming:
```json
{ "reply": "texto completo", "marcos": ["pac-man-1980"] }
```

### Formato padrão de erro (todas as rotas)
```json
{ "error": { "code": "not_found", "message": "Marco não encontrado." } }
```
Códigos usados: `validation_error` (422), `not_found` (404), `llm_unavailable` (503), `internal_error` (500).

## Base de conhecimento (`data/timeline.json`)

Schema de cada marco:
```json
{
  "id": "slug-ano",
  "ano": 1980,
  "titulo": "Nome do jogo ou marco",
  "era": "id-da-era",
  "resumo": "1 frase curta para card",
  "descricao": "2–4 parágrafos explicando o que a IA fazia e por que importou",
  "tecnica": "ex.: máquina de estados, behavior tree, GOAP, aprendizado por reforço",
  "tags": ["..."],
  "fontes": ["URL ou referência bibliográfica"]
}
```

Sugestões de marcos para popular (conferir datas e detalhes em fontes antes de adicionar):
Nimrod (1951, Nim), OXO (1952, jogo da velha no EDSAC), Space Invaders (1978), Pac-Man (1980), Half-Life (1998, soldados em esquadrão), The Sims (2000, objetos inteligentes e necessidades), Black & White (2001, criatura que aprende), Halo 2 (2004, popularização de behavior trees), F.E.A.R. (2005, GOAP), Oblivion (2006, Radiant AI), Left 4 Dead (2008, AI Director), Alien: Isolation (2014), AlphaGo (2016), OpenAI Five e AlphaStar (2019), agentes generativos e NPCs com LLM (2023 em diante).

Eras sugeridas: `pioneiros`, `arcade`, `3d-e-taticas`, `mundos-vivos`, `aprendizado-de-maquina`, `ia-generativa`.

## Persona da IA (`app/services/prompt.py`)

- Fala em **português do Brasil**, tom de guia de museu: animado, didático, acessível para estudantes do ensino médio.
- Responde **somente sobre a história da IA em jogos** e assuntos diretamente ligados. Se a pergunta fugir do tema, redireciona com educação.
- Usa os marcos do `timeline.json` como fonte principal (os marcos relevantes são injetados no system prompt).
- **Nunca inventa datas, nomes ou fatos.** Se não tiver certeza ou o dado não estiver na base, diz isso claramente.
- Respostas curtas por padrão (até ~4 parágrafos), a não ser que o usuário peça mais.
- Ao final do stream, o backend envia no evento `sources` os `id`s dos marcos usados, para o front poder mostrar links/cards.

Estratégia de recuperação (simples, sem vetor por enquanto): `knowledge.py` faz busca por palavras-chave em `titulo`, `tags`, `tecnica` e `ano`, pega os até 3 marcos mais relevantes e injeta no prompt (número baixo de propósito — o modelo roda local via Ollama em hardware modesto, e um prompt menor responde bem mais rápido). Se nada casar, injeta os resumos de todas as eras.

## Regras para o Claude Code

1. **Não quebrar o contrato.** Antes de mudar qualquer rota ou schema, avise. Se mudar, atualize `docs/API.md` e `CHANGELOG.md` juntos.
2. **Não criar frontend** neste repositório.
3. Toda rota nova precisa de: schema Pydantic de request/response, exemplo no `docs/API.md` e pelo menos um teste.
4. Nos testes, **mockar o LLM** (`app/services/llm.py`) — testes não podem gastar API nem depender de internet.
5. Manter CORS configurável via `CORS_ORIGINS`.
6. Toda chamada ao LLM passa por `services/llm.py`. Rotas não importam o SDK diretamente.
7. Tratar erros do provedor (timeout, rate limit) e devolver no formato padrão (`llm_unavailable`).
8. Validar entrada: `message` obrigatório, entre 1 e 2000 caracteres.
9. Código e comentários podem ser em inglês; textos que o usuário final vê (mensagens de erro, persona) em português.
10. Ao adicionar marcos no `timeline.json`, sempre preencher `fontes`. Projeto escolar: precisão histórica vale nota.
11. Commits pequenos e descritivos.

## Handoff para o frontend

O colega do front precisa só de:
- URL base (dev: `http://localhost:8000/api`)
- `docs/API.md` + Swagger em `/docs`
- Saber que o chat é via SSE (`POST` com `fetch` + leitura do stream; `EventSource` não serve porque não suporta POST) e que existe `/api/chat/sync` como alternativa mais simples.
- Saber que ele é responsável por guardar o histórico da conversa e mandá-lo em cada requisição.
