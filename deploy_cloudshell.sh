#!/bin/bash
set -e

# ==============================================================================
# SCRIPT DE DEPLOY COMPLETO - LUMINAR SAÚDE NO GOOGLE CLOUD (CLOUD SHELL)
# ==============================================================================
# Usuário: admin@anselmodanilo.altostrat.com
# Projeto: abiding-arch-505313-m3
# Número do Projeto: 431262818879
# ==============================================================================

PROJECT_ID="abiding-arch-505313-m3"
PROJECT_NUMBER="431262818879"
REGION="southamerica-east1"
DATASET_ID="luminar_saude"
BUCKET_NAME="${PROJECT_ID}-luminar-saude"
SERVICE_NAME="luminar-saude-demo"

echo "========================================================================="
echo "  🚀 INICIANDO DEPLOY COMPLETO DA DEMO LUMINAR SAÚDE"
echo "  Projeto GCP: ${PROJECT_ID} (${PROJECT_NUMBER})"
echo "  Região:      ${REGION}"
echo "========================================================================="

# 1. Configurar Projeto Ativo
echo -e "\n[1/6] Configurando o projeto ativo no gcloud..."
gcloud config set project ${PROJECT_ID}

# 2. Habilitar APIs Necessárias
echo -e "\n[2/6] Habilitando APIs do Google Cloud (BigQuery, Storage, Cloud Run, Vertex AI, Agent Platform)..."
gcloud services enable \
    bigquery.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    discoveryengine.googleapis.com

# 3. Gerar Assets Locais caso não existam
echo -e "\n[3/6] Gerando laudos médicos em PDF, CSVs e dados de CRM..."
python3 generate_assets.py
python3 generate_extra_docs.py

# 4. Criar Dataset e Tabelas no BigQuery
echo -e "\n[4/6] Provisionando Dataset e Tabelas no BigQuery..."
bq --location=US mk -d --description "Luminar Saúde: CRM, Diagnósticos de Sono e Catálogo Respiratório" ${PROJECT_ID}:${DATASET_ID} 2>/dev/null || echo "Dataset '${DATASET_ID}' já existente."

echo " -> Carregando leads_pacientes..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.leads_pacientes bigquery/data/leads_pacientes.csv

echo " -> Carregando catalogo_produtos..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.catalogo_produtos bigquery/data/catalogo_produtos.csv

echo " -> Carregando recomendacoes_vendedor..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.recomendacoes_vendedor bigquery/data/recomendacoes_vendedor.csv

echo " -> Carregando historico_compras_trocas..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.historico_compras_trocas bigquery/data/historico_compras_trocas.csv

# 5. Criar Bucket e Upload no Cloud Storage
echo -e "\n[5/6] Criando Bucket Cloud Storage e enviando Laudos e Prescrições..."
gcloud storage buckets create gs://${BUCKET_NAME} --location=US 2>/dev/null || echo "Bucket 'gs://${BUCKET_NAME}' já existente."
gcloud storage cp -r storage/* gs://${BUCKET_NAME}/

# 6. Build e Deploy da Aplicação no Cloud Run (Web UI & MCP Server)
echo -e "\n[6/6] Construindo e fazendo deploy da aplicação no Cloud Run..."
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

echo -e "\n========================================================================="
echo "  🎉 DEPLOY FINALIZADO COM SUCESSO!"
echo "========================================================================="
echo -e "\n🌐 Portal Web da Demonstração (Streamlit & Cockpit do Vendedor):"
echo "   ${SERVICE_URL}"
echo -e "\n🤖 Endpoint MCP Server & Ferramentas do Agent:"
echo "   ${SERVICE_URL}/mcp/manifest.json"
echo "   ${SERVICE_URL}/docs (Swagger OpenAPI)"
echo -e "\n📊 Console do BigQuery:"
echo "   https://console.cloud.google.com/bigquery?project=${PROJECT_ID}"
echo -e "\n🗄️ Bucket do Cloud Storage:"
echo "   https://console.cloud.google.com/storage/browser/${BUCKET_NAME}?project=${PROJECT_ID}"
echo -e "\n🤖 Vertex AI Agent Builder / Agent Platform:"
echo "   https://console.cloud.google.com/gen-app-builder/engines?project=${PROJECT_ID}"
echo "========================================================================="
