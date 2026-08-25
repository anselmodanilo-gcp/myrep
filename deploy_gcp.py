#!/usr/bin/env python3
"""
Deploy Luminar Saúde Demo to Google Cloud Platform
Project: abiding-arch-505313-m3
Dataset: luminar_saude
Bucket: abiding-arch-505313-m3-luminar-saude
"""

import os
import sys
from google.cloud import bigquery
from google.cloud import storage

PROJECT_ID = "abiding-arch-505313-m3"
DATASET_ID = "luminar_saude"
BUCKET_NAME = f"{PROJECT_ID}-luminar-saude"
LOCATION = "US"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "bigquery", "data")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

def deploy_bigquery():
    print(f"\n==========================================")
    print(f"🚀 1. DEPLOYING BIGQUERY ({PROJECT_ID}.{DATASET_ID})")
    print(f"==========================================")
    try:
        client = bigquery.Client(project=PROJECT_ID)
        dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = LOCATION
        dataset.description = "Luminar Saúde: CRM, Diagnósticos de Sono e Catálogo Respiratório"
        
        try:
            client.create_dataset(dataset, exists_ok=True)
            print(f"✅ Dataset `{PROJECT_ID}.{DATASET_ID}` criado/verificado com sucesso!")
        except Exception as e:
            print(f"⚠️ Aviso ao criar dataset: {e}")

        # Load tables
        tables = [
            ("leads_pacientes", os.path.join(DATA_DIR, "leads_pacientes.csv")),
            ("catalogo_produtos", os.path.join(DATA_DIR, "catalogo_produtos.csv")),
            ("recomendacoes_vendedor", os.path.join(DATA_DIR, "recomendacoes_vendedor.csv")),
            ("historico_compras_trocas", os.path.join(DATA_DIR, "historico_compras_trocas.csv"))
        ]

        for table_name, csv_file in tables:
            if not os.path.exists(csv_file):
                print(f"❌ Arquivo não encontrado: {csv_file}")
                continue
            
            table_ref = dataset_ref.table(table_name)
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
            )
            
            with open(csv_file, "rb") as f_in:
                job = client.load_table_from_file(f_in, table_ref, job_config=job_config)
                job.result()
            
            table = client.get_table(table_ref)
            print(f"✅ Tabela `{table_name}` carregada com {table.num_rows} registros!")

    except Exception as e:
        print(f"❌ Erro no deploy do BigQuery: {e}")
        print("💡 Dica: Certifique-se de estar autenticado com `gcloud auth application-default login` ou ter credenciais do projeto.")

def deploy_storage():
    print(f"\n==========================================")
    print(f"🚀 2. DEPLOYING CLOUD STORAGE (gs://{BUCKET_NAME})")
    print(f"==========================================")
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        
        try:
            if not bucket.exists():
                bucket = storage_client.create_bucket(BUCKET_NAME, location=LOCATION)
                print(f"✅ Bucket `gs://{BUCKET_NAME}` criado com sucesso!")
            else:
                print(f"✅ Bucket `gs://{BUCKET_NAME}` já existe.")
        except Exception as e:
            print(f"⚠️ Aviso ao verificar bucket: {e}")

        # Upload files
        for root, dirs, files in os.walk(STORAGE_DIR):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, STORAGE_DIR)
                blob = bucket.blob(rel_path)
                blob.upload_from_filename(local_path)
                print(f"✅ Upload concluído: gs://{BUCKET_NAME}/{rel_path}")

    except Exception as e:
        print(f"❌ Erro no deploy do Cloud Storage: {e}")
        print("💡 Dica: Verifique as permissões de Storage Admin no projeto.")

if __name__ == "__main__":
    print(f"Iniciando deploy dos assets Luminar Saúde no projeto: {PROJECT_ID}...")
    deploy_bigquery()
    deploy_storage()
    print("\n🏁 Processo de Deploy Finalizado!")
