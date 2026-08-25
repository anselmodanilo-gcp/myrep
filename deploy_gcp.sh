#!/bin/bash
set -e

PROJECT_ID="abiding-arch-505313-m3"
DATASET_ID="luminar_saude"
BUCKET_NAME="${PROJECT_ID}-luminar-saude"
LOCATION="US"

echo "================================================================="
echo "  LUMINAR SAÚDE - DEPLOY DE ASSETS GOOGLE CLOUD (ARGOLIS)"
echo "  Projeto: ${PROJECT_ID}"
echo "  Dataset BigQuery: ${DATASET_ID}"
echo "  Bucket GCS: gs://${BUCKET_NAME}"
echo "================================================================="

# 1. Configurar projeto padrão no gcloud
echo -e "\n[1/4] Configurando projeto no gcloud..."
gcloud config set project ${PROJECT_ID}

# 2. Criar Dataset no BigQuery
echo -e "\n[2/4] Criando Dataset BigQuery '${DATASET_ID}'..."
bq --location=${LOCATION} mk -d --description "Luminar Saúde: CRM, Diagnósticos de Sono e Catálogo Respiratório" ${PROJECT_ID}:${DATASET_ID} 2>/dev/null || echo "Dataset já existe."

# Carregar tabelas
echo "Carregando tabela leads_pacientes..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.leads_pacientes bigquery/data/leads_pacientes.csv

echo "Carregando tabela catalogo_produtos..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.catalogo_produtos bigquery/data/catalogo_produtos.csv

echo "Carregando tabela recomendacoes_vendedor..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.recomendacoes_vendedor bigquery/data/recomendacoes_vendedor.csv

echo "Carregando tabela historico_compras_trocas..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.historico_compras_trocas bigquery/data/historico_compras_trocas.csv

# 3. Criar Bucket e Fazer Upload no Cloud Storage
echo -e "\n[3/4] Criando Bucket Cloud Storage 'gs://${BUCKET_NAME}'..."
gcloud storage buckets create gs://${BUCKET_NAME} --location=${LOCATION} 2>/dev/null || echo "Bucket já existe."

echo "Fazendo upload dos laudos de polissonografia e catálogos..."
gcloud storage cp -r storage/* gs://${BUCKET_NAME}/

# 4. Finalização
echo -e "\n[4/4] Executando script de validação Python..."
source venv/bin/activate 2>/dev/null || true
python deploy_gcp.py

echo -e "\n================================================================="
echo "  🎉 DEPLOY CONCLUÍDO COM SUCESSO NO PROJETO ${PROJECT_ID}!"
echo "================================================================="
