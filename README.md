# Histor.ia — Backend

Backend do **Histor.ia**, um projeto escolar: uma IA conversacional que conta
a história da inteligência artificial nos jogos, dos primeiros oponentes
controlados por computador (Nimrod, 1951) até NPCs modernos com IA
generativa.

O usuário conversa com a IA ("como funcionavam os fantasmas do Pac-Man?", "o
que mudou com o F.E.A.R.?") e ela responde como uma narradora/guia de museu,
usando uma linha do tempo curada como base de conhecimento — sem inventar
fatos.

Este repositório contém **só o backend**: uma API REST (com um endpoint de
chat via streaming SSE) feita para ser consumida por um frontend separado,
desenvolvido por outra pessoa do grupo.

## Stack

- Python 3.10+ · [FastAPI](https://fastapi.tiangolo.com/) · [Uvicorn](https://www.uvicorn.org/)
- Pydantic v2 + `pydantic-settings` para schemas e configuração
- [Ollama](https://ollama.com) local (modelo de linguagem rodando na própria máquina, sem custo e sem internet), isolado em `app/services/llm.py`
- Base de conhecimento em JSON (`data/timeline.json`) — sem banco de dados
- `pytest` + `httpx` para testes (o LLM é sempre mockado nos testes)

## Como rodar

Precisa do [Ollama](https://ollama.com/download) instalado e rodando
(`ollama serve`, ou já roda sozinho depois da instalação), com o modelo
baixado:

```bash
ollama pull qwen2.5:3b           # ou outro modelo — veja OLLAMA_MODEL no .env
```

Depois, na primeira vez ou sempre que quiser subir o servidor:

```bash
./run.sh
```

Esse script cria o `.venv` se não existir, instala as dependências, cria o
`.env` a partir do `.env.example` se não existir, avisa se o Ollama ou o
modelo configurado não estiverem prontos, e sobe o servidor com reload
automático. Não precisa ativar o venv manualmente nem lembrar do comando do
uvicorn — só rodar `./run.sh` de novo toda vez.

Se preferir os passos manuais:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # padrão já aponta pro Ollama local, não precisa editar
uvicorn app.main:app --reload --port 8000
```

Docs interativas (Swagger): http://localhost:8000/docs
Contrato completo da API: [`docs/API.md`](docs/API.md)

Se o Ollama não estiver rodando ou o modelo em `OLLAMA_MODEL` não estiver
baixado, todas as rotas de conteúdo (`/api/health`, `/api/eras`,
`/api/timeline*`) continuam funcionando normalmente — só as rotas de chat
(`/api/chat`, `/api/chat/sync`) respondem `503 llm_unavailable`, que é o
comportamento esperado.

### Testes

```bash
pytest -q
```

Os testes nunca chamam o Ollama de verdade — `app/services/llm.py`
é sempre substituído por um fake (veja `tests/conftest.py`).

## Estrutura

```
histor-ia-backend/
├── CHANGELOG.md
├── run.sh                  # sobe tudo com um comando: ./run.sh
├── docs/API.md             # contrato oficial com o frontend
├── data/timeline.json      # base de conhecimento (eras + marcos históricos)
├── app/
│   ├── main.py              # cria o app, CORS, inclui routers
│   ├── config.py            # Settings (lê .env)
│   ├── errors.py            # formato padrão de erro + exception handlers
│   ├── routers/              # health, timeline, chat
│   ├── schemas/               # modelos Pydantic de request/response
│   └── services/
│       ├── llm.py             # única camada que fala com o Ollama
│       ├── knowledge.py       # carrega e busca marcos no timeline.json
│       └── prompt.py          # monta o system prompt da persona
└── tests/
```

## Handoff para o frontend

Quem for consumir esta API só precisa de:

- URL base em dev: `http://localhost:8000/api`
- O contrato em [`docs/API.md`](docs/API.md) + o Swagger em `/docs`
- Saber que `/api/chat` é streaming via SSE — usar `fetch` + leitura manual
  do stream (o `EventSource` do navegador não serve porque não suporta
  `POST`) — e que `/api/chat/sync` existe como alternativa mais simples,
  sem streaming, pra testar a integração primeiro
- Saber que **o backend não guarda sessão**: o front é responsável por
  guardar o histórico da conversa e reenviá-lo em cada requisição

## Base de conhecimento

`data/timeline.json` tem duas listas: `eras` (períodos, pra montar
filtros/abas) e `marcos` (17 marcos históricos, de Nimrod/1951 a agentes
generativos/2023, cada um com resumo, descrição, técnica usada, tags e
fontes). Para adicionar ou revisar um marco, siga o schema documentado no
[`CLAUDE.md`](CLAUDE.md) e sempre preencha `fontes` — é um projeto escolar e
precisão histórica vale nota.

## Licença

Projeto escolar, sem licença específica definida.
