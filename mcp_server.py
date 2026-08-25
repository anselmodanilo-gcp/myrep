#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server & Tool API for Luminar Saúde
Exposes specialized tools for Agent Platform / Vertex AI Agent Builder / Gemini.
"""

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import pandas as pd
import json

app = FastAPI(
    title="Luminar Saúde MCP Tool Server",
    description="MCP Server providing clinical diagnosis, CPAP recommendation, and sales copilot tools for Vertex AI Agent Platform.",
    version="1.0.0"
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "bigquery", "data")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

def get_leads_df():
    path = os.path.join(DATA_DIR, "leads_pacientes.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def get_catalogo_df():
    path = os.path.join(DATA_DIR, "catalogo_produtos.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def get_rec_df():
    path = os.path.join(DATA_DIR, "recomendacoes_vendedor.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

# -------------------------------------------------------------
# Tool 1: Consultar Paciente & Laudo Clínico
# -------------------------------------------------------------
@app.get("/tools/consultar_paciente", summary="Consultar ficha clínica e laudo polissonográfico do paciente")
def consultar_paciente(lead_id: str):
    """
    Busca o histórico clínico, diagnóstico CID, índice IAH, saturação SpO2 mínima,
    pressão titulada em laboratório e médico prescritor a partir do ID do lead.
    """
    df = get_leads_df()
    match = df[df['lead_id'].str.upper() == lead_id.upper()]
    if match.empty:
        # Tenta buscar por nome
        match = df[df['nome_paciente'].str.contains(lead_id, case=False, na=False)]
    
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Paciente/Lead '{lead_id}' não encontrado.")
    
    row = match.iloc[0].to_dict()
    return {
        "status": "success",
        "lead_id": row.get("lead_id"),
        "nome_paciente": row.get("nome_paciente"),
        "idade": row.get("idade"),
        "diagnostico": row.get("diagnostico_cid"),
        "iah": row.get("iah"),
        "gravidade_apneia": "Grave" if row.get("iah", 0) >= 30 else ("Moderada" if row.get("iah", 0) >= 15 else "Leve"),
        "spo2_minima": row.get("spo2_minima"),
        "pressao_titulada_cmh2o": row.get("pressao_titulada_cmh2o"),
        "respiracao_predominante": row.get("respiracao_predominante"),
        "medico_prescritor": row.get("medico_prescritor"),
        "crm_medico": row.get("crm_medico"),
        "convenio": row.get("convenio"),
        "comorbidades": row.get("comorbidades"),
        "sensibilidade_pressao": row.get("sensibilidade_pressao"),
        "score_prioridade": row.get("score_prioridade")
    }

# -------------------------------------------------------------
# Tool 2: Recomendar Equipamento e Máscara
# -------------------------------------------------------------
@app.get("/tools/recomendar_produtos", summary="Recomenda pacote de CPAP, máscara e insumos com IA")
def recomendar_produtos(lead_id: str):
    """
    Cruza as métricas clínicas do paciente (IAH, padrão oral/nasal, pressão)
    com o catálogo comercial da Luminar Saúde, retornando o equipamento principal,
    modelo de máscara ideal, insumos recomendados (cross-sell) e condições de parcelamento.
    """
    df_rec = get_rec_df()
    match = df_rec[df_rec['lead_id'].str.upper() == lead_id.upper()]
    if match.empty:
        # Busca dinâmica caso não esteja na tabela pré-calculada
        df_leads = get_leads_df()
        lead = df_leads[df_leads['lead_id'].str.upper() == lead_id.upper()]
        if lead.empty:
            raise HTTPException(status_code=404, detail="Lead não encontrado.")
        l = lead.iloc[0]
        
        # Algoritmo de matching dinâmico
        is_oral = "oral" in str(l.get("respiracao_predominante", "")).lower()
        pressao = float(l.get("pressao_titulada_cmh2o", 10.0))
        
        if pressao > 14.0:
            equip = "ResMed AirCurve 10 VAuto (BiPAP)"
            sku_eq = "BIPAP-RES-AC10"
            preco = 9800.00
        else:
            equip = "ResMed AirSense 11 AutoSet"
            sku_eq = "CPAP-RES-AS11"
            preco = 5890.00
            
        if is_oral or pressao >= 12.0:
            mask = "AirFit F20 Full Face (Facial)"
            sku_mk = "MSK-RES-F20"
            preco_mk = 890.00
        else:
            mask = "AirFit N20 Nasal ou P10 Almofadas"
            sku_mk = "MSK-RES-N20"
            preco_mk = 690.00
            
        total = preco + preco_mk + 390.00 + 150.00
        return {
            "status": "success",
            "lead_id": lead_id,
            "paciente": l.get("nome_paciente"),
            "equipamento_recomendado": equip,
            "sku_equipamento": sku_eq,
            "mascara_recomendada": mask,
            "sku_mascara": sku_mk,
            "insumos_cross_sell": "Tubo Aquecido ClimateLineAir + Kit Filtros Hipoalergênicos + Lenços CPAP Wipes",
            "valor_total_brl": total,
            "condicao_comercial": f"12x de R$ {total/12:.2f} sem juros ou 8% desc. à vista no PIX",
            "racional_clinico": f"Paciente com pressão de {pressao} cmH2O e padrão respiratório {l.get('respiracao_predominante')}. Indicação direta para evitar fuga aérea e ressecamento."
        }
        
    r = match.iloc[0].to_dict()
    return {
        "status": "success",
        "lead_id": r.get("lead_id"),
        "paciente": r.get("nome_paciente"),
        "equipamento_recomendado": r.get("equipamento_principal_nome"),
        "sku_equipamento": r.get("equipamento_principal_sku"),
        "mascara_recomendada": r.get("mascara_recomendada_nome"),
        "sku_mascara": r.get("mascara_recomendada_sku"),
        "insumos_cross_sell": r.get("insumos_cross_sell"),
        "valor_total_brl": r.get("valor_total_pacote_brl"),
        "condicao_comercial": r.get("condicao_comercial_sugerida"),
        "argumentacao_vendas": r.get("argumentacao_venda_ia"),
        "quebra_objecoes": r.get("quebra_objecoes"),
        "probabilidade_conversao": r.get("probabilidade_conversao")
    }

# -------------------------------------------------------------
# Tool 3: Gerar Pitch de Vendas & Copy Omnichannel
# -------------------------------------------------------------
@app.get("/tools/gerar_pitch_vendas", summary="Gera roteiro de WhatsApp e e-mail de proposta para o cliente")
def gerar_pitch_vendas(lead_id: str, canal: str = "whatsapp"):
    """
    Gera texto persuasivo e empático baseado no diagnóstico médico para envio via WhatsApp ou Gmail.
    """
    rec = recomendar_produtos(lead_id)
    leads = get_leads_df()
    lead = leads[leads['lead_id'].str.upper() == lead_id.upper()].iloc[0]
    
    nome = lead.get("nome_paciente", "Cliente")
    medico = lead.get("medico_prescritor", "Médico Especialista")
    
    if canal.lower() == "whatsapp":
        msg = (
            f"Olá, {nome}! Tudo bem? Aqui é o especialista em sono da Luminar Saúde.\n\n"
            f"Recebemos seu laudo do {medico} e preparamos seu kit com o moderno {rec['equipamento_recomendado']} "
            f"e a máscara {rec['mascara_recomendada']}.\n\n"
            f"✨ Destaques do seu pacote:\n"
            f"- Silêncio absoluto durante a noite (25 dBA)\n"
            f"- Alívio automático de pressão para respirar naturalmente\n"
            f"- Programa de Adaptação 30 Dias: se não se adaptar à máscara, trocamos gratuitamente!\n\n"
            f"💳 Valor Especial: {rec['condicao_comercial']}\n\n"
            f"Podemos agendar a entrega assistida na sua residência hoje ou amanhã?"
        )
    else:
        msg = (
            f"Assunto: Proposta Personalizada CPAP - Luminar Saúde & {medico}\n\n"
            f"Prezado(a) {nome},\n\n"
            f"Com base na sua polissonografia (IAH {lead.get('iah')} ev/h, pressão {lead.get('pressao_titulada_cmh2o')} cmH2O), "
            f"estruturamos sua solução de terapia respiratória:\n\n"
            f"1. Equipamento: {rec['equipamento_recomendado']}\n"
            f"2. Máscara: {rec['mascara_recomendada']}\n"
            f"3. Insumos: {rec['insumos_cross_sell']}\n\n"
            f"Condições: {rec['condicao_comercial']}\n\n"
            f"Ficamos à disposição para agendamento da visita técnica de adaptação."
        )
        
    return {
        "status": "success",
        "lead_id": lead_id,
        "canal": canal,
        "mensagem_gerada": msg
    }

# -------------------------------------------------------------
# Tool 4: Criar Novo Lead Simulado em Tempo Real
# -------------------------------------------------------------
class NovoLeadRequest(BaseModel):
    nome_paciente: str = Field(..., example="Ana Paula Valente")
    idade: int = Field(45, example=45)
    genero: str = Field("F", example="F")
    telefone: str = Field("(11) 99999-8888", example="(11) 99999-8888")
    email: str = Field("ana.valente@email.com", example="ana.valente@email.com")
    cidade: str = Field("São Paulo", example="São Paulo")
    estado: str = Field("SP", example="SP")
    medico_prescritor: str = Field("Dr. Fernando Albuquerque", example="Dr. Fernando Albuquerque")
    crm_medico: str = Field("CRM-SP 142.890", example="CRM-SP 142.890")
    convenio: str = Field("Bradesco Saúde", example="Bradesco Saúde")
    iah: float = Field(34.5, example=34.5)
    spo2_minima: float = Field(76.0, example=76.0)
    pressao_titulada_cmh2o: float = Field(11.5, example=11.5)
    respiracao_predominante: str = Field("Oral / Mista", example="Oral / Mista")
    comorbidades: str = Field("Hipertensão, Fadiga Crônica", example="Hipertensão, Fadiga Crônica")

@app.post("/tools/criar_novo_lead", summary="Cria e qualifica um novo paciente em tempo real")
def criar_novo_lead(req: NovoLeadRequest):
    """
    Insere um novo lead no banco de dados e calcula imediatamente o score de qualificação
    e a recomendação de produtos.
    """
    df = get_leads_df()
    novo_id = f"LEAD-{1000 + len(df) + 1}"
    
    score = 95 if req.iah >= 30 else (85 if req.iah >= 15 else 70)
    urgencia = "URGENTE" if req.iah >= 40 else ("ALTA" if req.iah >= 30 else ("MEDIA" if req.iah >= 15 else "BAIXA"))
    
    novo_lead_dict = {
        "lead_id": novo_id,
        "nome_paciente": req.nome_paciente,
        "idade": req.idade,
        "genero": req.genero,
        "telefone": req.telefone,
        "email": req.email,
        "cidade": req.cidade,
        "estado": req.estado,
        "medico_prescritor": req.medico_prescritor,
        "crm_medico": req.crm_medico,
        "especialidade_medico": "Pneumologia e Medicina do Sono",
        "convenio": req.convenio,
        "diagnostico_cid": f"G47.3 - Apneia Obstrutiva do Sono ({'Grave' if req.iah >= 30 else 'Moderada'})",
        "iah": req.iah,
        "spo2_minima": req.spo2_minima,
        "spo2_media": 92.0,
        "pressao_titulada_cmh2o": req.pressao_titulada_cmh2o,
        "respiracao_predominante": req.respiracao_predominante,
        "presenca_ronco": "Alto / Frequente",
        "comorbidades": req.comorbidades,
        "sensibilidade_pressao": "Média a Alta",
        "score_prioridade": score,
        "urgencia_comercial": urgencia,
        "status_funil": "Qualificado - Novo Lead IA",
        "data_entrada": pd.Timestamp.now().strftime("%Y-%m-%d")
    }
    
    df_novo = pd.concat([df, pd.DataFrame([novo_lead_dict])], ignore_index=True)
    df_novo.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
    
    # Gera recomendação automática
    rec = recomendar_produtos(novo_id)
    
    return {
        "status": "success",
        "mensagem": f"Lead {novo_id} ({req.nome_paciente}) criado e qualificado com sucesso!",
        "lead_id": novo_id,
        "score_prioridade": score,
        "urgencia": urgencia,
        "recomendacao_imediata": rec
    }

# -------------------------------------------------------------
# Tool 5: Agente Autônomo de Qualificação (Agent Platform)
# -------------------------------------------------------------
from qualification_agent import LeadQualificationAgent
global_qualification_agent = LeadQualificationAgent()

class QualificacaoAgentRequest(BaseModel):
    lead_id: str = Field(..., example="LEAD-1001")
    notas_contexto: Optional[str] = Field("", example="Paciente tem receio de barulho durante a noite")
    session_id: Optional[str] = Field(None, example="sess-12345")

@app.post("/tools/qualificar_lead_agent", summary="Aciona o Agente Autônomo de Qualificação com Memory Bank e Sessions")
def qualificar_lead_agent(req: QualificacaoAgentRequest):
    """
    Aciona o fluxo autônomo do LeadQualificationAgent:
    - Recupera dados clínicos e laudos
    - Consulta e atualiza o Memory Bank do paciente
    - Faz o matching com o catálogo
    - Calcula o score de prioridade e SLA
    - Gera a proposta comercial e scripts de quebra de objeções
    """
    res = global_qualification_agent.qualify_lead(
        lead_id=req.lead_id,
        context_notes=req.notas_contexto or "",
        session_id=req.session_id
    )
    return res

# -------------------------------------------------------------
# Manifest & Health Check
# -------------------------------------------------------------
@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "luminar-saude-mcp-server"}

@app.get("/mcp/manifest.json", summary="MCP Server Manifest Definition")
def mcp_manifest():
    return {
        "schema_version": "v1",
        "name_for_model": "luminar_saude_sales_copilot",
        "name_for_human": "Luminar Saúde - Copiloto Comercial & CPAP",
        "description_for_model": "Ferramentas para consultar diagnósticos de apneia do sono, laudos polissonográficos, recomendar catálogos de CPAP/BiPAP/Máscaras e gerar pitches de vendas para a Luminar Saúde.",
        "description_for_human": "Assistente inteligente para vendedores da Luminar Saúde qualificarem leads e venderem CPAPs.",
        "tools": [
            {
                "name": "qualificar_lead_agent",
                "description": "Aciona o Agente Autônomo de Qualificação com Memory Bank e Sessions.",
                "endpoint": "/tools/qualificar_lead_agent"
            },
            {
                "name": "consultar_paciente",
                "description": "Busca laudo de sono, IAH, saturação de O2 e pressão de titulação de um paciente.",
                "endpoint": "/tools/consultar_paciente"
            },
            {
                "name": "recomendar_produtos",
                "description": "Calcula o melhor combo de CPAP, modelo de máscara e insumos para o paciente.",
                "endpoint": "/tools/recomendar_produtos"
            },
            {
                "name": "gerar_pitch_vendas",
                "description": "Gera texto personalizado para WhatsApp ou Gmail com quebra de objeções.",
                "endpoint": "/tools/gerar_pitch_vendas"
            },
            {
                "name": "criar_novo_lead",
                "description": "Insere um novo paciente simulado no banco de dados e qualifica na hora.",
                "endpoint": "/tools/criar_novo_lead"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
