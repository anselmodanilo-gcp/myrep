#!/usr/bin/env python3
"""
🚀 Deploy & Configuração do Vertex AI Agent Platform / Agent Builder
Luminar Saúde - Copiloto Comercial & Recomendador de CPAP
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
from typing import Dict, Any, Optional

try:
    import google.auth
    from google.auth.transport.requests import Request
    import requests
except ImportError:
    print("Instalando dependências necessárias...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-auth", "requests", "pyyaml"])
    import google.auth
    from google.auth.transport.requests import Request
    import requests

DEFAULT_PROJECT_ID = "abiding-arch-505313-m3"
DEFAULT_LOCATION = "global"  # Discovery Engine default location
DEFAULT_GCP_REGION = "southamerica-east1"
DATA_STORE_ID = "luminar-saude-datastore"
DATA_STORE_NAME = "Luminar Saúde - Laudos e Catálogos Médicos"
ENGINE_ID = "luminar-saude-agent"
ENGINE_NAME = "Luminar Saúde - Copiloto de Vendas e CPAP"

SYSTEM_INSTRUCTION = """Você é o Copiloto Especialista em Terapias do Sono e Consultoria Comercial da Luminar Saúde.
Sua missão é auxiliar consultores de vendas e pacientes a compreender laudos de polissonografia, receitas médicas e encontrar a melhor solução de CPAP, BiPAP, máscaras e insumos respiratórios.

Diretrizes de Atuação:
1. Consulta Clínica: Utilize a ferramenta `consultar_paciente` para buscar IAH, saturação de O2, padrão respiratório (oral/nasal) e pressão titulada em cmH2O.
2. Recomendação Precisa: Utilize a ferramenta `recomendar_produtos` para cruzar os dados médicos com o catálogo da Luminar Saúde.
3. Quebra de Objeções: Explique com empatia e autoridade os benefícios da adaptação ao CPAP, alívio expiratório (EPR), baixo ruído e garantia de 30 dias de troca de máscara.
4. Comunicação: Utilize `gerar_pitch_vendas` para elaborar mensagens sob medida para WhatsApp ou e-mail.
5. Cadastro Rápido: Utilize `criar_novo_lead` caso receba novos dados de pacientes ou novas receitas.

Mantenha sempre uma postura empática, consultiva, técnica e ética no tratamento de dados de saúde."""

def get_auth_token():
    """Obtém o token OAuth2 via Application Default Credentials ou gcloud."""
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        return credentials.token, credentials.project_id or project
    except Exception as e:
        # Fallback via CLI gcloud
        try:
            token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
            project = subprocess.check_output(["gcloud", "config", "get-value", "project"], text=True).strip()
            return token, project
        except Exception:
            raise RuntimeError("Não foi possível obter credenciais GCP. Execute `gcloud auth application-default login` ou `gcloud auth login`.")

def get_cloud_run_url(project_id: str, region: str, service_name: str = "luminar-saude-demo") -> Optional[str]:
    """Descobre a URL pública do Cloud Run."""
    try:
        url = subprocess.check_output(
            ["gcloud", "run", "services", "describe", service_name, "--platform", "managed", "--region", region, "--project", project_id, "--format", "value(status.url)"],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        return url if url else None
    except Exception:
        return None

def update_openapi_spec(service_url: str, output_path: str = "openapi_mcp_deployed.yaml") -> str:
    """Atualiza a especificação OpenAPI com a URL real do Cloud Run."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_spec = os.path.join(base_dir, "openapi_mcp.yaml")
    
    with open(source_spec, "r", encoding="utf-8") as f:
        spec_data = yaml.safe_load(f)
    
    spec_data["servers"] = [
        {"url": service_url, "description": "Cloud Run Live Endpoint"},
        {"url": "http://localhost:8000", "description": "Local Testing"}
    ]
    
    dest_file = os.path.join(base_dir, output_path)
    with open(dest_file, "w", encoding="utf-8") as f:
        yaml.dump(spec_data, f, sort_keys=False, allow_unicode=True)
        
    # Também gera JSON
    json_path = os.path.join(base_dir, "openapi_mcp_deployed.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(spec_data, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Especificação OpenAPI atualizada com URL do Cloud Run ({service_url}):")
    print(f"   - YAML: {dest_file}")
    print(f"   - JSON: {json_path}")
    return dest_file

def create_discovery_engine_datastore(token: str, project_id: str, location: str, bucket_name: str):
    """Cria o Data Store no Vertex AI Agent Builder / Discovery Engine."""
    print(f"\n[1/3] Configurando Data Store no Vertex AI Agent Builder ({DATA_STORE_ID})...")
    url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/{location}/collections/default_collection/dataStores"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "displayName": DATA_STORE_NAME,
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_SEARCH", "SOLUTION_TYPE_CHAT"],
        "contentConfig": "CONTENT_REQUIRED",
        "documentProcessingConfig": {
            "defaultParsingConfig": {
                "digitalParsingConfig": {}
            }
        }
    }
    
    params = {"dataStoreId": DATA_STORE_ID}
    response = requests.post(url, headers=headers, params=params, json=body)
    
    if response.status_code in [200, 201]:
        print(f"✅ Data Store `{DATA_STORE_ID}` criado com sucesso!")
    elif response.status_code == 409 or "ALREADY_EXISTS" in response.text:
        print(f"✅ Data Store `{DATA_STORE_ID}` já existente no projeto.")
    else:
        print(f"⚠️ Resposta da criação do Data Store ({response.status_code}): {response.text}")
        
    # Importar documentos do bucket Cloud Storage
    print(f"\n[2/3] Importando laudos e manuais de gs://{bucket_name}/...")
    import_url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{DATA_STORE_ID}/branches/default_branch/documents:import"
    import_body = {
        "gcsSource": {
            "inputUris": [
                f"gs://{bucket_name}/storage/laudos_polissonografia/*",
                f"gs://{bucket_name}/storage/receitas_medicas/*",
                f"gs://{bucket_name}/storage/catalogos_manuais/*"
            ]
        },
        "reconciliationMode": "INCREMENTAL"
    }
    
    imp_resp = requests.post(import_url, headers=headers, json=import_body)
    if imp_resp.status_code in [200, 201]:
        print(f"✅ Job de importação de laudos iniciado com sucesso!")
    else:
        print(f"ℹ️ Status da importação ({imp_resp.status_code}): {imp_resp.text}")

def create_discovery_engine_app(token: str, project_id: str, location: str):
    """Cria ou configura a aplicação/Engine de Agente no Agent Builder."""
    print(f"\n[3/3] Configurando Agent App no Agent Builder ({ENGINE_ID})...")
    url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/{location}/collections/default_collection/engines"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "displayName": ENGINE_NAME,
        "solutionType": "SOLUTION_TYPE_CHAT",
        "dataStoreIds": [DATA_STORE_ID],
        "chatEngineConfig": {
            "agentCreationConfig": {
                "business": "Luminar Saúde - Terapias Respiratórias e Medicina do Sono",
                "defaultLanguageCode": "pt-BR",
                "timeZone": "America/Sao_Paulo"
            }
        }
    }
    
    params = {"engineId": ENGINE_ID}
    response = requests.post(url, headers=headers, params=params, json=body)
    
    if response.status_code in [200, 201]:
        print(f"✅ Agent Engine `{ENGINE_ID}` criado com sucesso no Agent Builder!")
    elif response.status_code == 409 or "ALREADY_EXISTS" in response.text:
        print(f"✅ Agent Engine `{ENGINE_ID}` já existe no projeto.")
    else:
        print(f"ℹ️ Status do Agent Engine ({response.status_code}): {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Deploy & Configuração do Vertex AI Agent Builder")
    parser.add_argument("--project", default=None, help="GCP Project ID")
    parser.add_argument("--location", default=DEFAULT_LOCATION, help="Location do Agent Builder (default: global)")
    parser.add_argument("--region", default=DEFAULT_GCP_REGION, help="GCP Region do Cloud Run (default: southamerica-east1)")
    parser.add_argument("--service-url", default=None, help="URL pública do Cloud Run")
    args = parser.parse_args()
    
    print("=========================================================================")
    print("  🤖 DEPLOY & INTEGRAÇÃO COM VERTEX AI AGENT BUILDER (AGENT PLATFORM)")
    print("=========================================================================")
    
    # 1. Obter Autenticação
    try:
        token, detected_project = get_auth_token()
        project_id = args.project or detected_project or DEFAULT_PROJECT_ID
    except Exception as e:
        print(f"❌ Erro de Autenticação: {e}")
        print("💡 Execute: `gcloud auth application-default login`")
        return
        
    bucket_name = f"{project_id}-luminar-saude"
    
    print(f"Projeto GCP:     {project_id}")
    print(f"Location Agent:  {args.location}")
    print(f"Região CloudRun: {args.region}")
    print(f"Bucket GCS:      gs://{bucket_name}")
    
    # 2. Descobrir URL do Cloud Run
    service_url = args.service_url or get_cloud_run_url(project_id, args.region)
    if not service_url:
        service_url = f"https://luminar-saude-demo-431262818879.{args.region}.run.app"
        print(f"ℹ️ URL do Cloud Run assumida: {service_url}")
    else:
        print(f"✅ URL do Cloud Run detectada: {service_url}")
        
    # 3. Atualizar especificação OpenAPI
    update_openapi_spec(service_url)
    
    # 4. Criar Data Store no Discovery Engine
    try:
        create_discovery_engine_datastore(token, project_id, args.location, bucket_name)
    except Exception as e:
        print(f"⚠️ Erro ao criar Data Store: {e}")
        
    # 5. Criar App / Engine no Discovery Engine
    try:
        create_discovery_engine_app(token, project_id, args.location)
    except Exception as e:
        print(f"⚠️ Erro ao criar Agent Engine: {e}")
        
    # 6. Exibir Resumo e Guia de Conexão das Tools
    print("\n=========================================================================")
    print("  🎉 CONFIGURAÇÃO DO AGENT PLATFORM CONCLUÍDA!")
    print("=========================================================================")
    print(f"\n🌐 Console do Vertex AI Agent Builder:")
    print(f"   https://console.cloud.google.com/gen-app-builder/engines?project={project_id}")
    print(f"\n📂 Console do Data Store (Laudos e Manuais):")
    print(f"   https://console.cloud.google.com/gen-app-builder/data-stores?project={project_id}")
    print(f"\n🛠️ OpenAPI Spec para Registro de Tools no Agent Platform:")
    print(f"   YAML: {os.path.abspath('openapi_mcp_deployed.yaml')}")
    print(f"   URL:  {service_url}/openapi.json")
    print(f"   MCP:  {service_url}/mcp/manifest.json")
    print("=========================================================================\n")

if __name__ == "__main__":
    main()
