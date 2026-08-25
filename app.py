import streamlit as st
import pandas as pd
import json
import os
import glob

# Set page config
st.set_page_config(
    page_title="Luminar Saúde | Copiloto Comercial & Qualificação de Leads CPAP",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Medical / Corporate Look
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
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF, #F0F4F8);
        border: 1px solid #CFD8DC;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .product-box {
        border-left: 4px solid #1E88E5;
        background-color: #F8FAFC;
        padding: 12px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load CSV Data
DATA_DIR = os.path.join(os.path.dirname(__file__), "bigquery", "data")
WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "workspace")
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")

@st.cache_data
def load_data():
    df_leads = pd.read_csv(os.path.join(DATA_DIR, "leads_pacientes.csv"))
    df_catalogo = pd.read_csv(os.path.join(DATA_DIR, "catalogo_produtos.csv"))
    df_rec = pd.read_csv(os.path.join(DATA_DIR, "recomendacoes_vendedor.csv"))
    df_hist = pd.read_csv(os.path.join(DATA_DIR, "historico_compras_trocas.csv"))
    return df_leads, df_catalogo, df_rec, df_hist

df_leads, df_catalogo, df_rec, df_hist = load_data()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/lungs.png", width=64)
st.sidebar.title("Luminar Saúde")
st.sidebar.caption("Demo Argolis: abiding-arch-505313-m3")

menu = st.sidebar.radio(
    "Navegação:",
    [
        "🩺 1. Radar de Leads & Triagem IA",
        "🎯 2. Copiloto de Recomendação de CPAP",
        "✉️ 3. Gerador Omnichannel (WhatsApp / Gmail)",
        "🔄 4. Recorrência & Pós-Venda (LTV)",
        "☁️ 5. Google Cloud & BigQuery Assets",
        "📁 6. Google Workspace & Drive Assets"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Ambiente de Demonstração**
- **Projeto GCP:** `abiding-arch-505313-m3`
- **BigQuery Dataset:** `luminar_saude`
- **Cloud Storage:** `gs://abiding-arch-505313-m3-luminar-saude`
""")

# ==============================================================================
# MENU 1: RADAR DE LEADS & TRIAGEM IA
# ==============================================================================
if "1. Radar" in menu:
    st.markdown('<div class="main-header">🩺 Radar de Qualificação de Leads & Diagnóstico Clínico</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Triagem inteligente de prescrições médicas e laudos polissonográficos com IA</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Novos Leads Hoje", len(df_leads), "+2 desde ontem")
    with col2:
        urgentes = len(df_leads[df_leads['urgencia_comercial'].isin(['URGENTE', 'ALTA'])])
        st.metric("Prioridade Alta / Urgente", urgentes, "80% da base")
    with col3:
        st.metric("Ticket Médio Estimado", "R$ 6.954,00", "+18% cross-sell")
    with col4:
        st.metric("Tempo Médio de Fechamento", "2.1 dias", "-45% c/ IA")

    st.markdown("---")
    
    st.subheader("📋 Lista de Pacientes / Leads Qualificados")
    
    display_df = df_leads[['lead_id', 'nome_paciente', 'idade', 'convenio', 'diagnostico_cid', 'iah', 'spo2_minima', 'pressao_titulada_cmh2o', 'respiracao_predominante', 'urgencia_comercial', 'score_prioridade']].copy()
    display_df.columns = ['ID', 'Paciente', 'Idade', 'Convênio', 'Diagnóstico CID', 'IAH (ev/h)', 'SpO2 Mín (%)', 'Pressão Titulada', 'Respiração', 'Urgência', 'Score']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("🔍 Detalhe Clínico e Extração de Laudo Polissonográfico")
    
    selected_patient = st.selectbox("Selecione o paciente para inspeção detalhada:", df_leads['nome_paciente'].tolist())
    p_info = df_leads[df_leads['nome_paciente'] == selected_patient].iloc[0]
    
    c_left, c_right = st.columns([1.2, 1])
    
    with c_left:
        st.markdown(f"### 🫁 Ficha Médica: {p_info['nome_paciente']}")
        st.markdown(f"""
        - **Idade / Gênero:** {p_info['idade']} anos ({p_info['genero']})
        - **Contato:** {p_info['telefone']} | {p_info['email']}
        - **Localização:** {p_info['cidade']} - {p_info['estado']}
        - **Médico Prescritor:** {p_info['medico_prescritor']} ({p_info['crm_medico']})
        - **Especialidade:** {p_info['especialidade_medico']}
        - **Convênio / Plano:** {p_info['convenio']}
        - **Comorbidades Associadas:** `{p_info['comorbidades']}`
        """)
        
        if p_info['iah'] >= 30:
            st.error(f"⚠️ **Apneia Obstrutiva Grave**: IAH de **{p_info['iah']} eventos/hora** com queda crítica de SpO2 para **{p_info['spo2_minima']}%**. Alto risco cardiovascular! Abordagem comercial prioritária.")
        elif p_info['iah'] >= 15:
            st.warning(f"⚠️ **Apneia Obstrutiva Moderada**: IAH de **{p_info['iah']} eventos/hora** (SpO2 mínima {p_info['spo2_minima']}%).")
        else:
            st.info(f"ℹ️ **Apneia Leve**: IAH de **{p_info['iah']} eventos/hora** com queixa de sonolência diurna.")

    with c_right:
        st.markdown("### 📄 Extração Multimodal de Laudo (Cloud Storage / OCR)")
        first_name = p_info['nome_paciente'].split()[0].lower()
        last_name = p_info['nome_paciente'].split()[1].lower()
        txt_filename = f"laudo_psg_{first_name}_{last_name}.txt"
        txt_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", txt_filename)
        
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.text_area("Laudo Estruturado Extraído por IA (Gemini Flash OCR):", content, height=210)
        
        pdf_filename = f"laudo_psg_{first_name}_{last_name}.pdf"
        pdf_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", pdf_filename)
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f_pdf:
                st.download_button(
                    label=f"📥 Baixar Laudo Completo em PDF ({pdf_filename})",
                    data=f_pdf,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

# ==============================================================================
# MENU 2: COPILOTO DE RECOMENDAÇÃO DE CPAP
# ==============================================================================
elif "2. Copiloto" in menu:
    st.markdown('<div class="main-header">🎯 Copiloto de Recomendação de Equipamentos & Insumos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Matching automatizado entre prescrição clínica, preferências de conforto e catálogo comercial</div>', unsafe_allow_html=True)
    
    lead_select = st.selectbox("Selecione o Lead / Paciente:", df_leads['nome_paciente'].tolist())
    lead_row = df_leads[df_leads['nome_paciente'] == lead_select].iloc[0]
    rec_row = df_rec[df_rec['lead_id'] == lead_row['lead_id']].iloc[0]
    
    st.markdown("---")
    
    col_rec_left, col_rec_right = st.columns([1.3, 1])
    
    with col_rec_left:
        st.markdown(f"### 💡 Pacote Recomendado por IA para **{lead_row['nome_paciente']}**")
        
        st.markdown(f"""
        <div class="product-box">
            <h4 style="color:#0D47A1; margin:0;">1. Equipamento Principal: {rec_row['equipamento_principal_nome']}</h4>
            <p><b>SKU:</b> <code>{rec_row['equipamento_principal_sku']}</code></p>
        </div>
        <div class="product-box">
            <h4 style="color:#00838F; margin:0;">2. Interface / Máscara: {rec_row['mascara_recomendada_nome']}</h4>
            <p><b>SKU:</b> <code>{rec_row['mascara_recomendada_sku']}</code></p>
        </div>
        <div class="product-box">
            <h4 style="color:#2E7D32; margin:0;">3. Insumos Cross-Sell & Acessórios</h4>
            <p>{rec_row['insumos_cross_sell']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🧠 Racional Clínico-Comercial da IA")
        st.info(rec_row['argumentacao_venda_ia'])
        
        st.markdown("#### 🛡️ Quebra de Objeções Pronta para o Vendedor")
        st.warning(f"**Como contornar hesitação do paciente:**\n\n{rec_row['quebra_objecoes']}")

    with col_rec_right:
        st.markdown("### 💰 Proposta Financeira & Conversão")
        
        st.metric("Valor Total do Pacote", f"R$ {rec_row['valor_total_pacote_brl']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.metric("Probabilidade de Conversão IA", f"{int(rec_row['probabilidade_conversao']*100)}%", "+24% acima da média")
        
        st.markdown("#### 💳 Condições Comerciais")
        st.success(f"**Opções de Fechamento:**\n\n{rec_row['condicao_comercial_sugerida']}")
        
        st.markdown("#### ⚡ Ações Rápidas do Vendedor")
        if st.button("🚀 Gerar Proposta Comercial em PDF", use_container_width=True):
            st.toast("Proposta gerada com sucesso e arquivada no Google Drive!")
        if st.button("📲 Disparar Prévia no WhatsApp", use_container_width=True):
            st.toast("Mensagem formatada copiada para o painel de atendimento!")
        if st.button("📧 Notificar Médico Prescritor via Gmail", use_container_width=True):
            st.toast("Notificação de atendimento enviada ao Dr. Prescritor!")

# ==============================================================================
# MENU 3: GERADOR OMNICHANNEL (WHATSAPP / GMAIL)
# ==============================================================================
elif "3. Gerador Omnichannel" in menu:
    st.markdown('<div class="main-header">✉️ Gerador de Mensagens e Propostas Omnichannel</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Templates hiper-personalizados baseados no diagnóstico do paciente para Gmail e WhatsApp</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["📧 Proposta por E-mail (Gmail)", "📲 Mensagens de WhatsApp", "📩 E-mail de Encaminhamento Médico", "📊 Telemonitoramento (7 Dias)"])
    
    with t1:
        st.subheader("E-mail Comercial Personalizado para o Paciente")
        with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "02_proposta_comercial_paciente.md"), "r", encoding="utf-8") as f:
            email_content = f.read()
        st.markdown(f"```text\n{email_content}\n```")
        if st.button("Copiar E-mail da Proposta"):
            st.toast("Copiado com sucesso!")
            
    with t2:
        st.subheader("Script Interativo de Conversação no WhatsApp")
        with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "03_script_whatsapp_vendedor.md"), "r", encoding="utf-8") as f:
            wpp_content = f.read()
        st.markdown(wpp_content)
        
    with t3:
        st.subheader("E-mail Recebido do Médico com Encaminhamento")
        with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "01_encaminhamento_medico.md"), "r", encoding="utf-8") as f:
            med_content = f.read()
        st.markdown(f"```text\n{med_content}\n```")
        
    with t4:
        st.subheader("E-mail Pós-Venda: Adesão e Telemonitoramento AirView")
        with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "04_pos_venda_adesao_telemonitoramento.md"), "r", encoding="utf-8") as f:
            pos_content = f.read()
        st.markdown(f"```text\n{pos_content}\n```")

# ==============================================================================
# MENU 4: RECORRÊNCIA & PÓS-VENDA (LTV)
# ==============================================================================
elif "4. Recorrência" in menu:
    st.markdown('<div class="main-header">🔄 Gestão de Recorrência & Reposição de Insumos (LTV)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Geração automática de novas oportunidades de venda de filtros, traqueias e almofadas</div>', unsafe_allow_html=True)
    
    st.markdown("""
    > [!TIP]
    > **Regra de Ouro da Terapia Respiratória:** As almofadas de silicone perdem a vedação após 6 meses de uso, aumentando o vazamento de ar e o desconforto. Filtros devem ser trocados a cada 30-60 dias.
    """)
    
    st.dataframe(df_hist, use_container_width=True, hide_index=True)
    
    st.subheader("🔔 Pacientes com Alertas de Troca Imediata")
    for idx, row in df_hist.iterrows():
        with st.expander(f"⚠️ {row['nome_paciente']} ({row['paciente_id']}) — {row['dias_desde_troca_mascara']} dias sem trocar máscara"):
            st.markdown(f"""
            - **Equipamento em Uso:** `{row['produto_sku']}`
            - **Data da Compra Inicial:** {row['data_compra']}
            - **Última Troca de Máscara:** {row['data_ultima_troca_mascara']}
            - **Alerta do Sistema:** `{row['alerta_reposicao']}`
            - **Potencial de Receita Recorrente:** R$ {row['valor_recorrente_estimado_brl']:,.2f}
            """)
            st.button(f"📲 Disparar Lembrete WhatsApp para {row['nome_paciente']}", key=f"btn_rec_{idx}")

# ==============================================================================
# MENU 5: GOOGLE CLOUD & BIGQUERY ASSETS
# ==============================================================================
elif "5. Google Cloud" in menu:
    st.markdown('<div class="main-header">☁️ Google Cloud Assets & Arquitetura de Dados</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tabelas do BigQuery, Queries de IA e Buckets do Cloud Storage</div>', unsafe_allow_html=True)
    
    tab_sql1, tab_sql2, tab_gcs = st.tabs(["📊 BigQuery Schemas (DDL)", "⚡ Consultas SQL & BigQuery AI", "🗄️ Cloud Storage Layout"])
    
    with tab_sql1:
        st.subheader("DDL do Dataset `luminar_saude`")
        with open(os.path.join(os.path.dirname(__file__), "bigquery", "schema.sql"), "r", encoding="utf-8") as f:
            schema_content = f.read()
        st.code(schema_content, language="sql")
        
    with tab_sql2:
        st.subheader("Consultas de Junção Comercial & Gemini no BigQuery")
        with open(os.path.join(os.path.dirname(__file__), "bigquery", "analytics_queries.sql"), "r", encoding="utf-8") as f:
            queries_content = f.read()
        st.code(queries_content, language="sql")
        
    with tab_gcs:
        st.subheader("Estrutura do Bucket: `gs://abiding-arch-505313-m3-luminar-saude`")
        st.markdown("""
        ```bash
        gs://abiding-arch-505313-m3-luminar-saude/
        ├── laudos_polissonografia/
        │   ├── laudo_psg_roberto_silveira.pdf
        │   ├── laudo_psg_roberto_silveira.txt
        │   ├── laudo_psg_mariana_costa.pdf
        │   ├── laudo_psg_mariana_costa.txt
        │   ├── laudo_psg_carlos_eduardo.pdf
        │   ├── laudo_psg_carlos_eduardo.txt
        │   ├── laudo_psg_fernanda_lima.pdf
        │   ├── laudo_psg_fernanda_lima.txt
        │   ├── laudo_psg_luiz_gustavo.pdf
        │   └── laudo_psg_luiz_gustavo.txt
        ├── catalogos_manuais/
        │   └── catalogo_produtos.csv
        └── datasets_raw/
            ├── leads_pacientes.csv
            ├── catalogo_produtos.csv
            └── recomendacoes_vendedor.csv
        ```
        """)

# ==============================================================================
# MENU 6: GOOGLE WORKSPACE & DRIVE ASSETS
# ==============================================================================
elif "6. Google Workspace" in menu:
    st.markdown('<div class="main-header">📁 Google Workspace & Drive Assets</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Planilhas, Playbooks de Vendas e Materiais de Apoio</div>', unsafe_allow_html=True)
    
    st.subheader("📘 Playbook de Vendas: Qualificação e Conversão de CPAP (Google Docs)")
    with open(os.path.join(WORKSPACE_DIR, "google_drive", "Playbook_Vendas_Luminar_Saude.md"), "r", encoding="utf-8") as f:
        playbook_content = f.read()
    st.markdown(playbook_content)
    
    st.markdown("---")
    st.subheader("📊 Planilhas do Google Sheets Prontas para Importação")
    st.markdown("""
    - `workspace/google_sheets/CRM_Leads_Luminar_Saude.csv`
    - `workspace/google_sheets/Catalogo_Produtos_Precos.csv`
    """)
