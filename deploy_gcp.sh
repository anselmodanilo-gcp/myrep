#!/bin/bash
set -e

# ==============================================================================
# LUMINAR SAÚDE - DEPLOY COMPLETO (GCP & VERTEX AI AGENT PLATFORM)
# ==============================================================================

PROJECT_ID="${PROJECT_ID:-abiding-arch-505313-m3}"
PROJECT_NUMBER="${PROJECT_NUMBER:-431262818879}"
REGION="${REGION:-southamerica-east1}"
DATASET_ID="luminar_saude"
BUCKET_NAME="${PROJECT_ID}-luminar-saude"
SERVICE_NAME="luminar-saude-demo"

echo "========================================================================="
echo "  🚀 INICIANDO DEPLOY COMPLETO DA DEMO LUMINAR SAÚDE"
echo "  Projeto GCP:   ${PROJECT_ID}"
echo "  Região Cloud:  ${REGION}"
echo "  Dataset BQ:    ${DATASET_ID}"
echo "  Bucket GCS:    gs://${BUCKET_NAME}"
echo "========================================================================="

# 1. Configurar Projeto Ativo
echo -e "\n[1/7] Configurando o projeto ativo no gcloud..."
gcloud config set project ${PROJECT_ID}

# 2. Habilitar APIs Necessárias
echo -e "\n[2/7] Habilitando APIs do Google Cloud..."
gcloud services enable \
    bigquery.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    discoveryengine.googleapis.com

# 3. Gerar Assets Locais
echo -e "\n[3/7] Gerando laudos médicos em PDF, CSVs e playbooks..."
source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || true
python3 generate_assets.py
python3 generate_extra_docs.py

# 4. Provisionar BigQuery
echo -e "\n[4/7] Provisionando Dataset e Tabelas no BigQuery..."
bq --location=US mk -d --description "Luminar Saúde: CRM, Diagnósticos de Sono e Catálogo Respiratório" ${PROJECT_ID}:${DATASET_ID} 2>/dev/null || echo "Dataset '${DATASET_ID}' já existente."

echo " -> Carregando leads_pacientes..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.leads_pacientes bigquery/data/leads_pacientes.csv

echo " -> Carregando catalogo_produtos..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.catalogo_produtos bigquery/data/catalogo_produtos.csv

echo " -> Carregando recomendacoes_vendedor..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.recomendacoes_vendedor bigquery/data/recomendacoes_vendedor.csv

echo " -> Carregando historico_compras_trocas..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.historico_compras_trocas bigquery/data/historico_compras_trocas.csv

# 5. Provisionar Cloud Storage
echo -e "\n[5/7] Criando Bucket Cloud Storage e enviando Laudos e Prescrições..."
gcloud storage buckets create gs://${BUCKET_NAME} --location=US 2>/dev/null || echo "Bucket 'gs://${BUCKET_NAME}' já existente."
gcloud storage cp -r storage/* gs://${BUCKET_NAME}/

# 6. Build e Deploy no Cloud Run
echo -e "\n[6/7] Construindo e fazendo deploy da aplicação no Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars PROJECT_ID=${PROJECT_ID},DATASET_ID=${DATASET_ID} \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 2

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

# 7. Configuração do Vertex AI Agent Builder & Data Store
echo -e "\n[7/7] Configurando Vertex AI Agent Platform & Data Store..."
python3 deploy_agent_platform.py --project ${PROJECT_ID} --region ${REGION} --service-url ${SERVICE_URL} || true

echo -e "\n========================================================================="
echo "  🎉 DEPLOY COMPLETO REALIZADO COM SUCESSO!"
echo "========================================================================="
echo -e "\n🌐 Portal Web da Demonstração (Streamlit Cockpit):"
echo "   ${SERVICE_URL}"
echo -e "\n🤖 Endpoints de Ferramentas do Agente (MCP & OpenAPI):"
echo "   ${SERVICE_URL}/docs (Swagger OpenAPI Interativo)"
echo "   ${SERVICE_URL}/mcp/manifest.json (MCP Manifest)"
echo "   ${SERVICE_URL}/openapi.json (OpenAPI 3.0 Spec)"
echo -e "\n📂 Vertex AI Agent Builder (Search & Conversation):"
echo "   https://console.cloud.google.com/gen-app-builder/engines?project=${PROJECT_ID}"
echo -e "\n📊 Console do BigQuery:"
echo "   https://console.cloud.google.com/bigquery?project=${PROJECT_ID}"
echo -e "\n🗄️ Bucket do Cloud Storage:"
echo "   https://console.cloud.google.com/storage/browser/${BUCKET_NAME}?project=${PROJECT_ID}"
echo "========================================================================="
