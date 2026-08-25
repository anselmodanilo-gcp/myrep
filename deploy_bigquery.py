#!/usr/bin/env python3
"""
Deploy BigQuery Tables and Seed Data for Luminar Saúde
Project: abiding-arch-505313-m3
Dataset: luminar_saude
"""

import os
import sys
from google.cloud import bigquery

PROJECT_ID = "abiding-arch-505313-m3"
DATASET_ID = "luminar_saude"
LOCATION = "US"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "bigquery", "data")

def main():
    print("=================================================================")
    print(f"🚀 INICIANDO DEPLOY NO BIGQUERY")
    print(f"   Projeto: {PROJECT_ID}")
    print(f"   Dataset: {DATASET_ID}")
    print("=================================================================")

    try:
        client = bigquery.Client(project=PROJECT_ID)
    except Exception as e:
        print(f"\n❌ Erro ao inicializar cliente BigQuery: {e}")
        print("\n👉 Certifique-se de estar autenticado executando no terminal:")
        print("   gcloud auth application-default login")
        print("   gcloud config set project abiding-arch-505313-m3")
        sys.exit(1)

    # 1. Criar Dataset
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = LOCATION
    dataset.description = "Luminar Saúde: CRM, Diagnósticos de Sono e Catálogo Respiratório"

    try:
        client.create_dataset(dataset, exists_ok=True)
        print(f"✅ Dataset `{PROJECT_ID}.{DATASET_ID}` criado/verificado com sucesso!")
    except Exception as e:
        print(f"⚠️ Nota ao verificar dataset: {e}")

    # 2. Carregar Tabelas
    tables = [
        ("leads_pacientes", os.path.join(DATA_DIR, "leads_pacientes.csv")),
        ("catalogo_produtos", os.path.join(DATA_DIR, "catalogo_produtos.csv")),
        ("recomendacoes_vendedor", os.path.join(DATA_DIR, "recomendacoes_vendedor.csv")),
        ("historico_compras_trocas", os.path.join(DATA_DIR, "historico_compras_trocas.csv"))
    ]

    for table_name, csv_path in tables:
        if not os.path.exists(csv_path):
            print(f"❌ Arquivo não encontrado: {csv_path}")
            continue

        table_ref = dataset_ref.table(table_name)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )

        print(f"⏳ Carregando `{table_name}` a partir de `{os.path.basename(csv_path)}`...")
        with open(csv_path, "rb") as f_in:
            job = client.load_table_from_file(f_in, table_ref, job_config=job_config)
            job.result()  # Aguarda a conclusão

        loaded_table = client.get_table(table_ref)
        print(f"   ✅ Tabela `{table_name}` criada com {loaded_table.num_rows} linhas e {len(loaded_table.schema)} colunas.")

    print("\n=================================================================")
    print(f"🎉 TODAS AS TABELAS E DADOS FORAM CARREGADOS COM SUCESSO NO BIGQUERY!")
    print(f"   Acesse no console: https://console.cloud.google.com/bigquery?project={PROJECT_ID}")
    print("=================================================================")

if __name__ == "__main__":
    main()
