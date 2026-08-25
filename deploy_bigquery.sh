#!/bin/bash
set -e

PROJECT_ID="abiding-arch-505313-m3"
DATASET_ID="luminar_saude"
LOCATION="US"

echo "================================================================="
echo "  LUMINAR SAÚDE - DEPLOY BIGQUERY"
echo "  Projeto: ${PROJECT_ID}"
echo "  Dataset: ${DATASET_ID}"
echo "  Região:  ${LOCATION}"
echo "================================================================="

# 1. Definir projeto ativo
echo -e "\n[1/3] Configurando projeto no gcloud..."
gcloud config set project ${PROJECT_ID}

# 2. Criar Dataset caso não exista
echo -e "\n[2/3] Criando/Verificando Dataset '${DATASET_ID}'..."
bq --location=${LOCATION} mk -d --description "Luminar Saúde: CRM, Diagnósticos de Sono e Catálogo Respiratório" ${PROJECT_ID}:${DATASET_ID} 2>/dev/null || echo "Dataset '${DATASET_ID}' já existe ou verificado."

# 3. Carregar Tabelas e Dados
echo -e "\n[3/3] Criando tabelas e inserindo dados dos CSVs..."

echo " -> Carregando tabela: leads_pacientes..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.leads_pacientes bigquery/data/leads_pacientes.csv

echo " -> Carregando tabela: catalogo_produtos..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.catalogo_produtos bigquery/data/catalogo_produtos.csv

echo " -> Carregando tabela: recomendacoes_vendedor..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.recomendacoes_vendedor bigquery/data/recomendacoes_vendedor.csv

echo " -> Carregando tabela: historico_compras_trocas..."
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace ${PROJECT_ID}:${DATASET_ID}.historico_compras_trocas bigquery/data/historico_compras_trocas.csv

echo -e "\n================================================================="
echo "  ✅ TODAS AS TABELAS DO BIGQUERY FORAM DEPLOYADAS COM SUCESSO!"
echo "================================================================="
echo "Tabelas criadas no BigQuery:"
bq ls ${PROJECT_ID}:${DATASET_ID}
