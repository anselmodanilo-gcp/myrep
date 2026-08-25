#!/usr/bin/env python3
"""
🤖 Luminar Saúde - Agente Autônomo de Qualificação de Leads & Vendas CPAP
Implementação nativa para deploy no Vertex AI Agent Platform / Reasoning Engine
com suporte a Memory Bank, Sessions e Agent Registry.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

# ==============================================================================
# 1. MEMORY BANK & SESSION STORE
# ==============================================================================
class MemoryBank:
    """
    Banco de Memória Semântica e Episódica do Paciente/Lead.
    Armazena histórico, preferências, restrições, sensibilidade a ruído,
    histórico de claustrofobia e objeções registradas em interações anteriores.
    """
    def __init__(self):
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        
    def get_memory(self, user_id: str) -> Dict[str, Any]:
        return self._memory_store.get(user_id, {
            "user_id": user_id,
            "preferencias": {},
            "restricoes_clinicas": [],
            "objecoes_frequentes": [],
            "historico_interacoes": [],
            "ultima_atualizacao": datetime.datetime.now().isoformat()
        })
        
    def update_memory(self, user_id: str, key: str, value: Any):
        if user_id not in self._memory_store:
            self._memory_store[user_id] = self.get_memory(user_id)
        self._memory_store[user_id][key] = value
        self._memory_store[user_id]["ultima_atualizacao"] = datetime.datetime.now().isoformat()
        
    def add_interaction_note(self, user_id: str, note: str):
        mem = self.get_memory(user_id)
        mem["historico_interacoes"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "nota": note
        })
        self._memory_store[user_id] = mem


class SessionManager:
    """
    Gerenciador de Sessões de Atendimento Multiturno para o Vertex AI Agent Platform.
    Preserva o contexto de diálogo e rastreia o estado da qualificação.
    """
    def __init__(self):
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
        
    def create_session(self, session_id: Optional[str] = None) -> str:
        s_id = session_id or str(uuid.uuid4())
        if s_id not in self._sessions:
            self._sessions[s_id] = []
        return s_id
        
    def append_message(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self.create_session(session_id)
        self._sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self._sessions.get(session_id, [])


# ==============================================================================
# 2. CLASSE PRINCIPAL DO AGENTE DE QUALIFICAÇÃO
# ==============================================================================
class LeadQualificationAgent:
    """
    Agente Autônomo de Qualificação de Leads da Luminar Saúde.
    Compatível com Vertex AI Reasoning Engine e Agent Registry.
    """
    def __init__(
        self,
        project_id: str = "abiding-arch-505313-m3",
        dataset_id: str = "luminar_saude",
        location: str = "southamerica-east1",
        model_name: str = "gemini-1.5-flash"
    ):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.location = location
        self.model_name = model_name
        self.memory_bank = MemoryBank()
        self.session_manager = SessionManager()
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.data_dir = os.path.join(self.base_dir, "bigquery", "data")

    def set_up(self):
        """Inicialização e aquecimento de conexões com Vertex AI."""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(
                self.model_name,
                system_instruction=[
                    "Você é o Agente Autônomo Especialista em Qualificação de Leads e Medicina do Sono da Luminar Saúde.",
                    "Sua missão é analisar laudos de polissonografia, cruzar dados com o catálogo e estruturar propostas comerciais completas."
                ]
            )
        except Exception:
            self.model = None

    # -------------------------------------------------------------
    # FERRAMENTAS INTERNAS (TOOLS)
    # -------------------------------------------------------------
    def _get_leads_df(self) -> pd.DataFrame:
        p = os.path.join(self.data_dir, "leads_pacientes.csv")
        return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

    def _get_catalogo_df(self) -> pd.DataFrame:
        p = os.path.join(self.data_dir, "catalogo_produtos.csv")
        return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

    def query_patient_data(self, lead_id: str) -> Dict[str, Any]:
        """Busca os dados clínicos e cadastrais do paciente."""
        df = self._get_leads_df()
        if df.empty:
            return {"status": "error", "message": "Base de dados vazia."}
        
        match = df[df['lead_id'].str.upper() == lead_id.upper()]
        if match.empty:
            match = df[df['nome_paciente'].str.contains(lead_id, case=False, na=False)]
        
        if match.empty:
            return {"status": "error", "message": f"Lead {lead_id} não encontrado."}
        
        return match.iloc[0].to_dict()

    def match_cpap_catalog(self, pressao: float, respiracao: str, comorbidades: str = "") -> Dict[str, Any]:
        """Calcula o combo ideal de CPAP, Máscara e Insumos."""
        is_oral = "oral" in respiracao.lower() or "bucal" in respiracao.lower()
        is_cardio = "cardíaca" in comorbidades.lower() or "arritmia" in comorbidades.lower()
        
        if pressao > 14.5 or is_cardio:
            equipamento = "ResMed AirCurve 10 VAuto (BiPAP)"
            sku_eq = "BIPAP-RES-AC10"
            preco_eq = 9800.00
            racional_eq = "Pressão de titulação muito alta ou comorbidade cardíaca; o BiPAP com alívio binível evita fadiga respiratória."
        else:
            equipamento = "ResMed AirSense 11 AutoSet"
            sku_eq = "CPAP-RES-AS11"
            preco_eq = 5890.00
            racional_eq = "Titulação automática com alívio de pressão expiratório (EPR 3) e conexão celular 4G AirView."
            
        if is_oral or pressao >= 12.0:
            mascara = "AirFit F20 Full Face (Facial)"
            sku_mk = "MSK-RES-F20"
            preco_mk = 890.00
            racional_mk = "Obrigatória para respirador oral e pressões elevadas, garantindo vedação total sem escape de ar bucal."
        else:
            mascara = "AirFit P10 (Almofadas Nasais Ultraleves) ou N20 Nasal"
            sku_mk = "MSK-RES-P10"
            preco_mk = 690.00
            racional_mk = "Ultraleve (apenas 45g), ideal para respiração nasal, conforto máximo e pacientes com receio de claustrofobia."
            
        insumos = "Tubo Aquecido ClimateLineAir + Kit Filtros Hipoalergênicos + Lenços CPAP Wipes"
        total = preco_eq + preco_mk + 390.00 + 150.00 + 75.00
        
        return {
            "equipamento_recomendado": equipamento,
            "sku_equipamento": sku_eq,
            "preco_equipamento": preco_eq,
            "racional_equipamento": racional_eq,
            "mascara_recomendada": mascara,
            "sku_mascara": sku_mk,
            "preco_mascara": preco_mk,
            "racional_mascara": racional_mk,
            "insumos_cross_sell": insumos,
            "valor_total_pacote": total,
            "condicao_sugerida": f"12x de R$ {total/12:.2f} sem juros ou 8% desc. à vista no PIX (R$ {total*0.92:.2f})"
        }

    # -------------------------------------------------------------
    # QUALIFICAÇÃO AUTÔNOMA END-TO-END
    # -------------------------------------------------------------
    def qualify_lead(self, lead_id: str, context_notes: str = "", session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa a qualificação autônoma completa do lead ao ser acionado:
        1. Consulta dados do paciente e laudo polissonográfico.
        2. Consulta o Memory Bank para preferências e restrições prévias.
        3. Realiza o matching clínico com o catálogo de produtos.
        4. Calcula o score de prioridade e SLA de atendimento.
        5. Gera a proposta comercial personalizada e argumentos de quebra de objeções.
        6. Registra na sessão e atualiza o Memory Bank.
        """
        s_id = self.session_manager.create_session(session_id)
        self.session_manager.append_message(s_id, "system", f"Iniciando qualificação autônoma do lead: {lead_id}")
        
        # 1. Obter dados do paciente
        p_data = self.query_patient_data(lead_id)
        if "status" in p_data and p_data["status"] == "error":
            return p_data
            
        nome = p_data.get("nome_paciente", "Paciente")
        iah = float(p_data.get("iah", 20.0))
        pressao = float(p_data.get("pressao_titulada_cmh2o", 10.0))
        resp = str(p_data.get("respiracao_predominante", "Oral / Mista"))
        comorb = str(p_data.get("comorbidades", ""))
        
        # 2. Consultar Memory Bank
        mem = self.memory_bank.get_memory(lead_id)
        if context_notes:
            self.memory_bank.add_interaction_note(lead_id, context_notes)
            
        # 3. Matching Clínico
        combo = self.match_cpap_catalog(pressao, resp, comorb)
        
        # 4. Cálculo de Score & SLA
        if iah >= 35.0 or pressao >= 14.0:
            score = 98
            urgencia = "URGENTE"
            sla_horas = 2
        elif iah >= 20.0:
            score = 88
            urgencia = "ALTA"
            sla_horas = 4
        else:
            score = 75
            urgencia = "MEDIA"
            sla_horas = 24
            
        # 5. Elaboração da Proposta e Quebra de Objeções
        pitch_whatsapp = (
            f"Olá, {nome}! Tudo bem? Aqui é o especialista da Luminar Saúde.\n\n"
            f"Recebemos seu laudo médico e estruturamos seu tratamento com o moderno {combo['equipamento_recomendado']} "
            f"e a máscara {combo['mascara_recomendada']}.\n\n"
            f"✨ Destaques do seu pacote:\n"
            f"- Silêncio absoluto durante o sono (25 dBA)\n"
            f"- Alívio de pressão automático para respirar naturalmente\n"
            f"- Programa Luminar Adaptação 30 Dias: troca 100% gratuita de máscara se sentir qualquer desconforto!\n\n"
            f"💳 Condição Especial: {combo['condicao_sugerida']}\n\n"
            f"Podemos agendar a visita técnica de adaptação na sua residência hoje ou amanhã?"
        )
        
        # 6. Atualizar Memory Bank com a qualificação
        self.memory_bank.update_memory(lead_id, "score_prioridade", score)
        self.memory_bank.update_memory(lead_id, "urgencia", urgencia)
        self.memory_bank.update_memory(lead_id, "combo_recomendado", combo["equipamento_recomendado"])
        self.memory_bank.update_memory(lead_id, "mascara_recomendada", combo["mascara_recomendada"])
        
        resposta_final = {
            "status": "success",
            "lead_id": lead_id,
            "session_id": s_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "paciente": {
                "nome": nome,
                "idade": p_data.get("idade"),
                "diagnostico_cid": p_data.get("diagnostico_cid"),
                "iah": iah,
                "spo2_minima": p_data.get("spo2_minima"),
                "pressao_titulada_cmh2o": pressao,
                "respiracao_predominante": resp,
                "medico_prescritor": p_data.get("medico_prescritor")
            },
            "qualificacao_ia": {
                "score_prioridade": score,
                "urgencia_comercial": urgencia,
                "sla_atendimento_horas": sla_horas,
                "racional_clinico": f"Paciente com IAH {iah} ev/h ({'Grave' if iah>=30 else 'Moderada'}) e pressão {pressao} cmH2O."
            },
            "recomendacao_produtos": combo,
            "proposta_comercial": {
                "pitch_whatsapp": pitch_whatsapp,
                "quebra_objecoes_sugerida": "Destacar o Programa Luminar Adaptação 30 Dias e o baixo nível de ruído (25 dBA)."
            },
            "memory_bank_snapshot": self.memory_bank.get_memory(lead_id)
        }
        
        self.session_manager.append_message(s_id, "assistant", json.dumps(resposta_final, ensure_ascii=False))
        return resposta_final

    def query(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Interface padrão de conversação multiturno para o Vertex AI Agent Platform."""
        s_id = self.session_manager.create_session(session_id)
        self.session_manager.append_message(s_id, "user", message)
        
        # Resposta inteligente consultando ferramentas internas
        if "qualificar" in message.lower() or "lead-" in message.lower():
            # Extrai ID do lead se presente
            for token in message.replace(":", " ").replace(",", " ").split():
                if token.upper().startswith("LEAD-"):
                    return self.qualify_lead(token.upper(), session_id=s_id)
            return self.qualify_lead("LEAD-1001", session_id=s_id)
            
        elif "roberto" in message.lower():
            return self.qualify_lead("LEAD-1001", session_id=s_id)
        elif "mariana" in message.lower():
            return self.qualify_lead("LEAD-1002", session_id=s_id)
        elif "carlos" in message.lower():
            return self.qualify_lead("LEAD-1003", session_id=s_id)
        else:
            resposta = {
                "status": "success",
                "session_id": s_id,
                "mensagem": "Sou o Agente de Qualificação Luminar Saúde. Informe o ID do Lead (ex: LEAD-1001) para qualificar automaticamente."
            }
            self.session_manager.append_message(s_id, "assistant", resposta["mensagem"])
            return resposta

if __name__ == "__main__":
    agent = LeadQualificationAgent()
    res = agent.qualify_lead("LEAD-1001", context_notes="Paciente com receio de barulho durante a noite.")
    print(json.dumps(res, indent=2, ensure_ascii=False))
