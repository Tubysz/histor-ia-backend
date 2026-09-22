#!/usr/bin/env bash
# Sobe o backend do Histor.ia com um único comando: ./run.sh
set -e

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "==> Criando ambiente virtual (.venv)..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "==> Instalando dependências..."
pip install -q -r requirements.txt

if [ ! -f .env ]; then
  echo "==> Criando .env a partir do .env.example..."
  cp .env.example .env
fi

if ! curl -s -o /dev/null http://localhost:11434/api/version; then
  echo ""
  echo "AVISO: não consegui falar com o Ollama em localhost:11434."
  echo "Instale em https://ollama.com/download e deixe rodando (ollama serve"
  echo "ou o app do Ollama) antes de usar o chat. As outras rotas funcionam"
  echo "normalmente mesmo sem o Ollama."
  echo ""
fi

MODEL=$(grep '^OLLAMA_MODEL=' .env | cut -d= -f2)
if [ -n "$MODEL" ] && ! ollama list 2>/dev/null | grep -q "^${MODEL}"; then
  echo "AVISO: modelo '$MODEL' (definido em OLLAMA_MODEL no .env) não está"
  echo "baixado. Rode: ollama pull $MODEL"
  echo ""
fi

echo "==> Subindo em http://localhost:8000 (docs em http://localhost:8000/docs)"
exec uvicorn app.main:app --reload --port 8000
