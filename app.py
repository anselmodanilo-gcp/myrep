import streamlit as st
import pandas as pd
import json
import os
import glob
from datetime import datetime, timedelta
import random

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Luminar Saúde | Gerenciador da Demo & Hub de Dados para Gemini Enterprise",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# DESIGN SYSTEM COM ALTA LEGIBILIDADE E CONTRASTE
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }
    
    .main-header {
        font-size: 24px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .sub-header {
        font-size: 15px;
        color: #334155;
        margin-bottom: 24px;
        font-weight: 400;
        line-height: 1.5;
    }
    .card-container {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .prompt-box {
        background-color: #F1F5F9;
        border: 1px solid #94A3B8;
        border-left: 5px solid #0284C7;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 12px 0;
        font-family: 'Inter', sans-serif;
        color: #0F172A;
        font-size: 14.5px;
        line-height: 1.6;
    }
    .scenario-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-left: 5px solid #0369A1;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .scenario-title {
        font-weight: 700;
        color: #0369A1;
        font-size: 16px;
        margin-bottom: 6px;
    }
    .gemini-badge {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
    }
    .source-badge {
        background-color: #E2E8F0;
        color: #1E293B;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CARGA E GESTÃO DE DADOS
# ==============================================================================
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "bigquery", "data")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "laudos_polissonografia"), exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "receitas_medicas"), exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "catalogos_manuais"), exist_ok=True)

def load_data():
    p_leads = os.path.join(DATA_DIR, "leads_pacientes.csv")
    p_cat = os.path.join(DATA_DIR, "catalogo_produtos.csv")
    p_rec = os.path.join(DATA_DIR, "recomendacoes_vendedor.csv")
    p_hist = os.path.join(DATA_DIR, "historico_compras_trocas.csv")
    
    df_leads = pd.read_csv(p_leads) if os.path.exists(p_leads) else pd.DataFrame()
    df_cat = pd.read_csv(p_cat) if os.path.exists(p_cat) else pd.DataFrame()
    df_rec = pd.read_csv(p_rec) if os.path.exists(p_rec) else pd.DataFrame()
    df_hist = pd.read_csv(p_hist) if os.path.exists(p_hist) else pd.DataFrame()
    return df_leads, df_cat, df_rec, df_hist

def reset_demo_data():
    try:
        import subprocess
        subprocess.run(["python3", "generate_assets.py"], check=True)
        subprocess.run(["python3", "generate_extra_docs.py"], check=True)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao resetar base: {e}")
        return False

df_leads, df_catalogo, df_rec, df_hist = load_data()

# ==============================================================================
# MENU LATERAL - CENTRO DE CONTROLE DA DEMO
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/lungs.png", width=50)
st.sidebar.markdown("### **Luminar Saúde**")
st.sidebar.markdown("**Gerenciador da Demo & Hub de Dados**")
st.sidebar.caption("Fonte de Dados para: **Gemini Enterprise**")

menu = st.sidebar.radio(
    "Navegação do Gerenciador:",
    [
        "🧭 1. Roteiro da Demo & Prompts do Gemini Enterprise",
        "🪄 2. Gerador de Dados Sintéticos & Injeção ao Vivo",
        "📊 3. Inspeção de Fontes de Dados (BigQuery & Storage)",
        "⚙️ 4. Conexões do Gemini Enterprise & Reset da Base"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🔄 Ações Rápidas")
if st.sidebar.button("Restaurar Base Padrão da Demo", use_container_width=True):
    if reset_demo_data():
        st.sidebar.success("Base restaurada com sucesso!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size:12.5px; color:#334155; line-height:1.5;">
<b>Arquitetura da Demo:</b><br/>
• <b>Gerenciador (Cloud Run):</b> Gera dados e controla cenários.<br/>
• <b>Ponto de Acesso do Usuário:</b> Gemini Enterprise (Chat com dados, busca em PDFs e tools MCP).
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# MENU 1: ROTEIRO DA DEMO & PROMPTS DO GEMINI ENTERPRISE
# ==============================================================================
if "1. Roteiro" in menu:
    st.markdown('<div class="main-header">🧭 Roteiro da Demonstração & Prompts para o Gemini Enterprise</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Utilize este roteiro durante a apresentação. O <b>Gemini Enterprise</b> é o ponto de acesso único onde você fará as perguntas, consultará os laudos em PDF e obterá as recomendações de CPAP.</div>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="card-container">
            <span class="gemini-badge">Fonte BigQuery</span>
            <div style="font-size:20px; font-weight:700; color:#0F172A;">""" + str(len(df_leads)) + """ Pacientes</div>
            <div style="font-size:13px; color:#475569;">CRM e métricas clínicas no BigQuery</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        laudos_count = len(glob.glob(os.path.join(STORAGE_DIR, "laudos_polissonografia", "*.*")))
        st.markdown("""
        <div class="card-container">
            <span class="gemini-badge">Fonte Cloud Storage</span>
            <div style="font-size:20px; font-weight:700; color:#0F172A;">""" + str(laudos_count) + """ Laudos & PDFs</div>
            <div style="font-size:13px; color:#475569;">Polissonografias e Prescrições Médicas</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="card-container">
            <span class="gemini-badge">Ferramentas MCP</span>
            <div style="font-size:20px; font-weight:700; color:#0F172A;">4 Tools Ativas</div>
            <div style="font-size:13px; color:#475569;">Matching, Pitch e Consulta Clínica</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎬 Atos da Apresentação com Prompts do Gemini Enterprise")

    # ATO 1
    with st.expander("📍 **ATO 1: O Desafio Comercial & Consulta ao Gemini Enterprise (2 min)**", expanded=True):
        st.markdown("""
        <div class="scenario-card">
            <div class="scenario-title">1. Contexto & Consulta Geral de Leads</div>
            <p><b>Objetivo:</b> Mostrar como o vendedor consulta o Gemini Enterprise para entender quem são os pacientes que precisam de atendimento prioritário hoje.</p>
            <p><b>Prompt para copiar e colar no Gemini Enterprise:</b></p>
            <div class="prompt-box">
            <b>"Quais são os pacientes com apneia do sono grave na nossa base do BigQuery que exigem contato imediato da equipe de vendas? Apresente o IAH, saturação mínima e médico prescritor de cada um."</b>
            </div>
            <p><b>O que o Gemini Enterprise fará:</b> Consultará o BigQuery <code>luminar_saude.leads_pacientes</code> e listará os pacientes com IAH &gt;= 30 (como Roberto Silveira Santos e Carlos Eduardo Paes).</p>
        </div>
        """, unsafe_allow_html=True)

    # ATO 2
    with st.expander("📍 **ATO 2: Extração Multimodal do Laudo de Polissonografia (3 min)**", expanded=True):
        st.markdown("""
        <div class="scenario-card">
            <div class="scenario-title">2. Busca de Conhecimento Não Estruturado (PDFs no Cloud Storage)</div>
            <p><b>Objetivo:</b> Demonstrar o Gemini Enterprise lendo o laudo médico original em PDF armazenado no Cloud Storage e traduzindo termos médicos complexos.</p>
            <p><b>Prompt para copiar e colar no Gemini Enterprise:</b></p>
            <div class="prompt-box">
            <b>"Abra o laudo polissonográfico do paciente Roberto Silveira Santos no Cloud Storage e resuma: qual foi a pressão titulada recomendada pelo Dr. Fernando Albuquerque e qual é o padrão respiratório dele?"</b>
            </div>
            <p><b>Resposta esperada do Gemini:</b> Identificará pressão de 12.0 cmH2O, IAH de 38.4 eventos/hora e respiração bucal/mista.</p>
        </div>
        """, unsafe_allow_html=True)

    # ATO 3
    with st.expander("📍 **ATO 3: Matching Inteligente de CPAP, Máscara e Quebra de Objeções (3 min)**", expanded=True):
        st.markdown("""
        <div class="scenario-card">
            <div class="scenario-title">3. Recomendação de Produtos com Ferramentas MCP & Proposta Comercial</div>
            <p><b>Objetivo:</b> Mostrar a IA recomendando o combo completo de produtos (equipamento + máscara correta + tubo aquecido) e redigindo a mensagem comercial.</p>
            <p><b>Prompt para copiar e colar no Gemini Enterprise:</b></p>
            <div class="prompt-box">
            <b>"Com base no laudo e na respiração bucal do Roberto Silveira, qual modelo de CPAP e qual máscara do nosso catálogo devo ofertar? Gere também uma proposta comercial com quebra de objeções sobre adaptação para envio via WhatsApp."</b>
            </div>
            <p><b>Resposta esperada do Gemini:</b>
            <br/>• Equipamento: <i>ResMed AirSense 11 AutoSet</i>
            <br/>• Máscara: <i>ResMed AirFit F20 Facial</i> (obrigatória para quem respira pela boca e tem pressão &gt;= 12 cmH2O)
            <br/>• Argumento: Destaque do programa <i>'Luminar Adaptação 30 Dias'</i> (troca grátis de modelo de máscara caso sinta desconforto).
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ATO 4
    with st.expander("📍 **ATO 4: Injeção de Novo Lead ao Vivo & Reação do Gemini (3 min)**", expanded=True):
        st.markdown("""
        <div class="scenario-card">
            <div class="scenario-title">4. Injeção de Dados em Tempo Real pelo Gerenciador</div>
            <p><b>Objetivo:</b> Mostrar a agilidade do ecossistema: um novo lead é gerado aqui no menu <b>2. Gerador de Dados</b> e imediatamente o Gemini Enterprise já sabe tudo sobre ele.</p>
            <p><b>Ação do Apresentador:</b>
            <br/>1. Vá ao menu <b>2. Gerador de Dados Sintéticos</b> e clique em <i>'Injetar Cenário: Juliana Silveira (Rinite & Claustrofobia)'</i>.
            <br/>2. Volte ao Gemini Enterprise e execute o prompt abaixo:
            </p>
            <div class="prompt-box">
            <b>"A paciente Juliana Silveira acabou de ser cadastrada. Ela tem rinite alérgica crônica e queixa de claustrofobia com máscaras faciais grandes. O que você recomenda para o caso dela?"</b>
            </div>
            <p><b>Resposta esperada do Gemini:</b> Recomendação da <i>Máscara de Almofadas Nasais AirFit P10 (45g)</i> ultraleve com filtros hipoalergênicos.</p>
        </div>
        """, unsafe_allow_html=True)

    # ATO 5
    with st.expander("📍 **ATO 5: Recorrência & Gestão do Ciclo de Vida (LTV) (2 min)**", expanded=True):
        st.markdown("""
        <div class="scenario-card">
            <div class="scenario-title">5. Proatividade de Vendas em Insumos Recorrentes</div>
            <p><b>Objetivo:</b> Mostrar o Gemini Enterprise analisando a tabela de histórico de compras para identificar oportunidades de reposição de almofadas e filtros.</p>
            <p><b>Prompt para copiar e colar no Gemini Enterprise:</b></p>
            <div class="prompt-box">
            <b>"Consulte o histórico de compras no BigQuery e liste quais clientes estão usando a mesma almofada de máscara há mais de 180 dias. Redija um lembrete empático de saúde para enviar aos pacientes elegíveis para troca."</b>
            </div>
            <p><b>Resposta esperada do Gemini:</b> Identificará os clientes com alerta de troca e redigirá o lembrete focado em higiene, vedação e conforto.</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# MENU 2: GERADOR DE DADOS SINTÉTICOS & INJEÇÃO AO VIVO
# ==============================================================================
elif "2. Gerador" in menu:
    st.markdown('<div class="main-header">🪄 Gerador de Dados Sintéticos para Ingestão no Gemini Enterprise</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Crie dados estruturados (BigQuery) e não estruturados (PDFs/TXTs no Storage) para alimentar as consultas do <b>Gemini Enterprise</b> durante a demonstração.</div>', unsafe_allow_html=True)
    
    tab_rapida, tab_form_lead, tab_form_hist = st.tabs([
        "⚡ Injeção Rápida de Cenários (1-Clique)",
        "📝 Criador Customizado de Paciente, Laudo & Objeções",
        "🔄 Injetor de Histórico de Compras (LTV)"
    ])
    
    with tab_rapida:
        st.subheader("⚡ Cenários Pré-Configurados para Injeção Instantânea")
        st.markdown("Ao clicar em qualquer botão, o paciente é gravado no BigQuery e seu laudo médico é gerado no Cloud Storage para busca do Gemini Enterprise:")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("""
            <div class="scenario-card">
                <div class="scenario-title">🚨 1. Apneia Crítica com Hipoxemia Severa</div>
                <b>Paciente:</b> Eduardo Brandão Fontes (58 anos, SP)<br/>
                <b>Diagnóstico:</b> IAH 42.8 ev/h, SpO2 mínima 71%, Pressão 14 cmH2O, Respiração bucal.<br/>
                <b>Contexto:</b> Risco cardiovascular iminente, sonolência diurna grave.
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Injetar Paciente 1: Eduardo Brandão", use_container_width=True):
                novo_id = f"LEAD-{1000 + len(df_leads) + 1}"
                novo_dict = {
                    "lead_id": novo_id,
                    "nome_paciente": "Eduardo Brandão Fontes",
                    "idade": 58,
                    "genero": "M",
                    "telefone": "(11) 98111-2233",
                    "email": "eduardo.fontes@email.com",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "medico_prescritor": "Dr. Fernando Albuquerque",
                    "crm_medico": "CRM-SP 142.890",
                    "especialidade_medico": "Pneumologia",
                    "convenio": "Bradesco Saúde",
                    "diagnostico_cid": "G47.3 - Apneia Grave com Hipoxemia Severa",
                    "iah": 42.8,
                    "spo2_minima": 71.0,
                    "spo2_media": 89.0,
                    "pressao_titulada_cmh2o": 14.0,
                    "respiracao_predominante": "Oral / Mista",
                    "presenca_ronco": "Muito Alto / Frequente",
                    "comorbidades": "Hipertensão Refratária, Obesidade Grau II",
                    "sensibilidade_pressao": "Alta",
                    "score_prioridade": 98,
                    "urgencia_comercial": "URGENTE",
                    "status_funil": "Qualificado - Lead Live Demo",
                    "data_entrada": datetime.now().strftime("%Y-%m-%d")
                }
                df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
                df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
                
                # Gera laudo em TXT no storage
                laudo_p = os.path.join(STORAGE_DIR, "laudos_polissonografia", "laudo_psg_eduardo_fontes.txt")
                with open(laudo_p, "w", encoding="utf-8") as f:
                    f.write(f"CLÍNICA DE MEDICINA DO SONO - LAUDO DE POLISSONOGRAFIA\nPACIENTE: Eduardo Brandão Fontes\nIAH: 42.8 ev/h (GRAVE)\nSpO2 Mínima: 71%\nPressão Titulada: 14.0 cmH2O\nRespiração: Oral / Mista\nMédico: Dr. Fernando Albuquerque (CRM-SP 142.890)")
                
                st.success(f"✅ Paciente {novo_id} (Eduardo Brandão) injetado com sucesso! Já disponível para consultas no Gemini Enterprise.")
                st.rerun()

            st.markdown("""
            <div class="scenario-card">
                <div class="scenario-title">✈️ 2. Executivo de Viagens (Busca CPAP Portátil)</div>
                <b>Paciente:</b> Marcelo Guimarães Dias (44 anos, SP)<br/>
                <b>Diagnóstico:</b> IAH 14.5 ev/h, Pressão 7.5 cmH2O, Respiração Nasal.<br/>
                <b>Objeção:</b> <i>'Preciso de um equipamento que caiba na minha mala de bordo.'</i>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Injetar Paciente 2: Marcelo Guimarães", use_container_width=True):
                novo_id = f"LEAD-{1000 + len(df_leads) + 1}"
                novo_dict = {
                    "lead_id": novo_id,
                    "nome_paciente": "Marcelo Guimarães Dias",
                    "idade": 44,
                    "genero": "M",
                    "telefone": "(11) 99333-4455",
                    "email": "marcelo.guimaraes@empresa.com",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "medico_prescritor": "Dr. Fernando Albuquerque",
                    "crm_medico": "CRM-SP 142.890",
                    "especialidade_medico": "Pneumologia",
                    "convenio": "Amil One",
                    "diagnostico_cid": "G47.3 - Apneia Leve-Moderada em Viagens",
                    "iah": 14.5,
                    "spo2_minima": 88.0,
                    "spo2_media": 95.0,
                    "pressao_titulada_cmh2o": 7.5,
                    "respiracao_predominante": "Nasal",
                    "presenca_ronco": "Moderado",
                    "comorbidades": "Viagens aéreas semanais frequentes",
                    "sensibilidade_pressao": "Baixa",
                    "score_prioridade": 82,
                    "urgencia_comercial": "MEDIA",
                    "status_funil": "Qualificado - Lead Live Demo",
                    "data_entrada": datetime.now().strftime("%Y-%m-%d")
                }
                df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
                df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
                st.success(f"✅ Paciente {novo_id} (Marcelo Guimarães) injetado com sucesso! Já disponível no Gemini Enterprise.")
                st.rerun()

        with c2:
            st.markdown("""
            <div class="scenario-card">
                <div class="scenario-title">🤧 3. Rinite Alérgica & Pânico de Claustrofobia</div>
                <b>Paciente:</b> Juliana Silveira Nogueira (39 anos, Campinas/SP)<br/>
                <b>Diagnóstico:</b> IAH 19.4 ev/h, SpO2 85%, Pressão 8.0 cmH2O, Respiração Nasal.<br/>
                <b>Objeção:</b> <i>'Tenho pânico de máscara fechada no rosto.'</i>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Injetar Paciente 3: Juliana Silveira", use_container_width=True):
                novo_id = f"LEAD-{1000 + len(df_leads) + 1}"
                novo_dict = {
                    "lead_id": novo_id,
                    "nome_paciente": "Juliana Silveira Nogueira",
                    "idade": 39,
                    "genero": "F",
                    "telefone": "(11) 97222-3344",
                    "email": "juliana.nogueira@email.com",
                    "cidade": "Campinas",
                    "estado": "SP",
                    "medico_prescritor": "Dra. Beatriz Mendes",
                    "crm_medico": "CRM-SP 178.432",
                    "especialidade_medico": "Otorrinolaringologia",
                    "convenio": "SulAmérica",
                    "diagnostico_cid": "G47.3 - Apneia Moderada com Rinite",
                    "iah": 19.4,
                    "spo2_minima": 85.0,
                    "spo2_media": 94.0,
                    "pressao_titulada_cmh2o": 8.0,
                    "respiracao_predominante": "Nasal",
                    "presenca_ronco": "Moderado",
                    "comorbidades": "Rinite Alérgica Crônica, Claustrofobia com Máscaras Faciais",
                    "sensibilidade_pressao": "Média",
                    "score_prioridade": 86,
                    "urgencia_comercial": "ALTA",
                    "status_funil": "Qualificado - Lead Live Demo",
                    "data_entrada": datetime.now().strftime("%Y-%m-%d")
                }
                df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
                df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
                st.success(f"✅ Paciente {novo_id} (Juliana Silveira) injetada com sucesso! Já disponível no Gemini Enterprise.")
                st.rerun()

            st.markdown("""
            <div class="scenario-card">
                <div class="scenario-title">🫀 4. Cardiopata com Pressão Alta (Indicação BiPAP)</div>
                <b>Paciente:</b> Alvaro Ramos de Souza (67 anos, RJ)<br/>
                <b>Diagnóstico:</b> IAH 48.2 ev/h, SpO2 66%, Pressão 16.0 cmH2O, Insuficiência Cardíaca.<br/>
                <b>Indicação:</b> BiPAP (Pressão Binível) devido à alta resistência expiratória.
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Injetar Paciente 4: Alvaro Ramos", use_container_width=True):
                novo_id = f"LEAD-{1000 + len(df_leads) + 1}"
                novo_dict = {
                    "lead_id": novo_id,
                    "nome_paciente": "Alvaro Ramos de Souza",
                    "idade": 67,
                    "genero": "M",
                    "telefone": "(21) 98444-5566",
                    "email": "alvaro.ramos@email.com",
                    "cidade": "Rio de Janeiro",
                    "estado": "RJ",
                    "medico_prescritor": "Dr. Henrique Vasconcellos",
                    "crm_medico": "CRM-RJ 98.765",
                    "especialidade_medico": "Cardiologia",
                    "convenio": "Particular (Reembolso)",
                    "diagnostico_cid": "G47.3 - Apneia Severa com Insuficiência Cardíaca",
                    "iah": 48.2,
                    "spo2_minima": 66.0,
                    "spo2_media": 87.0,
                    "pressao_titulada_cmh2o": 16.0,
                    "respiracao_predominante": "Oral",
                    "presenca_ronco": "Grave",
                    "comorbidades": "Insuficiência Cardíaca, Fibrilação Atrial",
                    "sensibilidade_pressao": "Extrema (intolerante a CPAP convencional)",
                    "score_prioridade": 99,
                    "urgencia_comercial": "URGENTE",
                    "status_funil": "Qualificado - Lead Live Demo",
                    "data_entrada": datetime.now().strftime("%Y-%m-%d")
                }
                df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
                df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
                st.success(f"✅ Paciente {novo_id} (Alvaro Ramos) injetado com sucesso! Já disponível no Gemini Enterprise.")
                st.rerun()

    with tab_form_lead:
        st.subheader("📝 Criador Customizado de Paciente, Laudo e Contexto de Vendas")
        st.markdown("Preencha para criar um paciente específico e gerar os dados para o Gemini Enterprise:")
        
        with st.form("form_novo_paciente_custom"):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.markdown("##### 👤 1. Identificação")
                c_nome = st.text_input("Nome Completo", "Dr. Maurício Becker")
                c_idade = st.number_input("Idade", 18, 95, 52)
                c_genero = st.selectbox("Gênero", ["M", "F"])
                c_tel = st.text_input("WhatsApp", "(11) 98765-4321")
                c_cidade = st.text_input("Cidade / Estado", "São Paulo/SP")
                c_convenio = st.selectbox("Convênio", ["Bradesco Saúde", "SulAmérica", "Amil One", "Unimed", "Particular"])
            with fc2:
                st.markdown("##### 🫁 2. Parâmetros da Polissonografia")
                c_iah = st.number_input("IAH (Eventos/hora)", 1.0, 120.0, 36.5)
                c_spo2 = st.number_input("SpO2 Mínima (%)", 50.0, 99.0, 75.0)
                c_pressao = st.number_input("Pressão Titulada (cmH2O)", 4.0, 25.0, 11.5)
                c_resp = st.selectbox("Padrão Respiratório", ["Oral / Mista", "Nasal", "Exclusivamente Bucal"])
                c_medico = st.text_input("Médico Prescritor", "Dr. Fernando Albuquerque")
                c_comorb = st.text_input("Comorbidades / Sintomas", "Hipertensão, Sonolência Diurna, Ronco Alto")
            with fc3:
                st.markdown("##### 💬 3. Objeções & Contexto do Cliente")
                c_objecao = st.selectbox(
                    "Principal Objeção:",
                    [
                        "Claustrofobia: 'Tenho medo de me sentir sufocado'",
                        "Ruído: 'Tenho medo do barulho acordar minha esposa'",
                        "Preço: 'Preciso de parcelamento sem juros em 12x'",
                        "Adaptação: 'E se eu não me acostumar a dormir com o CPAP?'"
                    ]
                )
                c_pergunta = st.text_area(
                    "Dúvida enviada pelo cliente no WhatsApp:",
                    "Olá, recebi a recomendação de CPAP com pressão 11.5, mas tenho muito medo de me sentir sufocado com a máscara. Vocês oferecem garantia de adaptação?",
                    height=100
                )
                
            sub_custom = st.form_submit_button("🚀 Gravar Paciente no BigQuery & Gerar Laudo no Storage", use_container_width=True)
            if sub_custom:
                novo_id = f"LEAD-{1000 + len(df_leads) + 1}"
                first_name = c_nome.split()[0].lower()
                last_name = c_nome.split()[-1].lower()
                
                # Gera laudo em TXT no storage
                laudo_txt_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", f"laudo_psg_{first_name}_{last_name}.txt")
                with open(laudo_txt_path, "w", encoding="utf-8") as f:
                    f.write(f"CLÍNICA DE MEDICINA DO SONO\nLAUDO DE POLISSONOGRAFIA\nPACIENTE: {c_nome}\nIAH: {c_iah} ev/h\nSpO2 Mínima: {c_spo2}%\nPressão: {c_pressao} cmH2O\nRespiração: {c_resp}\nMédico: {c_medico}\nComorbidades: {c_comorb}\nObjeção Registrada: {c_objecao}")
                    
                novo_dict = {
                    "lead_id": novo_id,
                    "nome_paciente": c_nome,
                    "idade": c_idade,
                    "genero": c_genero,
                    "telefone": c_tel,
                    "email": f"{first_name}.{last_name}@email.com",
                    "cidade": c_cidade.split("/")[0],
                    "estado": c_cidade.split("/")[-1] if "/" in c_cidade else "SP",
                    "medico_prescritor": c_medico,
                    "crm_medico": "CRM-SP 142.890",
                    "especialidade_medico": "Pneumologia",
                    "convenio": c_convenio,
                    "diagnostico_cid": f"G47.3 - Apneia Obstrutiva ({'Grave' if c_iah>=30 else 'Moderada'})",
                    "iah": c_iah,
                    "spo2_minima": c_spo2,
                    "spo2_media": 92.0,
                    "pressao_titulada_cmh2o": c_pressao,
                    "respiracao_predominante": c_resp,
                    "presenca_ronco": "Alto",
                    "comorbidades": f"{c_comorb} | Objeção: {c_objecao}",
                    "sensibilidade_pressao": "Média",
                    "score_prioridade": 95 if c_iah>=30 else 80,
                    "urgencia_comercial": "URGENTE" if c_iah>=30 else "ALTA",
                    "status_funil": "Qualificado - Lead Live Demo",
                    "data_entrada": datetime.now().strftime("%Y-%m-%d")
                }
                df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
                df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
                st.success(f"🎉 Paciente **{novo_id} ({c_nome})** cadastrado e laudo gravado no Storage! Pronto para consulta no Gemini Enterprise.")
                st.rerun()

    with tab_form_hist:
        st.subheader("🔄 Injetor de Histórico de Compras e Recorrência (LTV)")
        st.markdown("Adicione registros de compras antigas para testar alertas de reposição periódica no Gemini Enterprise:")
        
        with st.form("form_hist_ltv"):
            hc1, hc2 = st.columns(2)
            with hc1:
                h_pac = st.selectbox("Paciente:", df_leads['nome_paciente'].tolist() if not df_leads.empty else ["Roberto Silveira Santos"])
                h_prod = st.selectbox("Equipamento / Máscara:", ["CPAP ResMed AirSense 11", "Máscara Facial AirFit F20", "Máscara Nasal AirFit N20"])
            with hc2:
                h_dias = st.slider("Dias desde a compra da almofada de silicone:", 30, 300, 200)
                h_val = st.number_input("Valor do Kit de Reposição (R$):", 100.0, 1500.0, 490.0)
                
            sub_h = st.form_submit_button("➕ Gravar Histórico de Compras no BigQuery")
            if sub_h:
                data_compra = (datetime.now() - timedelta(days=h_dias)).strftime("%Y-%m-%d")
                lead_id_m = df_leads[df_leads['nome_paciente'] == h_pac].iloc[0]['lead_id'] if not df_leads.empty else "LEAD-1001"
                novo_h = {
                    "historico_id": f"HIST-{2000 + len(df_hist) + 1}",
                    "lead_id": lead_id_m,
                    "nome_paciente": h_pac,
                    "data_compra_inicial": (datetime.now() - timedelta(days=h_dias+90)).strftime("%Y-%m-%d"),
                    "produto_sku": "CPAP-RES-AS11",
                    "mascara_sku": "MSK-RES-F20",
                    "data_ultima_troca_mascara": data_compra,
                    "dias_desde_troca_mascara": h_dias,
                    "status_adesao": "Adesão Alta",
                    "alerta_reposicao": "🚨 TROCA URGENTE: Silicone com mais de 6 meses" if h_dias>=180 else "⚠️ Manutenção Regular",
                    "valor_recorrente_estimado_brl": h_val
                }
                df_hist = pd.concat([df_hist, pd.DataFrame([novo_h])], ignore_index=True)
                df_hist.to_csv(os.path.join(DATA_DIR, "historico_compras_trocas.csv"), index=False)
                st.success(f"✅ Histórico adicionado para **{h_pac}** ({h_dias} dias de uso).")
                st.rerun()

# ==============================================================================
# MENU 3: INSPEÇÃO DE FONTES DE DADOS (BIGQUERY & STORAGE)
# ==============================================================================
elif "3. Inspeção" in menu:
    st.markdown('<div class="main-header">📊 Inspeção de Fontes de Dados (Data Source Hub)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Confira o catálogo de dados estruturados e não estruturados que alimentam as respostas do <b>Gemini Enterprise</b>.</div>', unsafe_allow_html=True)
    
    tab_bq, tab_gcs, tab_mcp = st.tabs([
        "📊 Tabelas do BigQuery (`luminar_saude`)",
        "🗄️ Arquivos no Cloud Storage (`gs://...`)",
        "🛠️ Ferramentas MCP & OpenAPI"
    ])
    
    with tab_bq:
        st.markdown("#### 1. Tabela: `leads_pacientes` (CRM e Parâmetros Clínicos)")
        st.dataframe(df_leads, use_container_width=True, hide_index=True)
        
        st.markdown("#### 2. Tabela: `catalogo_produtos` (CPAPs, BiPAPs e Máscaras)")
        st.dataframe(df_catalogo, use_container_width=True, hide_index=True)
        
        st.markdown("#### 3. Tabela: `historico_compras_trocas` (Recorrência de Insumos)")
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
    with tab_gcs:
        st.markdown("#### 📁 Documentos não estruturados indexados para busca multimodal pelo Gemini")
        
        laudos_files = glob.glob(os.path.join(STORAGE_DIR, "laudos_polissonografia", "*.*"))
        receitas_files = glob.glob(os.path.join(STORAGE_DIR, "receitas_medicas", "*.*"))
        manuais_files = glob.glob(os.path.join(STORAGE_DIR, "catalogos_manuais", "*.*"))
        
        st.markdown(f"**Laudos de Polissonografia:** `{len(laudos_files)} arquivos` | **Receitas Médicas:** `{len(receitas_files)} arquivos` | **Manuais Técnicos:** `{len(manuais_files)} arquivos`")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("##### 📄 Laudos Médicos Disponíveis:")
            for f in laudos_files:
                st.code(os.path.basename(f), language="text")
        with col_g2:
            st.markdown("##### 📄 Prescrições e Manuais:")
            for f in receitas_files + manuais_files:
                st.code(os.path.basename(f), language="text")
                
    with tab_mcp:
        st.markdown("#### 🛠️ Ferramentas MCP expostas pelo Cloud Run para o Gemini Enterprise")
        st.markdown("""
        | Nome da Tool | Finalidade | Endpoint HTTP |
        | :--- | :--- | :--- |
        | `consultar_paciente` | Busca IAH, SpO2, pressão titulada e histórico clínico | `GET /tools/consultar_paciente` |
        | `recomendar_produtos` | Matching clínico de CPAP, modelo de máscara e tubos | `GET /tools/recomendar_produtos` |
        | `gerar_pitch_vendas` | Geração de propostas com quebra de objeções para WhatsApp/Gmail | `GET /tools/gerar_pitch_vendas` |
        | `criar_novo_lead` | Injeta paciente na base e qualifica na hora | `POST /tools/criar_novo_lead` |
        """)
        st.markdown(f"**OpenAPI 3.0 Spec:** `/openapi.json` | **MCP Manifest:** `/mcp/manifest.json`")

# ==============================================================================
# MENU 4: CONEXÕES DO GEMINI ENTERPRISE & RESET DA BASE
# ==============================================================================
elif "4. Conexões" in menu:
    st.markdown('<div class="main-header">⚙️ Conexão com Gemini Enterprise & Gestão da Demo</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configurações de integração entre o repositório de dados e a interface do <b>Gemini Enterprise</b>.</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card-container">
        <h4 style="margin-top:0; color:#0369A1;">Como o Gemini Enterprise acessa estas fontes de dados:</h4>
        <ol style="color:#1E293B; line-height:1.8;">
            <li><b>Data Store (Cloud Storage):</b> O Gemini Enterprise utiliza o Data Store <code>luminar-saude-datastore</code> para indexar e realizar buscas semânticas nos PDFs de laudos médicos e manuais.</li>
            <li><b>Tabelas BigQuery:</b> As 4 tabelas do dataset <code>luminar_saude</code> são consultadas via BigQuery Data Agent / Search & Conversation.</li>
            <li><b>OpenAPI Tools (Cloud Run):</b> As operações dinâmicas (como cálculo de preço, matching de catálogo e disparo de proposta) são executadas chamando a API exposta pelo Cloud Run.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔄 Restauração da Base de Demonstração")
    st.markdown("Caso queira reiniciar a apresentação do zero e voltar para o estado padrão com os 5 pacientes de referência:")
    
    if st.button("🔄 Executar Reset Geral da Base de Dados", use_container_width=False):
        if reset_demo_data():
            st.success("✅ Base de demonstração restaurada com sucesso para o estado padrão!")
            st.rerun()
