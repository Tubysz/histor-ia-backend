# API do Histor.ia — Contrato com o Frontend

Este é o contrato oficial entre o backend e o frontend. Qualquer mudança de
rota, payload ou formato de resposta aqui **deve** vir acompanhada de uma
entrada no [`CHANGELOG.md`](../CHANGELOG.md) no mesmo commit.

- **URL base (dev):** `http://localhost:8000/api`
- **Formato:** tudo em JSON, UTF-8, campos em `snake_case`
- **Docs interativas (Swagger):** `http://localhost:8000/docs` (gerado automaticamente pelo FastAPI — bom lugar pra testar as rotas sem escrever código)
- **CORS:** liberado para as origens listadas em `CORS_ORIGINS` no `.env` do backend. Se o front rodar em uma porta diferente da configurada, avise para adicionarmos a origem.

## Índice

- [GET /api/health](#get-apihealth)
- [GET /api/eras](#get-apieras)
- [GET /api/timeline](#get-apitimeline)
- [GET /api/timeline/{id}](#get-apitimelineid)
- [POST /api/chat](#post-apichat) (streaming via SSE)
- [POST /api/chat/sync](#post-apichatsync) (sem streaming)
- [Formato padrão de erro](#formato-padrão-de-erro)

---

## `GET /api/health`

Checagem simples de que o servidor está no ar.

**Resposta `200`:**

```json
{ "status": "ok", "version": "0.1.0" }
```

---

## `GET /api/eras`

Lista as eras da linha do tempo, para o front montar filtros/abas.

**Resposta `200`:**

```json
[
  {
    "id": "arcade",
    "nome": "Arcade",
    "periodo": "1978–1980",
    "descricao": "A era das máquinas de fliperama, onde regras simples e padrões de movimento criavam a ilusão de oponentes inteligentes com hardware muito limitado."
  }
]
```

---

## `GET /api/timeline`

Lista os marcos históricos em ordem cronológica (ano crescente), versão
resumida — pensada para cards de listagem.

**Query params:**

| Param | Obrigatório | Descrição |
|---|---|---|
| `era` | não | Filtra pelo `id` de uma era (ex.: `?era=arcade`). Se a era não existir, retorna lista vazia `[]`, não é erro. |

**Resposta `200`:**

```json
[
  {
    "id": "pac-man-1980",
    "ano": 1980,
    "titulo": "Pac-Man",
    "era": "arcade",
    "resumo": "Cada um dos quatro fantasmas tem um comportamento de perseguição diferente, criando personalidades distintas.",
    "tags": ["arcade", "maquina-de-estados", "pac-man", "fantasmas"]
  }
]
```

---

## `GET /api/timeline/{id}`

Retorna o marco completo, para uma página de detalhe.

**Resposta `200`:**

```json
{
  "id": "pac-man-1980",
  "ano": 1980,
  "titulo": "Pac-Man",
  "era": "arcade",
  "resumo": "Cada um dos quatro fantasmas tem um comportamento de perseguição diferente, criando personalidades distintas.",
  "tags": ["arcade", "maquina-de-estados", "pac-man", "fantasmas"],
  "descricao": "Pac-Man, criado por Toru Iwatani, é um dos exemplos mais citados de IA em jogos clássicos. [...]",
  "tecnica": "máquina de estados com alvos de perseguição distintos",
  "fontes": ["https://pacman.holenet.info/"]
}
```

**Resposta `404`** (id não existe) — ver [formato padrão de erro](#formato-padrão-de-erro).

---

## `POST /api/chat`

Chat com a Histor.IA, **com streaming via SSE** (Server-Sent Events).

> ⚠️ Use `fetch` + leitura manual do stream, não o `EventSource` do navegador
> — `EventSource` não suporta `POST`, e essa rota exige `POST` porque manda
> um corpo JSON (mensagem + histórico).

**Request:**

```json
{
  "message": "Como funcionava a IA dos fantasmas do Pac-Man?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

| Campo | Tipo | Obrigatório | Regras |
|---|---|---|---|
| `message` | string | sim | 1 a 2000 caracteres |
| `history` | array de `{role, content}` | não | `role` é `"user"` ou `"assistant"`. **O backend não guarda sessão** — o front deve mandar o histórico inteiro (ou pelo menos as últimas mensagens) a cada requisição. O backend corta automaticamente para as últimas `MAX_HISTORY_MESSAGES` (padrão: 20). |

**Resposta:** `Content-Type: text/event-stream`. Eventos, nesta ordem:

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

- `token` é emitido um ou mais vezes, com pedaços do texto da resposta, na ordem em que devem ser concatenados.
- `sources` é emitido **uma vez**, depois do último `token`, com os `id`s dos marcos usados como base para a resposta (pode ser `[]` se nenhum marco específico foi relevante). Use isso para mostrar links/cards de "saiba mais" para o usuário.
- `done` fecha o stream com sucesso.

**Em caso de erro no meio do stream** (ex.: provedor de IA fora do ar), o
stream ainda responde `200` (porque já começou), mas emite um evento
`error` no lugar de `sources`/`done` e encerra a conexão:

```
event: error
data: {"code": "llm_unavailable", "message": "O serviço de IA está indisponível no momento."}
```

Erros de validação (ex.: `message` vazio) acontecem **antes** do stream
começar e voltam como um `422` HTTP normal, no [formato padrão de erro](#formato-padrão-de-erro) — não como evento SSE.

---

## `POST /api/chat/sync`

Mesmo contrato de request do `/api/chat`, mas **sem streaming** — devolve a
resposta pronta de uma vez. Útil pro front testar a integração antes de
implementar a leitura de stream, ou como fallback mais simples.

**Request:** igual ao `POST /api/chat`.

**Resposta `200`:**

```json
{
  "reply": "Os fantasmas do Pac-Man usam máquinas de estado...",
  "marcos": ["pac-man-1980"]
}
```

**Resposta `503`** se o provedor de IA estiver indisponível — ver abaixo.

---

## Formato padrão de erro

Todas as rotas, em qualquer erro, respondem neste formato:

```json
{ "error": { "code": "not_found", "message": "Marco não encontrado." } }
```

| Código | HTTP status | Quando acontece |
|---|---|---|
| `validation_error` | 422 | Corpo da requisição inválido (ex.: `message` vazio ou maior que 2000 caracteres) |
| `not_found` | 404 | `id` de marco que não existe em `GET /api/timeline/{id}` |
| `llm_unavailable` | 503 | Erro do provedor de IA (timeout, rate limit, chave inválida, etc.) |
| `internal_error` | 500 | Qualquer erro inesperado não tratado |
