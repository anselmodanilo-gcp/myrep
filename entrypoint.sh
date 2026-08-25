#!/bin/bash
set -e

echo "Starting Luminar Saude Demo Services..."

# Inicia o MCP Server em background na porta 8000
source /app/venv/bin/activate 2>/dev/null || true
uvicorn mcp_server:app --host 0.0.0.0 --port 8000 &

# Inicia o Streamlit na porta padrão do Cloud Run ($PORT ou 8080)
PORT="${PORT:-8080}"
echo "Starting Streamlit UI on port ${PORT}..."
exec streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
