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
    page_title="Luminar Saúde | QG da Demo & Copiloto IA de CPAP",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# DESIGN SYSTEM & ESTILIZAÇÃO CSS AVANÇADA
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 26px;
        font-weight: 800;
        color: #0A3D62;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sub-header {
        font-size: 14px;
        color: #4A6572;
        margin-bottom: 20px;
        font-weight: 400;
    }
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        border-color: #CBD5E1;
    }
    .scenario-box {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        border: 1px solid #BAE6FD;
        border-left: 5px solid #0284C7;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .scenario-title {
        font-weight: 700;
        color: #0369A1;
        font-size: 16px;
        margin-bottom: 4px;
    }
    .product-card {
        border-left: 4px solid #0284C7;
        background-color: #F8FAFC;
        padding: 14px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 12px;
        border: 1px solid #E2E8F0;
        border-left-width: 5px;
    }
    .gmail-box {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .gmail-sender {
        font-weight: bold;
        color: #202124;
    }
    .gmail-subject {
        color: #1A73E8;
        font-size: 15px;
        font-weight: 600;
    }
    .badge-urgent {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge-high {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge-medium {
        background-color: #E0F2FE;
        color: #075985;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CARGA E GESTÃO DE ESTADO DE DADOS
# ==============================================================================
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "bigquery", "data")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
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
    """Restaura a base de demonstração para o estado original."""
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
# MENU LATERAL & GERENCIADOR DA DEMO
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/lungs.png", width=55)
st.sidebar.title("Luminar Saúde")
st.sidebar.markdown("**Centro de Comando & QG da Demo**")
st.sidebar.caption("Google Cloud Project: `abiding-arch-505313-m3`")

menu = st.sidebar.radio(
    "Módulos de Navegação:",
    [
        "🎮 0. QG da Demo & Roteiro Interativo",
        "🪄 1. Gerador Avançado de Dados & Contexto",
        "🩺 2. Cockpit Comercial & Qualificação",
        "🎯 3. Copiloto de Recomendação (CPAP/Máscaras)",
        "🤖 4. Agent Platform & MCP Playground",
        "✉️ 5. Simulador Workspace (Gmail & Drive)",
        "🔄 6. Recorrência & LTV (Insumos)",
        "☁️ 7. Google Cloud Architecture"
    ]
)

st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Controle da Demonstração"):
    if st.button("🔄 Resetar Base da Demo (Padrão)", use_container_width=True):
        if reset_demo_data():
            st.success("Base restaurada com sucesso!")
            st.rerun()
    st.caption("Restaura os 5 pacientes padrão e limpa simulações extras.")

st.sidebar.info("""
**Status da Infraestrutura:**
- 🟢 **Cloud Run:** Ativo (Porta 8080)
- 🟢 **MCP Server:** `/mcp/manifest.json`
- 🟢 **BigQuery:** `luminar_saude`
- 🟢 **Cloud Storage:** Ativo
- 🟢 **Vertex AI Agent:** Ativo
""")

# ==============================================================================
# MENU 0: QG DA DEMO & ROTEIRO INTERATIVO
# ==============================================================================
if "0. QG da Demo" in menu:
    st.markdown('<div class="main-header">🎮 Centro de Comando & Roteiro da Demonstração</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Guia interativo passo a passo com falas sugeridas, pontos de clique e acionamento de cenários</div>', unsafe_allow_html=True)
    
    # Cards de Métricas Gerais da Demo
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total de Pacientes no CRM", len(df_leads), "+ Pronto para Apresentação")
    with m2:
        urgentes = len(df_leads[df_leads['urgencia_comercial'].isin(['URGENTE', 'ALTA'])]) if not df_leads.empty else 0
        pct = int(urgentes/len(df_leads)*100) if len(df_leads) > 0 else 0
        st.metric("Casos de Alta Gravidade", f"{urgentes} leads", f"{pct}% da carteira")
    with m3:
        st.metric("Produtos no Catálogo", len(df_catalogo) if not df_catalogo.empty else 12, "CPAP, BiPAP, Máscaras")
    with m4:
        st.metric("Tempo Médio de Atendimento", "2.5 min", "-78% com Gemini")
        
    st.markdown("---")
    st.subheader("🧭 Roteiro Oficial da Apresentação (5 Atos)")
    
    # ATO 1
    with st.expander("📍 **ATO 1: O Desafio do Negócio (1 a 2 min)** — O Vendedor & A Complexidade Médica", expanded=True):
        st.markdown("""
        <div class="scenario-box">
            <div class="scenario-title">🎯 Objetivo: Conectar o público com o problema real de vendas de saúde</div>
            <p><b>Narrativa do Apresentador:</b><br/>
            <i>"Na medicina respiratória e do sono, o consultor não vende apenas um produto, ele vende uma terapia médica. 
            Quando um paciente chega com um laudo de polissonografia, há termos complexos: IAH, saturação de oxigênio mínima, pressão em cmH2O. 
            Traduzir isso no equipamento ideal, na máscara correta e quebrar o medo de claustrofobia demorava dias. 
            Com o Copiloto de IA da Luminar Saúde, o vendedor fecha em minutos com total segurança médica."</i></p>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 **Ação recomendada:** Explique o contexto antes de mudar de tela ou avance para o Cockpit.")
        
    # ATO 2
    with st.expander("📍 **ATO 2: Cockpit Comercial & Laudos Multimodais (3 min)** — Visão Geral & Extração de PDF", expanded=True):
        st.markdown("""
        <div class="scenario-box">
            <div class="scenario-title">🎯 O que mostrar: Triagem instantânea e leitura multimodal de PDF no Cloud Storage</div>
            <ul>
                <li><b>Onde clicar:</b> Menu Lateral 👉 <code>2. Cockpit Comercial & Qualificação</code></li>
                <li><b>Paciente Destaque:</b> Selecione <b>Roberto Silveira Santos</b> (IAH 38.4, Apneia Grave, Respirador Bucal).</li>
                <li><b>O que enfatizar:</b> O laudo em PDF foi lido diretamente do Cloud Storage e os parâmetros clínicos foram estruturados no BigQuery sem digitação humana.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<b>Mensagem de Impacto:</b> *'O Gemini estruturou o laudo médico em milissegundos, alertando o risco de saúde e a urgência comercial.'*")
        
    # ATO 3
    with st.expander("📍 **ATO 3: Matching Clínico & Quebra de Objeções (3 min)** — O Copiloto de Vendas", expanded=True):
        st.markdown("""
        <div class="scenario-box">
            <div class="scenario-title">🎯 O que mostrar: O pacote inteligente, o racional médico e os scripts comerciais</div>
            <ul>
                <li><b>Onde clicar:</b> Menu Lateral 👉 <code>3. Copiloto de Recomendação (CPAP/Máscaras)</code></li>
                <li><b>Pontos-chave:</b>
                    <ol>
                        <li><b>Equipamento:</b> ResMed AirSense 11 AutoSet (com alívio expiratório).</li>
                        <li><b>Máscara:</b> ResMed AirFit F20 Facial (indispensável para quem respira pela boca e tem pressão de 12 cmH2O).</li>
                        <li><b>Cross-Sell:</b> Tubo aquecido ClimateLineAir para evitar ressecamento.</li>
                        <li><b>Quebra de Objeções:</b> Argumento pronto do programa <i>'Luminar Adaptação 30 Dias'</i>.</li>
                    </ol>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<b>Mensagem de Impacto:</b> *'Zero erro de compatibilidade de produtos e aumento imediato do ticket médio com cross-sell.'*")
        
    # ATO 4
    with st.expander("📍 **ATO 4: Injeção de Dados em Tempo Real (Live Lead Simulator) (3 min)**", expanded=True):
        st.markdown("""
        <div class="scenario-box">
            <div class="scenario-title">🎯 O que mostrar: A IA reagindo instantaneamente a novos clientes ao vivo</div>
            <ul>
                <li><b>Onde clicar:</b> Menu Lateral 👉 <code>1. Gerador Avançado de Dados & Contexto</code></li>
                <li><b>Ação ao vivo:</b> Clique em um dos botões de 1-Clique (ex: <i>'🤧 Paciente Rinite & Claustrofobia'</i> ou <i>'✈️ Executivo Viagem'</i>).</li>
                <li><b>Retorno:</b> Volte ao Cockpit e mostre que a paciente foi qualificada e a IA montou a recomendação da Máscara P10 de 45g na hora!</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<b>Mensagem de Impacto:</b> *'Qualquer nova receita que entra por WhatsApp ou formulário web é qualificada e encaminhada em tempo real.'*")
        
    # ATO 5
    with st.expander("📍 **ATO 5: Vertex AI Agent Platform & Recorrência LTV (3 min)**", expanded=True):
        st.markdown("""
        <div class="scenario-box">
            <div class="scenario-title">🎯 O que mostrar: O ecossistema de Agentes com MCP Tools e receita recorrente</div>
            <ul>
                <li><b>Onde clicar:</b> Menu Lateral 👉 <code>4. Agent Platform & MCP Playground</code> e <code>6. Recorrência & LTV</code></li>
                <li><b>Teste no Agent:</b> Faça a pergunta sobre CPAP vs BiPAP para o paciente Carlos Eduardo (pressão 15 cmH2O).</li>
                <li><b>LTV:</b> Mostre como o sistema detecta almofadas de silicone com mais de 6 meses e envia lembrete proativo de troca.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<b>Mensagem de Impacto:</b> *'+35% de conversão de vendas, +22% de receita recorrente de insumos e ciclo comercial reduzido de semanas para minutos.'*")

# ==============================================================================
# MENU 1: GERADOR AVANÇADO DE DADOS & CONTEXTO (SYNTHETIC CONTEXT GENERATOR)
# ==============================================================================
elif "1. Gerador" in menu:
    st.markdown('<div class="main-header">🪄 Gerador de Dados Sintéticos & Criador de Contextos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Crie pacientes, laudos, histórico de compras, queixas e cenários contextuais sob medida para a demonstração</div>', unsafe_allow_html=True)
    
    tab_leads_gen, tab_custom_scenario, tab_hist_gen = st.tabs([
        "⚡ Injeção Rápida de Cenários (1-Clique)",
        "📝 Gerador Completo de Lead & Contexto Clínico",
        "🔄 Gerador de Histórico de Compras (LTV)"
    ])
    
    # ABA 1: CENÁRIOS RÁPIDOS 1-CLIQUE
    with tab_leads_gen:
        st.subheader("⚡ Injeção Instantânea de Cenários Pré-Configurados")
        st.markdown("Clique em qualquer cenário abaixo para injetar o paciente no BigQuery e gerar seus laudos e recomendações na hora:")
        
        c1, c2 = st.columns(2)
        
        with c1:
            with st.container():
                st.markdown("""
                <div class="scenario-box">
                    <div class="scenario-title">🚨 1. Apneia Crítica com Risco Cardiovascular</div>
                    <b>Perfil:</b> Homem, 58 anos, obeso, pressão de titulação alta (14 cmH2O), respiração bucal.<br/>
                    <b>Queixas:</b> Acorda sufocado, sonolência severa ao volante, pressão arterial descontrolada.<br/>
                    <b>Indicação IA:</b> CPAP AutoSet + Máscara Facial F20 + Tubo Aquecido.
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚀 Injetar Cenário: Apneia Crítica (Eduardo Brandão)", use_container_width=True):
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
                    st.success(f"✅ Lead {novo_id} (Eduardo Brandão) cadastrado com sucesso! Veja no Cockpit.")
                    st.rerun()

            with st.container():
                st.markdown("""
                <div class="scenario-box">
                    <div class="scenario-title">✈️ 2. Executivo de Viagens (Busca CPAP Ultracompacto)</div>
                    <b>Perfil:</b> Homem, 44 anos, viaja semanalmente, ronco em hotéis e cansaço diurno.<br/>
                    <b>Dúvidas/Objeções:</b> <i>'Não posso carregar um aparelho pesado na mala de mão.'</i><br/>
                    <b>Indicação IA:</b> ResMed AirMini Portátil + Máscara Nasal N30 + Bateria Externa.
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚀 Injetar Cenário: Executivo Viagem (Marcelo Guimarães)", use_container_width=True):
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
                        "comorbidades": "Viagens semanais aéreas frequentes",
                        "sensibilidade_pressao": "Baixa",
                        "score_prioridade": 82,
                        "urgencia_comercial": "MEDIA",
                        "status_funil": "Qualificado - Lead Live Demo",
                        "data_entrada": datetime.now().strftime("%Y-%m-%d")
                    }
                    df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
                    df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
                    st.success(f"✅ Lead {novo_id} (Marcelo Guimarães) injetado com sucesso! Recomendado AirMini.")
                    st.rerun()

        with c2:
            with st.container():
                st.markdown("""
                <div class="scenario-box">
                    <div class="scenario-title">🤧 3. Rinite Alérgica & Pânico de Claustrofobia</div>
                    <b>Perfil:</b> Mulher, 39 anos, respiração nasal, queixa de sufocamento com máscaras grandes.<br/>
                    <b>Dúvidas/Objeções:</b> <i>'Tenho aflição de colocar algo cobrindo todo o meu rosto.'</i><br/>
                    <b>Indicação IA:</b> Máscara de Almofadas Nasais AirFit P10 (45g) + Filtros Hipoalergênicos.
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚀 Injetar Cenário: Rinite & Claustrofobia (Juliana Silveira)", use_container_width=True):
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
                    st.success(f"✅ Lead {novo_id} (Juliana Silveira) injetada com sucesso! Recomendado AirFit P10.")
                    st.rerun()

            with st.container():
                st.markdown("""
                <div class="scenario-box">
                    <div class="scenario-title">🫀 4. Cardiopata com Pressão Alta (Indicação de BiPAP)</div>
                    <b>Perfil:</b> Homem, 67 anos, arritmia cardíaca, pressão de titulação muito alta (16 cmH2O).<br/>
                    <b>Racional Clínico:</b> CPAP convencional causaria sobrecarga expiratória e cansaço diafragma.<br/>
                    <b>Indicação IA:</b> ResMed AirCurve 10 VAuto (BiPAP) com pressão binível.
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚀 Injetar Cenário: Cardiopata BiPAP (Alvaro Ramos)", use_container_width=True):
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
                    st.success(f"✅ Lead {novo_id} (Alvaro Ramos) cadastrado com sucesso! Recomendado BiPAP.")
                    st.rerun()

    # ABA 2: FORMULÁRIO COMPLETO COM CONTEXTO E OBJEÇÕES
    with tab_custom_scenario:
        st.subheader("📝 Gerador Customizado de Lead com Contexto de Vendas & Objeções")
        st.markdown("Preencha as informações clínicas, o perfil do cliente e as perguntas/objeções dele para gerar uma qualificação completa:")
        
        with st.form("form_custom_lead"):
            fc1, fc2, fc3 = st.columns(3)
            
            with fc1:
                st.markdown("##### 👤 1. Dados Pessoais e Cadastrais")
                c_nome = st.text_input("Nome do Paciente", "Dr. Maurício Becker")
                c_idade = st.number_input("Idade", 18, 95, 51)
                c_genero = st.selectbox("Gênero", ["M", "F"])
                c_tel = st.text_input("WhatsApp / Telefone", "(11) 98765-4321")
                c_cidade = st.text_input("Cidade/UF", "São Paulo/SP")
                c_convenio = st.selectbox("Convênio / Pagamento", ["Bradesco Saúde", "SulAmérica", "Amil One", "Unimed", "Particular / PIX"])
                
            with fc2:
                st.markdown("##### 🫁 2. Parâmetros Clínicos & Polissonografia")
                c_iah = st.number_input("IAH (Eventos por Hora)", 1.0, 120.0, 36.4, help=">= 30 é Grave, 15-30 Moderada, <15 Leve")
                c_spo2 = st.number_input("SpO2 Mínima (%)", 50.0, 99.0, 75.0)
                c_pressao = st.number_input("Pressão Titulada em cmH2O", 4.0, 25.0, 11.5)
                c_padrao_resp = st.selectbox("Padrão Respiratório", ["Oral / Mista (Respira pela boca)", "Nasal (Respira pelo nariz)", "Exclusivamente Bucal"])
                c_medico = st.text_input("Médico Prescritor", "Dr. Fernando Albuquerque (CRM-SP 142.890)")
                c_comorb = st.text_input("Comorbidades / Sintomas", "Hipertensão, Sonolência Diurna, Ronco Alto")
                
            with fc3:
                st.markdown("##### 💭 3. Contexto Comercial & Objeções do Paciente")
                c_interesse = st.selectbox("Nível de Interesse do Cliente", ["🔥 Urgência Máxima (Quer comprar hoje)", "⚡ Alto Interesse (Pediu orçamento)", "❄️ Com Receio / Muitas Objeções"])
                c_objecao = st.selectbox(
                    "Principal Objeção / Dúvida do Cliente:",
                    [
                        "Claustrofobia: 'Tenho medo de me sentir sufocado com a máscara'",
                        "Ruído: 'Minha esposa tem sono leve e tenho medo do barulho do aparelho'",
                        "Preço / Condição: 'Achei o valor elevado, preciso parcelar em 12x'",
                        "Adaptação: 'E se eu comprar e não conseguir me acostumar a dormir com isso?'",
                        "Plano de Saúde: 'Meu convênio não reembolsa o equipamento?'"
                    ]
                )
                c_perguntas = st.text_area(
                    "Pergunta específica feita pelo cliente no WhatsApp:",
                    "Olá, o médico me passou o laudo com IAH 36, mas tenho medo de não me acostumar com a máscara. Vocês deixam testar antes?",
                    height=100
                )
                
            btn_sub = st.form_submit_button("🚀 Gerar Lead, Criar Laudo no Storage & Calcular Recomendação IA", use_container_width=True)
            
            if btn_sub:
                novo_id = f"LEAD-{1000 + len(df_leads) + 1}"
                is_oral = "oral" in c_padrao_resp.lower() or "bucal" in c_padrao_resp.lower()
                
                # Gera laudo em TXT na pasta de storage
                first_name = c_nome.split()[0].lower()
                last_name = c_nome.split()[-1].lower()
                laudo_txt_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", f"laudo_psg_{first_name}_{last_name}.txt")
                
                laudo_content = f"""CLÍNICA DE MEDICINA DO SONO E DIAGNÓSTICO RESPIRATÓRIO
LAUDO DE POLISSONOGRAFIA DE NOITE INTEIRA (PSG)
--------------------------------------------------------------------------------
PACIENTE: {c_nome} | IDADE: {c_idade} anos | DATA: {datetime.now().strftime('%d/%m/%Y')}
MÉDICO RESPONSÁVEL: {c_medico}

PARÂMETROS REGISTRADOS:
- Tempo Total de Registro: 460 minutos
- Eficiência do Sono: 79.4%
- Índice de Apneia e Hipopneia (IAH): {c_iah} eventos/hora ({'GRAVE' if c_iah>=30 else ('MODERADA' if c_iah>=15 else 'LEVE')})
- Saturação Mínima de O2 (SpO2): {c_spo2}%
- Dessaturações registradas: 142 episódios
- Padrão Respiratório: {c_padrao_resp}
- Pressão Titulada Recomendada: {c_pressao} cmH2O
- Comorbidades: {c_comorb}

CONCLUSÃO DIAGNÓSTICA:
Quadro compatível com Síndrome da Apneia Obstrutiva do Sono (SAOS).
Prescrição de terapia por pressão positiva contínua (CPAP) com titulação automática.
Interface recomendada de acordo com o padrão respiratório do paciente.
"""
                with open(laudo_txt_path, "w", encoding="utf-8") as f:
                    f.write(laudo_content)
                    
                score = 95 if c_iah >= 30 else (85 if c_iah >= 15 else 70)
                urgencia = "URGENTE" if c_iah >= 35 else ("ALTA" if c_iah >= 20 else "MEDIA")
                
                novo_dict = {
                    "lead_id": novo_id,
                    "nome_paciente": c_nome,
                    "idade": c_idade,
                    "genero": c_genero,
                    "telefone": c_tel,
                    "email": f"{first_name}.{last_name}@email.com",
                    "cidade": c_cidade.split("/")[0],
                    "estado": c_cidade.split("/")[-1] if "/" in c_cidade else "SP",
                    "medico_prescritor": c_medico.split("(")[0].strip(),
                    "crm_medico": c_medico.split("(")[-1].replace(")", "") if "(" in c_medico else "CRM-SP 142.890",
                    "especialidade_medico": "Pneumologia e Medicina do Sono",
                    "convenio": c_convenio,
                    "diagnostico_cid": f"G47.3 - Apneia Obstrutiva do Sono ({'Grave' if c_iah >= 30 else 'Moderada'})",
                    "iah": c_iah,
                    "spo2_minima": c_spo2,
                    "spo2_media": 92.0,
                    "pressao_titulada_cmh2o": c_pressao,
                    "respiracao_predominante": c_padrao_resp,
                    "presenca_ronco": "Alto / Frequente",
                    "comorbidades": f"{c_comorb} | Objeção: {c_objecao.split(':')[0]}",
                    "sensibilidade_pressao": "Alta" if c_pressao >= 12 else "Média",
                    "score_prioridade": score,
                    "urgencia_comercial": urgencia,
                    "status_funil": f"Qualificado - {c_interesse.split()[0]}",
                    "data_entrada": datetime.now().strftime("%Y-%m-%d")
                }
                
                df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
                df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
                
                st.success(f"🎉 Lead **{novo_id} ({c_nome})** criado com sucesso e laudo gravado no Cloud Storage!")
                st.info(f"💡 **Recomendação Calculada:** Equipamento com pressão de {c_pressao} cmH2O e máscara {'Facial Full Face' if is_oral or c_pressao >= 12 else 'Nasal / Pillow'}. Veja no Cockpit!")
                st.rerun()

    # ABA 3: HISTÓRICO DE COMPRAS (RECORRÊNCIA E LTV)
    with tab_hist_gen:
        st.subheader("🔄 Gerador de Histórico de Compras & Recorrência de Insumos")
        st.markdown("Adicione compras simuladas para pacientes com datas retroativas para gerar alertas automáticos de troca de máscara e filtros:")
        
        with st.form("form_hist_compra"):
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                h_paciente = st.selectbox("Selecione o Paciente Existente:", df_leads['nome_paciente'].tolist() if not df_leads.empty else ["Roberto Silveira Santos"])
                h_equip = st.selectbox("Equipamento Comprado Anteriormente:", ["CPAP-RES-AS11 - ResMed AirSense 11", "CPAP-RES-AS10 - ResMed AirSense 10", "BIPAP-RES-AC10 - ResMed AirCurve 10"])
                h_mask = st.selectbox("Máscara Utilizada:", ["MSK-RES-F20 - AirFit F20 Full Face", "MSK-RES-N20 - AirFit N20 Nasal", "MSK-RES-P10 - AirFit P10 Pillow"])
            with h_col2:
                h_dias = st.slider("Dias desde a última troca de almofada de silicone:", 30, 360, 210)
                h_valor = st.number_input("Valor Estimado do Kit de Reposição (R$):", 100.0, 1500.0, 480.0)
                
            sub_h = st.form_submit_button("➕ Injetar Registro de Recorrência no BigQuery")
            if sub_h:
                data_compra = (datetime.now() - timedelta(days=h_dias)).strftime("%Y-%m-%d")
                lead_id_match = df_leads[df_leads['nome_paciente'] == h_paciente].iloc[0]['lead_id'] if not df_leads.empty else "LEAD-1001"
                
                novo_hist = {
                    "historico_id": f"HIST-{2000 + len(df_hist) + 1}",
                    "lead_id": lead_id_match,
                    "nome_paciente": h_paciente,
                    "data_compra_inicial": (datetime.now() - timedelta(days=h_dias+90)).strftime("%Y-%m-%d"),
                    "produto_sku": h_equip.split(" - ")[0],
                    "mascara_sku": h_mask.split(" - ")[0],
                    "data_ultima_troca_mascara": data_compra,
                    "dias_desde_troca_mascara": h_dias,
                    "status_adesao": "Adesão Alta (Uso > 6h/noite)",
                    "alerta_reposicao": "🚨 TROCA URGENTE: Silicone com mais de 6 meses" if h_dias >= 180 else "⚠️ Manutenção Periódica",
                    "valor_recorrente_estimado_brl": h_valor
                }
                
                df_hist = pd.concat([df_hist, pd.DataFrame([novo_hist])], ignore_index=True)
                df_hist.to_csv(os.path.join(DATA_DIR, "historico_compras_trocas.csv"), index=False)
                st.success(f"✅ Histórico adicionado para **{h_paciente}** ({h_dias} dias de uso). Veja na aba Recorrência!")
                st.rerun()

# ==============================================================================
# MENU 2: COCKPIT COMERCIAL & QUALIFICAÇÃO
# ==============================================================================
elif "2. Cockpit" in menu:
    st.markdown('<div class="main-header">🩺 Cockpit Comercial & Triagem de Pacientes</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Qualificação automática de prescrições médicas e laudos polissonográficos via Gemini</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Pacientes no CRM", len(df_leads), "+ Base ao Vivo")
    with col2:
        urgentes = len(df_leads[df_leads['urgencia_comercial'].isin(['URGENTE', 'ALTA'])]) if not df_leads.empty else 0
        pct = int(urgentes/len(df_leads)*100) if len(df_leads) > 0 else 0
        st.metric("Prioridade Alta / Crítica", f"{urgentes} leads", f"{pct}% da base")
    with col3:
        st.metric("Ticket Médio c/ Cross-Sell", "R$ 6.945,00", "+22% rentabilidade")
    with col4:
        st.metric("Ciclo Comercial Médio", "1.8 dias", "-55% c/ IA")

    st.markdown("---")
    st.subheader("📋 Fila de Leads Qualificados em Tempo Real")
    
    if not df_leads.empty:
        display_df = df_leads[['lead_id', 'nome_paciente', 'idade', 'convenio', 'diagnostico_cid', 'iah', 'spo2_minima', 'pressao_titulada_cmh2o', 'respiracao_predominante', 'urgencia_comercial', 'score_prioridade']].copy()
        display_df.columns = ['ID Lead', 'Paciente', 'Idade', 'Convênio', 'Diagnóstico CID', 'IAH (ev/h)', 'SpO2 Mín (%)', 'Pressão cmH2O', 'Respiração', 'Urgência', 'Score IA']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Inspeção de Laudo Clínico e Parâmetros Polissonográficos")
        
        selected_name = st.selectbox("Selecione o paciente:", df_leads['nome_paciente'].tolist())
        p_info = df_leads[df_leads['nome_paciente'] == selected_name].iloc[0]
        
        c_left, c_right = st.columns([1.2, 1])
        
        with c_left:
            st.markdown(f"### 🫁 Ficha Médica: **{p_info['nome_paciente']}** ({p_info['lead_id']})")
            st.markdown(f"""
            - **Idade / Gênero:** {p_info['idade']} anos ({p_info['genero']})
            - **Contato:** {p_info['telefone']} | {p_info['email']}
            - **Cidade/Estado:** {p_info['cidade']}/{p_info['estado']}
            - **Médico Prescritor:** {p_info['medico_prescritor']} ({p_info['crm_medico']})
            - **Convênio / Plano:** {p_info['convenio']}
            - **Comorbidades:** `{p_info['comorbidades']}`
            """)
            
            iah = float(p_info['iah'])
            if iah >= 30:
                st.error(f"🚨 **Apneia Obstrutiva do Sono Grave (IAH: {iah} ev/h)**: Dessaturação de oxigênio crítica até **{p_info['spo2_minima']}%**. Risco cardiovascular iminente. Exige abordagem comercial em menos de 2 horas.")
            elif iah >= 15:
                st.warning(f"⚠️ **Apneia Obstrutiva Moderada (IAH: {iah} ev/h)**: SpO2 mínima de {p_info['spo2_minima']}%. Indicação de CPAP Auto.")
            else:
                st.info(f"ℹ️ **Apneia Leve (IAH: {iah} ev/h)**: Foco em conforto respiratório e eliminação do ronco.")

        with c_right:
            st.markdown("### 📄 Extração Multimodal do Laudo (PDF no Cloud Storage)")
            first_name = p_info['nome_paciente'].split()[0].lower()
            last_name = p_info['nome_paciente'].split()[-1].lower()
            txt_filename = f"laudo_psg_{first_name}_{last_name}.txt"
            txt_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", txt_filename)
            
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                st.text_area("Extrato do Laudo Polissonográfico Processado por IA:", content, height=180)
            else:
                st.info(f"Laudo gerado dinamicamente para {p_info['nome_paciente']} (IAH {p_info['iah']}, Pressão {p_info['pressao_titulada_cmh2o']} cmH2O).")
                
            pdf_filename = f"laudo_psg_{first_name}_{last_name}.pdf"
            pdf_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", pdf_filename)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f_pdf:
                    st.download_button(
                        label=f"📥 Baixar Laudo Clínico Original em PDF",
                        data=f_pdf,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )

# ==============================================================================
# MENU 3: COPILOTO DE RECOMENDAÇÃO DE CPAP
# ==============================================================================
elif "3. Copiloto" in menu:
    st.markdown('<div class="main-header">🎯 Copiloto de Recomendação de Produtos & Quebra de Objeções</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Matching automatizado entre padrão respiratório, pressão prescrita e catálogo de CPAPs/Máscaras</div>', unsafe_allow_html=True)
    
    if not df_leads.empty:
        lead_select = st.selectbox("Selecione o Lead / Paciente:", df_leads['nome_paciente'].tolist())
        lead_row = df_leads[df_leads['nome_paciente'] == lead_select].iloc[0]
        
        # Busca na tabela de recomendação ou calcula dinamicamente
        rec_match = df_rec[df_rec['lead_id'] == lead_row['lead_id']] if not df_rec.empty else pd.DataFrame()
        
        if not rec_match.empty:
            rec = rec_match.iloc[0]
            equip_nome = rec['equipamento_principal_nome']
            equip_sku = rec['equipamento_principal_sku']
            mask_nome = rec['mascara_recomendada_nome']
            mask_sku = rec['mascara_recomendada_sku']
            cross_sell = rec['insumos_cross_sell']
            valor_total = float(rec['valor_total_pacote_brl'])
            condicao = rec['condicao_comercial_sugerida']
            argumento = rec['argumentacao_venda_ia']
            objecoes = rec['quebra_objecoes']
            prob = float(rec['probabilidade_conversao'])
        else:
            # Fallback dinâmico
            is_oral = "oral" in str(lead_row.get("respiracao_predominante", "")).lower() or "bucal" in str(lead_row.get("respiracao_predominante", "")).lower()
            pressao = float(lead_row.get("pressao_titulada_cmh2o", 10.0))
            if pressao > 14:
                equip_nome, equip_sku, eq_preco = "ResMed AirCurve 10 VAuto (BiPAP)", "BIPAP-RES-AC10", 9800.0
            else:
                equip_nome, equip_sku, eq_preco = "ResMed AirSense 11 AutoSet", "CPAP-RES-AS11", 5890.0
                
            if is_oral or pressao >= 12:
                mask_nome, mask_sku, mk_preco = "AirFit F20 Full Face (Facial)", "MSK-RES-F20", 890.0
            else:
                mask_nome, mask_sku, mk_preco = "AirFit N20 Nasal Compacta", "MSK-RES-N20", 690.0
                
            cross_sell = "Tubo Aquecido ClimateLineAir + Kit Filtros Hipoalergênicos + Lenços CPAP Wipes"
            valor_total = eq_preco + mk_preco + 390.0 + 150.0 + 75.0
            condicao = f"12x de R$ {valor_total/12:.2f} sem juros ou 8% desc. no PIX (R$ {valor_total*0.92:.2f})"
            argumento = f"Paciente com pressão de {pressao} cmH2O e respiração {lead_row.get('respiracao_predominante')}. Indicação direta do {equip_nome} com alívio expiratório e máscara {mask_nome} para evitar fuga aérea."
            objecoes = "Reforçar o programa 'Luminar Adaptação 30 Dias' (troca grátis de modelo de máscara caso sinta desconforto)."
            prob = 0.92

        col_l, col_r = st.columns([1.3, 1])
        
        with col_l:
            st.markdown(f"### 💡 Pacote Recomendado para **{lead_row['nome_paciente']}**")
            
            st.markdown(f"""
            <div class="product-card">
                <h4 style="color:#0369A1; margin:0;">1. Equipamento Principal: {equip_nome}</h4>
                <p style="margin:2px 0 0 0;"><b>Código SKU:</b> <code>{equip_sku}</code> | Conectividade 4G AirView</p>
            </div>
            <div class="product-card">
                <h4 style="color:#0D9488; margin:0;">2. Interface / Máscara: {mask_nome}</h4>
                <p style="margin:2px 0 0 0;"><b>Código SKU:</b> <code>{mask_sku}</code> | Silicone Ultra Confortável</p>
            </div>
            <div class="product-card">
                <h4 style="color:#16A34A; margin:0;">3. Insumos Cross-Sell & Acessórios</h4>
                <p style="margin:2px 0 0 0;">{cross_sell}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🧠 Racional Clínico-Comercial da IA")
            st.info(argumento)
            
            st.markdown("#### 🛡️ Quebra de Objeções para o Consultor")
            st.warning(f"**Como converter a venda:**\n\n{objecoes}")

        with col_r:
            st.markdown("### 💰 Proposta Comercial & Conversão")
            st.metric("Valor Total do Pacote", f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.metric("Probabilidade de Conversão IA", f"{int(prob*100)}%", "+28% acima do canal padrão")
            
            st.markdown("#### 💳 Condições de Pagamento")
            st.success(f"**Opções Comerciais:**\n\n{condicao}")
            
            st.markdown("#### ⚡ Ações Rápidas")
            if st.button("📲 Disparar Proposta no WhatsApp", use_container_width=True):
                st.toast(f"Proposta enviada para {lead_row['telefone']}!")
            if st.button("📧 Gerar E-mail Formal (Gmail)", use_container_width=True):
                st.toast(f"E-mail rascunhado para {lead_row['email']}!")
            if st.button("📁 Salvar Dossier no Google Drive", use_container_width=True):
                st.toast("Dossier do paciente salvo no Drive corporativo!")

# ==============================================================================
# MENU 4: AGENT PLATFORM & MCP PLAYGROUND
# ==============================================================================
elif "4. Agent Platform" in menu:
    st.markdown('<div class="main-header">🤖 Agent Platform & MCP Tools Playground</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Integração do Gemini via Model Context Protocol (MCP) com as ferramentas clínicas e comerciais</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Este ambiente simula o **Vertex AI Agent Builder / Agent Platform** conectado ao MCP Server da Luminar Saúde.
    As ferramentas abaixo são chamadas autonomamente pelo modelo para responder às dúvidas do vendedor.
    """)
    
    tab_chat, tab_tools, tab_manifest = st.tabs(["💬 Chat com o Copiloto Comercial", "🛠️ Ferramentas MCP Disponíveis", "📋 Manifest & OpenAPI"])
    
    with tab_chat:
        st.subheader("Interaja com o Copiloto de Vendas da Luminar Saúde")
        
        exemplo_pergunta = st.selectbox(
            "Perguntas Rápidas de Exemplo:",
            [
                "Qual é o diagnóstico e a pressão recomendada para o paciente Roberto Silveira Santos?",
                "Qual combo de CPAP e máscara devo oferecer para a paciente Mariana Costa e por que?",
                "O paciente Carlos Eduardo tem pressão de 15 cmH2O e queixa de cansaço. Devo indicar CPAP ou BiPAP?",
                "Gere um script de WhatsApp para fechar a venda com o paciente Roberto Silveira."
            ]
        )
        
        user_query = st.text_input("Ou digite sua pergunta para o Agent:", exemplo_pergunta)
        
        if st.button("Enviar para o Gemini Agent"):
            with st.spinner("O Agent está consultando o MCP Server e BigQuery..."):
                if "Roberto" in user_query:
                    st.markdown("""
                    **🤖 Resposta do Agent (Vertex AI Gemini 1.5):**
                    
                    > 🔎 **Tool Executada:** `consultar_paciente(lead_id="LEAD-1001")`  
                    > 🔎 **Tool Executada:** `recomendar_produtos(lead_id="LEAD-1001")`
                    
                    Olá! O paciente **Roberto Silveira Santos** (52 anos) possui **Apneia Obstrutiva Grave (IAH: 38.4 eventos/hora)** com SpO2 mínima de 74%.
                    
                    **Conduta recomendada pela IA:**
                    1. **Equipamento:** ResMed AirSense 11 AutoSet (com alívio expiratório EPR no nível 3).
                    2. **Máscara:** ResMed AirFit F20 Full Face (Tamanho G). Como ele é respirador oral e a pressão titulada é **12 cmH2O**, a máscara facial é estritamente necessária para evitar escape de ar pela boca.
                    3. **Acessório Obrigatório:** Tubo Aquecido ClimateLineAir para evitar ressecamento da via aérea.
                    4. **Valor do Pacote:** R$ 7.345,00 (12x de R$ 612,08 sem juros).
                    """)
                elif "Mariana" in user_query:
                    st.markdown("""
                    **🤖 Resposta do Agent (Vertex AI Gemini 1.5):**
                    
                    > 🔎 **Tool Executada:** `consultar_paciente(lead_id="LEAD-1002")`  
                    > 🔎 **Tool Executada:** `recomendar_produtos(lead_id="LEAD-1002")`
                    
                    A paciente **Mariana Costa Andrade** tem **Apneia Moderada (IAH: 21.2)** com pressão titulada de **8.5 cmH2O**.
                    
                    **Recomendação Personalizada:**
                    - **Equipamento:** ResMed AirSense 10 AutoSet 4G.
                    - **Máscara:** AirFit P10 (Almofadas Nasais ultraleves de apenas 45g). Como a paciente relata **claustrofobia** e respira pelo nariz, a P10 elimina a sensação de sufocamento.
                    - **Cross-Sell:** Kit de Filtros Hipoalergênicos (ela tem rinite alérgica crônica).
                    """)
                elif "Carlos" in user_query or "BiPAP" in user_query:
                    st.markdown("""
                    **🤖 Resposta do Agent (Vertex AI Gemini 1.5):**
                    
                    > 🔎 **Tool Executada:** `consultar_paciente(lead_id="LEAD-1003")`
                    
                    Para o paciente **Carlos Eduardo Paes**, a indicação correta é o **BiPAP (AirCurve 10 VAuto)** pelos seguintes motivos clínicos:
                    1. A pressão prescrita é muito alta (**15 cmH2O**), o que causa alta resistência para expirar em CPAPs comuns.
                    2. Ele possui **comorbidade cardíaca** (arritmia e insuficiência leve) e IAH crítico (46.0). O BiPAP reduz o trabalho cardíaco durante o sono.
                    """)
                else:
                    st.markdown("""
                    **🤖 Resposta do Agent (Vertex AI Gemini 1.5):**
                    
                    > 🔎 **Tool Executada:** `gerar_pitch_vendas(lead_id="LEAD-1001", canal="whatsapp")`
                    
                    **Mensagem formatada para o WhatsApp do paciente:**
                    
                    ```text
                    Olá, Roberto! Tudo bem? Aqui é o consultor da Luminar Saúde.
                    Recebemos o encaminhamento do Dr. Fernando Albuquerque para o seu tratamento de sono.
                    
                    Montamos seu kit exclusivo com o silencioso ResMed AirSense 11 e a máscara AirFit F20, 
                    com o programa "Luminar Adaptação 30 Dias" (troca grátis de modelo se não se adaptar).
                    
                    Podemos agendar a visita do nosso fisioterapeuta na sua casa hoje às 16h?
                    ```
                    """)
                    
    with tab_tools:
        st.markdown("""
        ### Ferramentas MCP Registradas no Agent:
        
        | Nome da Tool | Finalidade | Endpoint HTTP |
        | :--- | :--- | :--- |
        | `consultar_paciente` | Busca dados do laudo, IAH, SpO2 e pressão | `GET /tools/consultar_paciente` |
        | `recomendar_produtos` | Matching clínico de CPAP, máscara e tubos | `GET /tools/recomendar_produtos` |
        | `gerar_pitch_vendas` | Copywriting empático para WhatsApp e e-mail | `GET /tools/gerar_pitch_vendas` |
        | `criar_novo_lead` | Injeta paciente na base e qualifica na hora | `POST /tools/criar_novo_lead` |
        """)
        
    with tab_manifest:
        st.subheader("Manifest JSON do MCP Server (`/mcp/manifest.json`)")
        manifest_data = {
            "schema_version": "v1",
            "name_for_model": "luminar_saude_sales_copilot",
            "description": "Ferramentas para medicina do sono, prescrições de CPAP e recomendações comerciais Luminar Saúde.",
            "tools": ["consultar_paciente", "recomendar_produtos", "gerar_pitch_vendas", "criar_novo_lead"]
        }
        st.json(manifest_data)

# ==============================================================================
# MENU 5: SIMULADOR WORKSPACE (GMAIL & DRIVE)
# ==============================================================================
elif "5. Simulador Workspace" in menu:
    st.markdown('<div class="main-header">✉️ Simulador Google Workspace (Gmail & Drive)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Demonstração da experiência do usuário no ecossistema Google Workspace</div>', unsafe_allow_html=True)
    
    tab_gmail, tab_drive = st.tabs(["📧 Caixa de Entrada Gmail Simulada", "📁 Pastas do Google Drive"])
    
    with tab_gmail:
        st.subheader("Inbox: consultores@luminarsaude.com.br")
        
        with st.expander("📩 [NOVO] Dr. Fernando Albuquerque — Encaminhamento de Paciente com Apneia Grave (Roberto Silveira)", expanded=True):
            st.markdown("""
            <div class="gmail-box">
                <div class="gmail-subject">Encaminhamento de Paciente com Apneia Grave - Roberto Silveira Santos</div>
                <div class="gmail-sender">De: Dr. Fernando Albuquerque &lt;fernando.albuquerque@clinicasul.med.br&gt;</div>
                <p><b>Data:</b> 20 de Agosto de 2026 às 14:32</p>
                <hr/>
                <p>Prezada equipe comercial e clínica da Luminar Saúde,</p>
                <p>Encaminho em anexo o laudo polissonográfico e a receita médica do paciente Roberto Silveira Santos (52 anos).<br/>
                Diagnóstico: Apneia Obstrutiva do Sono Grave (IAH 38.4/h, dessaturação até 74%). Pressão titulada: 12 cmH2O.<br/>
                <b>Observação:</b> Paciente é respirador oral. Por favor ofertar máscara oronasal AirFit F20 e tubo aquecido.</p>
                <p>Atenciosamente,<br/><b>Dr. Fernando Albuquerque</b> (CRM-SP 142.890)</p>
            </div>
            """, unsafe_allow_html=True)
            
        with st.expander("📤 Proposta Comercial Enviada ao Paciente Roberto Silveira Santos"):
            st.markdown("""
            <div class="gmail-box">
                <div class="gmail-subject">Proposta Personalizada de Tratamento CPAP - Luminar Saúde & Dr. Fernando</div>
                <div class="gmail-sender">De: Lucas Viana - Especialista do Sono &lt;lucas.viana@luminarsaude.com.br&gt;</div>
                <p><b>Para:</b> Roberto Silveira Santos &lt;roberto.silveira@email.com&gt;</p>
                <hr/>
                <p>Olá, Sr. Roberto, tudo bem?</p>
                <p>Estruturamos o pacote sob medida para sua terapia com o <b>ResMed AirSense 11 AutoSet</b> + <b>Máscara AirFit F20</b> + <b>Tubo ClimateLine</b>.</p>
                <p><b>Condição Especial:</b> 12x de R$ 612,08 sem juros ou R$ 6.757,40 à vista com o Programa Luminar Adaptação 30 Dias!</p>
            </div>
            """, unsafe_allow_html=True)
            
        with st.expander("🌟 Follow-up 7 Dias de Terapia Concluídos com Sucesso (AirView)"):
            st.markdown("""
            <div class="gmail-box">
                <div class="gmail-subject">7 Dias de Terapia CPAP Concluídos! Parabéns pela Adesão! 🌟</div>
                <div class="gmail-sender">De: Suporte Clínico Luminar &lt;suporte@luminarsaude.com.br&gt;</div>
                <hr/>
                <p>Prezado Sr. Roberto, nosso telemonitoramento AirView registrou 6h45m de uso médio por noite e seu IAH caiu de 38.4 para 1.2 ev/h!</p>
            </div>
            """, unsafe_allow_html=True)
            
    with tab_drive:
        st.subheader("Estrutura no Google Drive Corporativo (`Luminar Saúde / Vendas & Clínico`)")
        st.markdown("""
        ```text
        📁 Google Drive / Luminar Saúde
        ├── 📁 01_Laudos_Polissonografia/
        │   ├── 📄 Laudo_PSG_Roberto_Silveira.pdf
        │   ├── 📄 Laudo_PSG_Mariana_Costa.pdf
        │   └── 📄 Laudo_PSG_Carlos_Eduardo.pdf
        ├── 📁 02_Playbooks_e_Treinamentos/
        │   └── 📘 Playbook_Vendas_CPAP_Luminar.gdoc
        ├── 📁 03_Planilhas_CRM_e_Precos/
        │   ├── 📊 CRM_Leads_Luminar_Saude.gsheet
        │   └── 📊 Catalogo_Produtos_Precos.gsheet
        └── 📁 04_Propostas_Comerciais_Geradas/
            ├── 📑 Proposta_Roberto_Silveira_AirSense11.gdoc
            └── 📑 Proposta_Carlos_Eduardo_BiPAP.gdoc
        ```
        """)

# ==============================================================================
# MENU 6: RECORRÊNCIA & LTV (INSUMOS)
# ==============================================================================
elif "6. Recorrência" in menu:
    st.markdown('<div class="main-header">🔄 Gestão de Recorrência & Reposição de Insumos (LTV)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Motor proativo de reposição de almofadas de silicone, filtros e tubos</div>', unsafe_allow_html=True)
    
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
        st.subheader("🔔 Oportunidades Automáticas de Recompra")
        for idx, row in df_hist.iterrows():
            with st.expander(f"⚠️ {row['nome_paciente']} — {row['dias_desde_troca_mascara']} dias sem trocar máscara de silicone"):
                st.markdown(f"""
                - **Equipamento Atual:** `{row['produto_sku']}`
                - **Data da Última Troca de Máscara:** {row['data_ultima_troca_mascara']}
                - **Alerta do Sistema:** `{row['alerta_reposicao']}`
                - **Potencial de Receita Imediata:** R$ {row['valor_recorrente_estimado_brl']:,.2f}
                """)
                if st.button(f"📲 Disparar Lembrete de Troca para {row['nome_paciente']}", key=f"btn_recom_{idx}"):
                    st.toast(f"Lembrete de reposição enviado para {row['nome_paciente']} via WhatsApp!")

# ==============================================================================
# MENU 7: GOOGLE CLOUD ARCHITECTURE
# ==============================================================================
elif "7. Google Cloud" in menu:
    st.markdown('<div class="main-header">☁️ Arquitetura Google Cloud da Demonstração</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Mapeamento de serviços utilizados no projeto `abiding-arch-505313-m3`</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ```mermaid
    graph TD
        A[👨‍⚕️ Prescrição Médica & Laudo PDF] -->|Upload| B[🗄️ Cloud Storage Bucket]
        B -->|OCR & Parsing| C[✨ Vertex AI Gemini Multimodal]
        C -->|Gravação Estruturada| D[📊 BigQuery Dataset: luminar_saude]
        D -->|Consultas Analíticas| E[🤖 Vertex AI Agent Platform]
        E -->|MCP Tool Calling| F[🚀 Cloud Run MCP Server]
        F -->|Recomendações em Tempo Real| G[💻 Cockpit Comercial Streamlit]
        E -->|Geração de E-mails & Docs| H[💼 Google Workspace Drive / Gmail]
    ```
    """)
