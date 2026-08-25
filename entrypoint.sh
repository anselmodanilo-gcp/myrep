#!/bin/bash
set -e

PORT="${PORT:-8080}"
echo "======================================================"
echo "🚀 Iniciando Serviços Luminar Saúde no Cloud Run..."
echo "======================================================"

# 1. Inicia o MCP Server (FastAPI) na porta 8000
echo "[1/3] Iniciando FastAPI MCP Server na porta 8000..."
uvicorn mcp_server:app --host 127.0.0.1 --port 8000 &

# 2. Inicia o Streamlit na porta 8501
echo "[2/3] Iniciando Streamlit Cockpit na porta 8501..."
streamlit run app.py \
    --server.port=8501 \
    --server.address=127.0.0.1 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false &

# 3. Configura a porta no NGINX e inicia como processo principal
echo "[3/3] Iniciando NGINX Gateway na porta pública ${PORT}..."
sed -i "s/listen [0-9]\+;/listen ${PORT};/g" /etc/nginx/nginx.conf 2>/dev/null || true

# Garante que o NGINX rode em primeiro plano
exec nginx -g "daemon off;"
