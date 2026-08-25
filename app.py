import streamlit as st
import pandas as pd
import json
import os
import glob
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Luminar Saúde | Copiloto de Vendas CPAP & Gestão de Leads",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Healthcare Experience
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 800;
        color: #0D47A1;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #546E7A;
        margin-bottom: 20px;
    }
    .metric-box {
        background: linear-gradient(135deg, #FFFFFF, #F1F5F9);
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
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
    .status-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# File Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "bigquery", "data")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

def load_data():
    df_leads = pd.read_csv(os.path.join(DATA_DIR, "leads_pacientes.csv")) if os.path.exists(os.path.join(DATA_DIR, "leads_pacientes.csv")) else pd.DataFrame()
    df_catalogo = pd.read_csv(os.path.join(DATA_DIR, "catalogo_produtos.csv")) if os.path.exists(os.path.join(DATA_DIR, "catalogo_produtos.csv")) else pd.DataFrame()
    df_rec = pd.read_csv(os.path.join(DATA_DIR, "recomendacoes_vendedor.csv")) if os.path.exists(os.path.join(DATA_DIR, "recomendacoes_vendedor.csv")) else pd.DataFrame()
    df_hist = pd.read_csv(os.path.join(DATA_DIR, "historico_compras_trocas.csv")) if os.path.exists(os.path.join(DATA_DIR, "historico_compras_trocas.csv")) else pd.DataFrame()
    return df_leads, df_catalogo, df_rec, df_hist

df_leads, df_catalogo, df_rec, df_hist = load_data()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/lungs.png", width=60)
st.sidebar.title("Luminar Saúde")
st.sidebar.caption("GCP Project: `abiding-arch-505313-m3`")

menu = st.sidebar.radio(
    "Módulos da Demonstração:",
    [
        "🩺 1. Cockpit Comercial & Qualificação",
        "🎯 2. Copiloto de Recomendação (CPAP/Máscaras)",
        "➕ 3. Gerador de Clientes em Tempo Real",
        "🤖 4. Agent Platform & MCP Playground",
        "✉️ 5. Simulador Workspace (Gmail & Drive)",
        "🔄 6. Recorrência & LTV (Insumos)",
        "☁️ 7. Google Cloud Architecture"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Ambiente Integrado:**
- **Agent Platform:** Vertex AI Search & Conversation
- **MCP Server:** `/mcp/manifest.json`
- **BigQuery:** `luminar_saude`
- **GCS:** `gs://abiding-arch-505313-m3-luminar-saude`
""")

# ==============================================================================
# MENU 1: COCKPIT COMERCIAL & QUALIFICAÇÃO
# ==============================================================================
if "1. Cockpit" in menu:
    st.markdown('<div class="main-header">🩺 Cockpit Comercial & Triagem de Pacientes</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Qualificação automática de prescrições médicas e laudos polissonográficos via Gemini</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Pacientes / Leads", len(df_leads), "+ Novo Lead adicionado")
    with col2:
        urgentes = len(df_leads[df_leads['urgencia_comercial'].isin(['URGENTE', 'ALTA'])])
        st.metric("Prioridade Alta / Crítica", urgentes, f"{int(urgentes/len(df_leads)*100)}% da base")
    with col3:
        st.metric("Ticket Médio c/ Cross-Sell", "R$ 6.945,00", "+22% rentabilidade")
    with col4:
        st.metric("Ciclo Comercial Médio", "1.8 dias", "-55% c/ IA")

    st.markdown("---")
    st.subheader("📋 Fila de Leads Qualificados em Tempo Real")
    
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
        last_name = p_info['nome_paciente'].split()[1].lower()
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
# MENU 2: COPILOTO DE RECOMENDAÇÃO DE CPAP
# ==============================================================================
elif "2. Copiloto" in menu:
    st.markdown('<div class="main-header">🎯 Copiloto de Recomendação de Produtos & Quebra de Objeções</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Matching automatizado entre padrão respiratório, pressão prescrita e catálogo de CPAPs/Máscaras</div>', unsafe_allow_html=True)
    
    lead_select = st.selectbox("Selecione o Lead / Paciente:", df_leads['nome_paciente'].tolist())
    lead_row = df_leads[df_leads['nome_paciente'] == lead_select].iloc[0]
    
    # Busca na tabela de recomendação ou calcula dinamicamente
    rec_match = df_rec[df_rec['lead_id'] == lead_row['lead_id']]
    
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
        is_oral = "oral" in str(lead_row.get("respiracao_predominante", "")).lower()
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
# MENU 3: GERADOR DE CLIENTES EM TEMPO REAL (LIVE DEMO SIMULATOR)
# ==============================================================================
elif "3. Gerador" in menu:
    st.markdown('<div class="main-header">➕ Simulador de Geração de Novos Clientes em Tempo Real</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Crie pacientes instantaneamente para demonstrar a reação da IA durante a apresentação</div>', unsafe_allow_html=True)
    
    st.markdown("### ⚡ Cenários de 1-Clique (Predefinições Rápidas para Demonstração)")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        if st.button("🚨 Paciente Apneia Crítica\n(Resp. Oral + Pressão 14)", use_container_width=True):
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
                "diagnostico_cid": "G47.3 - Apneia Grave com Hipoxemia",
                "iah": 42.8,
                "spo2_minima": 71.0,
                "spo2_media": 89.0,
                "pressao_titulada_cmh2o": 14.0,
                "respiracao_predominante": "Oral / Mista",
                "presenca_ronco": "Muito Alto",
                "comorbidades": "Hipertensão Refratária, Obesidade",
                "sensibilidade_pressao": "Alta",
                "score_prioridade": 98,
                "urgencia_comercial": "URGENTE",
                "status_funil": "Qualificado - Lead Live Demo",
                "data_entrada": datetime.now().strftime("%Y-%m-%d")
            }
            df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
            df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
            st.success(f"✅ Lead {novo_id} (Eduardo Brandão) injetado com sucesso! A IA qualificou como Urgência Máxima.")
            st.rerun()

    with c2:
        if st.button("🤧 Paciente Rinite & Claustrofobia\n(Resp. Nasal + Pressão 8.0)", use_container_width=True):
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
                "comorbidades": "Rinite Alérgica, Claustrofobia com Máscaras Faciais",
                "sensibilidade_pressao": "Média",
                "score_prioridade": 86,
                "urgencia_comercial": "ALTA",
                "status_funil": "Qualificado - Lead Live Demo",
                "data_entrada": datetime.now().strftime("%Y-%m-%d")
            }
            df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
            df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
            st.success(f"✅ Lead {novo_id} (Juliana Silveira) injetada com sucesso! A IA recomendou Máscara Pillow P10 e Filtro Hipoalergênico.")
            st.rerun()

    with c3:
        if st.button("✈️ Paciente Executivo Viagem\n(Busca CPAP Portátil)", use_container_width=True):
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
                "presenca_ronco": "Leve a Moderado",
                "comorbidades": "Viagens semanais internacionais",
                "sensibilidade_pressao": "Baixa",
                "score_prioridade": 82,
                "urgencia_comercial": "MEDIA",
                "status_funil": "Qualificado - Lead Live Demo",
                "data_entrada": datetime.now().strftime("%Y-%m-%d")
            }
            df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
            df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
            st.success(f"✅ Lead {novo_id} (Marcelo Guimarães) injetado com sucesso! Recomendado AirMini Portátil.")
            st.rerun()

    with c4:
        if st.button("🫀 Paciente Cardiopata (BiPAP)\n(Pressão 16.0 + Dessaturação)", use_container_width=True):
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
            st.success(f"✅ Lead {novo_id} (Alvaro Ramos) injetado com sucesso! Recomendado BiPAP AirCurve 10.")
            st.rerun()

    st.markdown("---")
    st.subheader("📝 Formulário Manual de Cadastro de Paciente / Prescrição")
    
    with st.form("form_novo_paciente"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            nome = st.text_input("Nome Completo do Paciente", "Carolina Peixoto da Silva")
            idade = st.number_input("Idade", 18, 99, 47)
            genero = st.selectbox("Gênero", ["F", "M"])
            telefone = st.text_input("WhatsApp / Telefone", "(11) 98888-7777")
        with f_col2:
            medico = st.text_input("Médico Prescritor", "Dr. Fernando Albuquerque")
            crm = st.text_input("CRM do Médico", "CRM-SP 142.890")
            convenio = st.selectbox("Convênio", ["Bradesco Saúde", "SulAmérica", "Amil One", "Unimed", "Particular"])
            comorbidades = st.text_input("Comorbidades / Sintomas", "Sonolência Diurna, Hipertensão")
        with f_col3:
            iah_val = st.number_input("Índice de Apneia/Hipopneia (IAH)", 1.0, 100.0, 31.5)
            spo2_val = st.number_input("Saturação Mínima de O2 (%)", 50.0, 99.0, 78.0)
            pressao_val = st.number_input("Pressão Titulada (cmH2O)", 4.0, 25.0, 11.0)
            resp_val = st.selectbox("Padrão Respiratório", ["Oral / Mista", "Nasal", "Predominantemente Oral"])
            
        submitted = st.form_submit_button("🚀 Cadastrar e Qualificar com IA Instantaneamente")
        if submitted:
            novo_id = f"LEAD-{1000 + len(df_leads) + 1}"
            novo_dict = {
                "lead_id": novo_id,
                "nome_paciente": nome,
                "idade": idade,
                "genero": genero,
                "telefone": telefone,
                "email": f"{nome.split()[0].lower()}@email.com",
                "cidade": "São Paulo",
                "estado": "SP",
                "medico_prescritor": medico,
                "crm_medico": crm,
                "especialidade_medico": "Pneumologia",
                "convenio": convenio,
                "diagnostico_cid": f"G47.3 - Apneia Obstrutiva do Sono ({'Grave' if iah_val >= 30 else 'Moderada'})",
                "iah": iah_val,
                "spo2_minima": spo2_val,
                "spo2_media": 92.0,
                "pressao_titulada_cmh2o": pressao_val,
                "respiracao_predominante": resp_val,
                "presenca_ronco": "Frequente",
                "comorbidades": comorbidades,
                "sensibilidade_pressao": "Média",
                "score_prioridade": 95 if iah_val >= 30 else 80,
                "urgencia_comercial": "URGENTE" if iah_val >= 30 else "ALTA",
                "status_funil": "Qualificado - Lead Live Demo",
                "data_entrada": datetime.now().strftime("%Y-%m-%d")
            }
            df_leads = pd.concat([df_leads, pd.DataFrame([novo_dict])], ignore_index=True)
            df_leads.to_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"), index=False)
            st.success(f"🎉 Paciente **{nome}** cadastrado e qualificado como **{novo_dict['urgencia_comercial']}**! Veja na aba Cockpit.")
            st.rerun()

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
        
        # Email 1
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
            
        # Email 2
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
            
        # Email 3
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
            st.button(f"📲 Disparar Lembrete de Troca para {row['nome_paciente']}", key=f"btn_recom_{idx}")

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
