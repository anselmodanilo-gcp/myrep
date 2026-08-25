#!/usr/bin/env python3
"""
Asset Generator for Luminar Saúde Demo
Generates:
- BigQuery CSV and SQL datasets
- Clinical Polysomnography (PSG) reports & Prescriptions (PDF & Text)
- Product Catalog & Specs
- Gmail & WhatsApp templates
- Google Drive Dossiers & Playbooks
"""

import os
import csv
import json

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

PROJECT_ID = "abiding-arch-505313-m3"
DATASET_ID = "luminar_saude"
BUCKET_NAME = f"{PROJECT_ID}-luminar-saude"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BQ_DATA_DIR = os.path.join(BASE_DIR, "bigquery", "data")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")

os.makedirs(BQ_DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "laudos_polissonografia"), exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "receitas_medicas"), exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "catalogos_manuais"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "gmail_templates"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "google_drive"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "google_sheets"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "bigquery"), exist_ok=True)

# -------------------------------------------------------------
# 1. DATASETS DEFINITION
# -------------------------------------------------------------

LEADS_PACIENTES = [
    {
        "lead_id": "LEAD-1001",
        "nome_paciente": "Roberto Silveira Santos",
        "idade": 52,
        "genero": "M",
        "telefone": "(11) 98765-4321",
        "email": "roberto.silveira@email.com",
        "cidade": "São Paulo",
        "estado": "SP",
        "medico_prescritor": "Dr. Fernando Albuquerque",
        "crm_medico": "CRM-SP 142.890",
        "especialidade_medico": "Pneumologia e Medicina do Sono",
        "convenio": "Bradesco Saúde Top Nacional",
        "diagnostico_cid": "G47.3 - Apneia Obstrutiva do Sono Grave",
        "iah": 38.4,
        "spo2_minima": 74.0,
        "spo2_media": 91.5,
        "pressao_titulada_cmh2o": 12.0,
        "respiracao_predominante": "Oral / Mista",
        "presenca_ronco": "Alto / Frequente",
        "comorbidades": "Hipertensão Arterial, Obesidade Grau 1",
        "sensibilidade_pressao": "Alta (necessita alívio expiratório)",
        "score_prioridade": 95,
        "urgencia_comercial": "ALTA",
        "status_funil": "Qualificado - Aguardando Proposta",
        "data_entrada": "2026-08-20"
    },
    {
        "lead_id": "LEAD-1002",
        "nome_paciente": "Mariana Costa Andrade",
        "idade": 41,
        "genero": "F",
        "telefone": "(11) 97654-3210",
        "email": "mariana.andrade@email.com",
        "cidade": "Campinas",
        "estado": "SP",
        "medico_prescritor": "Dra. Beatriz Mendes",
        "crm_medico": "CRM-SP 178.432",
        "especialidade_medico": "Otorrinolaringologia",
        "convenio": "SulAmérica Especial",
        "diagnostico_cid": "G47.3 - Apneia Obstrutiva do Sono Moderada",
        "iah": 21.2,
        "spo2_minima": 84.0,
        "spo2_media": 94.2,
        "pressao_titulada_cmh2o": 8.5,
        "respiracao_predominante": "Nasal",
        "presenca_ronco": "Moderado",
        "comorbidades": "Rinite Alérgica Crônica, Insônia Inicial",
        "sensibilidade_pressao": "Média (relato de claustrofobia com máscaras volumosas)",
        "score_prioridade": 88,
        "urgencia_comercial": "ALTA",
        "status_funil": "Qualificado - Demonstração Agendada",
        "data_entrada": "2026-08-21"
    },
    {
        "lead_id": "LEAD-1003",
        "nome_paciente": "Carlos Eduardo Paes",
        "idade": 63,
        "genero": "M",
        "telefone": "(21) 99123-4567",
        "email": "cadu.paes@email.com",
        "cidade": "Rio de Janeiro",
        "estado": "RJ",
        "medico_prescritor": "Dr. Henrique Vasconcellos",
        "crm_medico": "CRM-RJ 98.765",
        "especialidade_medico": "Cardiologia",
        "convenio": "Particular (Reembolso Amil One)",
        "diagnostico_cid": "G47.3 - Apneia Mista com Hipoxemia Noturna",
        "iah": 46.0,
        "spo2_minima": 68.0,
        "spo2_media": 88.0,
        "pressao_titulada_cmh2o": 15.0,
        "respiracao_predominante": "Oral",
        "presenca_ronco": "Muito Alto",
        "comorbidades": "Insuficiência Cardíaca Leve, Fibrilação Atrial",
        "sensibilidade_pressao": "Muito Alta (indicação BiPAP ou Auto-CPAP com EPR máximo)",
        "score_prioridade": 98,
        "urgencia_comercial": "URGENTE",
        "status_funil": "Em Negociação - Teste em Domicílio",
        "data_entrada": "2026-08-22"
    },
    {
        "lead_id": "LEAD-1004",
        "nome_paciente": "Fernanda Lima de Oliveira",
        "idade": 36,
        "genero": "F",
        "telefone": "(31) 98877-6655",
        "email": "fernanda.oliveira@email.com",
        "cidade": "Belo Horizonte",
        "estado": "MG",
        "medico_prescritor": "Dra. Camila Nogueira",
        "crm_medico": "CRM-MG 65.432",
        "especialidade_medico": "Neurologia",
        "convenio": "Unimed Nacional",
        "diagnostico_cid": "G47.3 - Apneia Leve com Sintomas Diurnos",
        "iah": 9.8,
        "spo2_minima": 90.0,
        "spo2_media": 96.0,
        "pressao_titulada_cmh2o": 6.0,
        "respiracao_predominante": "Nasal",
        "presenca_ronco": "Leve",
        "comorbidades": "Sonolência Diurna Excessiva (Epworth 14), Bruxismo",
        "sensibilidade_pressao": "Baixa (busca equipamento ultrassilencioso para viagens)",
        "score_prioridade": 72,
        "urgencia_comercial": "MEDIA",
        "status_funil": "Primeiro Contato Realizado",
        "data_entrada": "2026-08-23"
    },
    {
        "lead_id": "LEAD-1005",
        "nome_paciente": "Luiz Gustavo Moreira",
        "idade": 48,
        "genero": "M",
        "telefone": "(41) 99888-1122",
        "email": "luiz.moreira@email.com",
        "cidade": "Curitiba",
        "estado": "PR",
        "medico_prescritor": "Dr. Fernando Albuquerque",
        "crm_medico": "CRM-SP 142.890",
        "especialidade_medico": "Pneumologia",
        "convenio": "Porto Seguro Ouro",
        "diagnostico_cid": "G47.3 - Apneia Obstrutiva Grave Posicional",
        "iah": 32.1,
        "spo2_minima": 79.0,
        "spo2_media": 92.0,
        "pressao_titulada_cmh2o": 10.5,
        "respiracao_predominante": "Nasal",
        "presenca_ronco": "Alto",
        "comorbidades": "Diabetes Tipo 2, Refluxo Gastroesofágico",
        "sensibilidade_pressao": "Média",
        "score_prioridade": 85,
        "urgencia_comercial": "ALTA",
        "status_funil": "Qualificado - Aguardando Proposta",
        "data_entrada": "2026-08-24"
    }
]

CATALOGO_PRODUTOS = [
    {
        "sku": "CPAP-RES-AS11",
        "categoria": "CPAP Auto",
        "fabricante": "ResMed",
        "modelo": "AirSense 11 AutoSet",
        "descricao": "CPAP automático premium com conectividade celular integrada (AirView), tecnologia AutoSet avançada, algoritmo de alívio expiratório EPR e tela touchscreen.",
        "faixa_pressao_cmh2o": "4 a 20",
        "nivel_ruido_dba": 25.0,
        "umidificador_incluso": "Sim (HumidAir integrado + ClimateLineAir opcional)",
        "peso_kg": 1.13,
        "preco_venda_brl": 5890.00,
        "preco_aluguel_mensal_brl": 290.00,
        "indicacao_clinica": "Apneia obstrutiva moderada a grave. Pacientes que demandam conforto, ajuste automático e telemonitoramento médico contínuo.",
        "itens_inclusos": "CPAP AirSense 11, Umidificador HumidAir, Tubo SlimLine, Filtro ultrafino, Fonte bivolt, Bolsa de transporte",
        "garantia_meses": 24,
        "estoque_disponivel": 45
    },
    {
        "sku": "CPAP-RES-AS10",
        "categoria": "CPAP Auto",
        "fabricante": "ResMed",
        "modelo": "AirSense 10 AutoSet 4G",
        "descricao": "CPAP automático mais consagrado do mercado global. Conectividade GSM AirView, alívio de pressão EPR e umidificador HumidAir integrado.",
        "faixa_pressao_cmh2o": "4 a 20",
        "nivel_ruido_dba": 26.6,
        "umidificador_incluso": "Sim (HumidAir integrado)",
        "peso_kg": 1.24,
        "preco_venda_brl": 4490.00,
        "preco_aluguel_mensal_brl": 240.00,
        "indicacao_clinica": "Excelente custo-benefício para tratamento de AOS leve, moderada e grave.",
        "itens_inclusos": "CPAP AirSense 10, Umidificador, Tubo padrão, Filtro, Fonte, Bolsa de transporte",
        "garantia_meses": 24,
        "estoque_disponivel": 60
    },
    {
        "sku": "BIPAP-RES-AC10",
        "categoria": "BiPAP / BiLevel",
        "fabricante": "ResMed",
        "modelo": "AirCurve 10 VAuto",
        "descricao": "Equipamento binível autoajustável para pacientes com alta necessidade pressórica, apneia complexa ou intolerância ao CPAP convencional.",
        "faixa_pressao_cmh2o": "4 a 25",
        "nivel_ruido_dba": 27.0,
        "umidificador_incluso": "Sim (HumidAir integrado)",
        "peso_kg": 1.25,
        "preco_venda_brl": 9800.00,
        "preco_aluguel_mensal_brl": 550.00,
        "indicacao_clinica": "Pressões de titulação superiores a 14 cmH2O, apneia mista, insuficiência respiratória ou intolerância a CPAP fixo/auto.",
        "itens_inclusos": "AirCurve 10 VAuto, Umidificador, Tubo ClimateLine, Filtro, Fonte, Bolsa",
        "garantia_meses": 24,
        "estoque_disponivel": 18
    },
    {
        "sku": "CPAP-BMC-G3A20",
        "categoria": "CPAP Auto",
        "fabricante": "BMC Medical",
        "modelo": "G3 A20 Auto CPAP",
        "descricao": "CPAP automático com pré-aquecimento inteligente do umidificador, conectividade Wi-Fi/QR Code no app PAP Link e design moderno.",
        "faixa_pressao_cmh2o": "4 a 20",
        "nivel_ruido_dba": 26.0,
        "umidificador_incluso": "Sim (Integrado com tubo aquecido)",
        "peso_kg": 1.30,
        "preco_venda_brl": 3290.00,
        "preco_aluguel_mensal_brl": 190.00,
        "indicacao_clinica": "Opção econômica e de alta eficiência para apneia do sono obstrutiva.",
        "itens_inclusos": "CPAP G3, Umidificador, Tubo aquecido, Filtros, Cartão SD, Bolsa",
        "garantia_meses": 24,
        "estoque_disponivel": 35
    },
    {
        "sku": "CPAP-RES-MINI",
        "categoria": "CPAP Portátil / Viagem",
        "fabricante": "ResMed",
        "modelo": "AirMini AutoSet",
        "descricao": "O menor CPAP automático do mundo (pesa apenas 300g). Sistema de umidificação anidra HumidX sem água, controle 100% via app Bluetooth.",
        "faixa_pressao_cmh2o": "4 a 20",
        "nivel_ruido_dba": 30.0,
        "umidificador_incluso": "Sim (Cápsula HumidX sem água)",
        "peso_kg": 0.30,
        "preco_venda_brl": 5490.00,
        "preco_aluguel_mensal_brl": 280.00,
        "indicacao_clinica": "Pacientes que viajam com frequência ou buscam máxima discrição e mobilidade.",
        "itens_inclusos": "AirMini, Fonte de alimentação, Tubo específico, Cápsulas HumidX, Estojo",
        "garantia_meses": 24,
        "estoque_disponivel": 22
    },
    {
        "sku": "MSK-RES-F20",
        "categoria": "Máscara Facial / Oronasal",
        "fabricante": "ResMed",
        "modelo": "AirFit F20 Full Face",
        "descricao": "Máscara facial com almofada de silicone InfinitySeal desenhada para vedação perfeita em altas pressões e respiração pela boca.",
        "faixa_pressao_cmh2o": "4 a 30",
        "nivel_ruido_dba": 21.0,
        "umidificador_incluso": "N/A",
        "peso_kg": 0.12,
        "preco_venda_brl": 890.00,
        "preco_aluguel_mensal_brl": 0.0,
        "indicacao_clinica": "Pacientes com respiração oral ou mista, desvio de septo ou pressões de titulação acima de 10 cmH2O.",
        "itens_inclusos": "Armação, Fixador de cabeça com presilhas magnéticas, Almofada InfinitySeal (P, M ou G)",
        "garantia_meses": 3,
        "estoque_disponivel": 120
    },
    {
        "sku": "MSK-RES-N20",
        "categoria": "Máscara Nasal",
        "fabricante": "ResMed",
        "modelo": "AirFit N20 Nasal",
        "descricao": "Máscara nasal compacta com almofada InfinitySeal, campo de visão livre para leitura e clips magnéticos para fácil remoção.",
        "faixa_pressao_cmh2o": "4 a 20",
        "nivel_ruido_dba": 20.0,
        "umidificador_incluso": "N/A",
        "peso_kg": 0.09,
        "preco_venda_brl": 690.00,
        "preco_aluguel_mensal_brl": 0.0,
        "indicacao_clinica": "Pacientes que respiram exclusivamente pelo nariz e buscam conforto e estabilidade durante o sono.",
        "itens_inclusos": "Armação, Fixador de cabeça magnético, Almofada nasal InfinitySeal",
        "garantia_meses": 3,
        "estoque_disponivel": 150
    },
    {
        "sku": "MSK-RES-P10",
        "categoria": "Máscara Almofadas Nasais (Pillows)",
        "fabricante": "ResMed",
        "modelo": "AirFit P10 Ultra Silenciosa",
        "descricao": "Máscara de almofadas nasais ultraleve (45g) com ventilação QuietAir de malha tecida que dispersa o ar suavemente.",
        "faixa_pressao_cmh2o": "4 a 15",
        "nivel_ruido_dba": 17.0,
        "umidificador_incluso": "N/A",
        "peso_kg": 0.045,
        "preco_venda_brl": 720.00,
        "preco_aluguel_mensal_brl": 0.0,
        "indicacao_clinica": "Pacientes claustrofóbicos, usuários que usam óculos na cama e respiradores nasais puros com pressões baixas a médias.",
        "itens_inclusos": "Arnês QuickFit elástico, 3 tamanhos de almofadas (P, M, G), tubo curto flexível",
        "garantia_meses": 3,
        "estoque_disponivel": 95
    },
    {
        "sku": "MSK-FPH-EVORA",
        "categoria": "Máscara Facial Híbrida",
        "fabricante": "Fisher & Paykel",
        "modelo": "Evora Full Face",
        "descricao": "Máscara facial compacta que se assenta sob o nariz (evita marcas na ponte nasal) e cobre a boca com vedação Dynamic Support.",
        "faixa_pressao_cmh2o": "4 a 25",
        "nivel_ruido_dba": 24.0,
        "umidificador_incluso": "N/A",
        "peso_kg": 0.11,
        "preco_venda_brl": 950.00,
        "preco_aluguel_mensal_brl": 0.0,
        "indicacao_clinica": "Respiradores orais que sentem desconforto com máscaras oronasais tradicionais na testa/nariz.",
        "itens_inclusos": "Máscara completa com arnês VentiCool respirável",
        "garantia_meses": 3,
        "estoque_disponivel": 40
    },
    {
        "sku": "INS-RES-CLINE",
        "categoria": "Insumo / Tubo Aquecido",
        "fabricante": "ResMed",
        "modelo": "Tubo Aquecido ClimateLineAir",
        "descricao": "Tubo com sensor térmico na ponta para manter temperatura e umidade constantes, eliminando 100% da condensação de água no tubo.",
        "faixa_pressao_cmh2o": "N/A",
        "nivel_ruido_dba": 0.0,
        "umidificador_incluso": "N/A",
        "peso_kg": 0.18,
        "preco_venda_brl": 390.00,
        "preco_aluguel_mensal_brl": 0.0,
        "indicacao_clinica": "Indispensável em regiões frias ou pacientes que usam alta umidificação e sofrem com 'gotejamento' de água.",
        "itens_inclusos": "1 Tubo térmico ClimateLineAir",
        "garantia_meses": 3,
        "estoque_disponivel": 200
    },
    {
        "sku": "INS-RES-FLT-HP",
        "categoria": "Insumo / Filtros",
        "fabricante": "ResMed",
        "modelo": "Kit 6 Filtros Hipoalergênicos AirSense 10/11",
        "descricao": "Filtro de microfibras de alta retenção contra pólen, ácaros, poeira e partículas finas.",
        "faixa_pressao_cmh2o": "N/A",
        "nivel_ruido_dba": 0.0,
        "umidificador_incluso": "N/A",
        "peso_kg": 0.02,
        "preco_venda_brl": 150.00,
        "preco_aluguel_mensal_brl": 0.0,
        "indicacao_clinica": "Recomendado para todos os pacientes alérgicos. Troca recomendada a cada 30 a 60 dias.",
        "itens_inclusos": "Pacote com 6 unidades seladas",
        "garantia_meses": 12,
        "estoque_disponivel": 350
    },
    {
        "sku": "INS-CPAP-WIPES",
        "categoria": "Higiene e Acessórios",
        "fabricante": "Luminar Care",
        "modelo": "Lenços Umedecidos 100% Algodão para Máscara CPAP (62 un)",
        "descricao": "Lenços sem álcool nem fragrância para limpeza diária de máscaras de silicone, aumentando a vida útil e prevenindo oleosidade e vazamentos.",
        "faixa_pressao_cmh2o": "N/A",
        "nivel_ruido_dba": 0.0,
        "umidificador_incluso": "N/A",
        "peso_kg": 0.35,
        "preco_venda_brl": 75.00,
        "preco_aluguel_mensal_brl": 0.0,
        "indicacao_clinica": "Higiene diária essencial para evitar infecções e foliculite facial.",
        "itens_inclusos": "Frasco dispenser com 62 lenços biodegradáveis",
        "garantia_meses": 24,
        "estoque_disponivel": 500
    }
]

RECOMENDACOES_VENDEDOR = [
    {
        "recomendacao_id": "REC-001",
        "lead_id": "LEAD-1001",
        "nome_paciente": "Roberto Silveira Santos",
        "equipamento_principal_sku": "CPAP-RES-AS11",
        "equipamento_principal_nome": "ResMed AirSense 11 AutoSet",
        "mascara_recomendada_sku": "MSK-RES-F20",
        "mascara_recomendada_nome": "AirFit F20 Full Face (Tamanho G)",
        "insumos_cross_sell": "INS-RES-CLINE (Tubo ClimateLineAir) + INS-RES-FLT-HP (Kit Filtros) + INS-CPAP-WIPES (Lenços)",
        "valor_total_pacote_brl": 7345.00,
        "condicao_comercial_sugerida": "12x de R$ 612,08 sem juros no cartão ou 8% de desconto à vista no PIX (R$ 6.757,40)",
        "argumentacao_venda_ia": "Paciente com IAH 38.4 (Grave) e respiração oral com pressão 12 cmH2O. É fundamental ofertar máscara oronasal F20 para evitar vazamento pela boca e ressecamento. O AirSense 11 com EPR alivia o esforço ao expirar e o tubo aquecido previne condensação no inverno. Destacar o telemonitoramento AirView para acompanhamento pelo Dr. Fernando Albuquerque.",
        "quebra_objecoes": "Se o paciente achar a máscara facial grande, demonstrar o silicone InfinitySeal macio e oferecer o plano Luminar Adaptação 30 Dias (troca grátis de modelo se não se adaptar).",
        "probabilidade_conversao": 0.94
    },
    {
        "recomendacao_id": "REC-002",
        "lead_id": "LEAD-1002",
        "nome_paciente": "Mariana Costa Andrade",
        "equipamento_principal_sku": "CPAP-RES-AS10",
        "equipamento_principal_nome": "ResMed AirSense 10 AutoSet 4G",
        "mascara_recomendada_sku": "MSK-RES-P10",
        "mascara_recomendada_nome": "AirFit P10 Almofadas Nasais",
        "insumos_cross_sell": "INS-RES-FLT-HP (Filtros Hipoalergênicos) + INS-CPAP-WIPES",
        "valor_total_pacote_brl": 5435.00,
        "condicao_comercial_sugerida": "Opção Compra em 12x R$ 452,91 ou Locação com opção de compra (R$ 240/mês nos primeiros 3 meses)",
        "argumentacao_venda_ia": "Paciente queixa-se de claustrofobia e tem respiração puramente nasal com pressão leve-moderada (8.5 cmH2O). A máscara P10 pesa apenas 45g e não obstrui a visão. Como tem rinite alérgica crônica, o kit de filtros hipoalergênicos é essencial.",
        "quebra_objecoes": "Se receio de dor no nariz, explicar que as almofadas de silicone ultrafinas da P10 possuem vedação com efeito mola sem apertar as narinas.",
        "probabilidade_conversao": 0.89
    },
    {
        "recomendacao_id": "REC-003",
        "lead_id": "LEAD-1003",
        "nome_paciente": "Carlos Eduardo Paes",
        "equipamento_principal_sku": "BIPAP-RES-AC10",
        "equipamento_principal_nome": "ResMed AirCurve 10 VAuto BiLevel",
        "mascara_recomendada_sku": "MSK-FPH-EVORA",
        "mascara_recomendada_nome": "Fisher & Paykel Evora Full Face",
        "insumos_cross_sell": "INS-RES-CLINE + INS-RES-FLT-HP + INS-CPAP-WIPES",
        "valor_total_pacote_brl": 11365.00,
        "condicao_comercial_sugerida": "Locação com assistência 24h (R$ 550/mês) ou Aquisição 12x de R$ 947,08 com emissão de Laudo para Reembolso Amil One",
        "argumentacao_venda_ia": "Paciente com IAH crítico (46.0), dessaturação severa (68%) e comorbidade cardíaca. Pressão de 15 cmH2O torna o CPAP comum desconfortável. O BiPAP AirCurve 10 reduz drasticamente a resistência expiratória (IPAP 15 / EPAP 11), estabilizando o ritmo cardíaco noturno. Fornecer relatório para reembolso do convênio Amil One.",
        "quebra_objecoes": "Paciente tem alto poder aquisitivo e foco em saúde cardiovascular. Enfatizar relatório semanal para o Dr. Henrique Vasconcellos.",
        "probabilidade_conversao": 0.96
    },
    {
        "recomendacao_id": "REC-004",
        "lead_id": "LEAD-1004",
        "nome_paciente": "Fernanda Lima de Oliveira",
        "equipamento_principal_sku": "CPAP-RES-MINI",
        "equipamento_principal_nome": "ResMed AirMini AutoSet (Kit Viagem)",
        "mascara_recomendada_sku": "MSK-RES-N20",
        "mascara_recomendada_nome": "AirFit N20 Nasal",
        "insumos_cross_sell": "Cápsulas HumidX Plus (Kit 3 un) + INS-CPAP-WIPES",
        "valor_total_pacote_brl": 6430.00,
        "condicao_comercial_sugerida": "10x de R$ 643,00 sem juros",
        "argumentacao_venda_ia": "Paciente jovem, ativa, executiva com viagens semanais e apneia leve (IAH 9.8). O AirMini é o único que cabe na bolsa de mão e dispensa carregar água destilada graças ao filtro HumidX. Máscara N20 oferece vedação segura sem marcas na pele.",
        "quebra_objecoes": "Comparar o ruído suave de 30 dBA (equivalente ao som de um sussurro) com o benefício de não ter que despachar bagagem.",
        "probabilidade_conversao": 0.82
    },
    {
        "recomendacao_id": "REC-005",
        "lead_id": "LEAD-1005",
        "nome_paciente": "Luiz Gustavo Moreira",
        "equipamento_principal_sku": "CPAP-BMC-G3A20",
        "equipamento_principal_nome": "BMC G3 A20 Auto CPAP com Tubo Aquecido",
        "mascara_recomendada_sku": "MSK-RES-N20",
        "mascara_recomendada_nome": "AirFit N20 Nasal",
        "insumos_cross_sell": "INS-RES-FLT-HP + INS-CPAP-WIPES",
        "valor_total_pacote_brl": 4205.00,
        "condicao_comercial_sugerida": "12x de R$ 350,41 sem juros ou Aluguel Econômico por R$ 190/mês",
        "argumentacao_venda_ia": "Excelente alternativa com umidificação inteligente pré-aquecida e ótimo custo benefício. Paciente com apneia posicional grave que se beneficia de alívio expiratório e tubo aquecido.",
        "quebra_objecoes": "Destacar a garantia integral de 2 anos com máquina reserva Luminar em caso de manutenção.",
        "probabilidade_conversao": 0.87
    }
]

HISTORICO_COMPRAS_TROCAS = [
    {
        "historico_id": "HIST-501",
        "paciente_id": "PAC-892",
        "nome_paciente": "Julio Cesar Brandão",
        "produto_sku": "CPAP-RES-AS10",
        "data_compra": "2024-06-15",
        "data_ultima_troca_mascara": "2025-11-10",
        "data_ultima_troca_filtro": "2026-05-15",
        "dias_desde_troca_mascara": 288,
        "alerta_reposicao": "URGENTE: Almofada de silicone com mais de 6 meses (risco de microvazamento)",
        "valor_recorrente_estimado_brl": 840.00
    },
    {
        "historico_id": "HIST-502",
        "paciente_id": "PAC-914",
        "nome_paciente": "Regina Silveira Camargo",
        "produto_sku": "CPAP-RES-AS11",
        "data_compra": "2025-02-20",
        "data_ultima_troca_mascara": "2026-02-10",
        "data_ultima_troca_filtro": "2026-06-01",
        "dias_desde_troca_mascara": 196,
        "alerta_reposicao": "RECOMENDADA: Troca de filtros hipoalergênicos e revisão da almofada N20",
        "valor_recorrente_estimado_brl": 450.00
    }
]

# -------------------------------------------------------------
# 2. WRITE CSV FILES
# -------------------------------------------------------------

def write_csv(data, filepath):
    if not data:
        return
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] CSV gerado: {filepath}")

write_csv(LEADS_PACIENTES, os.path.join(BQ_DATA_DIR, "leads_pacientes.csv"))
write_csv(CATALOGO_PRODUTOS, os.path.join(BQ_DATA_DIR, "catalogo_produtos.csv"))
write_csv(RECOMENDACOES_VENDEDOR, os.path.join(BQ_DATA_DIR, "recomendacoes_vendedor.csv"))
write_csv(HISTORICO_COMPRAS_TROCAS, os.path.join(BQ_DATA_DIR, "historico_compras_trocas.csv"))

# Copy to workspace google sheets
write_csv(LEADS_PACIENTES, os.path.join(WORKSPACE_DIR, "google_sheets", "CRM_Leads_Luminar_Saude.csv"))
write_csv(CATALOGO_PRODUTOS, os.path.join(WORKSPACE_DIR, "google_sheets", "Catalogo_Produtos_Precos.csv"))

# -------------------------------------------------------------
# 3. GENERATE BIGQUERY SQL SCRIPTS (DDL & QUERIES)
# -------------------------------------------------------------

SQL_SCHEMA = f"""-- BigQuery DDL: Dataset `{PROJECT_ID}.{DATASET_ID}`
-- Solução Luminar Saúde: Qualificação de Leads e Recomendações de CPAP com IA

CREATE SCHEMA IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}`
OPTIONS(
  location="US",
  description="Dataset de CRM, Diagnósticos de Sono e Catálogo Respiratório Luminar Saúde"
);

-- Tabela 1: Leads e Pacientes Qualificados
CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.leads_pacientes` (
  lead_id STRING NOT NULL,
  nome_paciente STRING NOT NULL,
  idade INT64,
  genero STRING,
  telefone STRING,
  email STRING,
  cidade STRING,
  estado STRING,
  medico_prescritor STRING,
  crm_medico STRING,
  especialidade_medico STRING,
  convenio STRING,
  diagnostico_cid STRING,
  iah FLOAT64,
  spo2_minima FLOAT64,
  spo2_media FLOAT64,
  pressao_titulada_cmh2o FLOAT64,
  respiracao_predominante STRING,
  presenca_ronco STRING,
  comorbidades STRING,
  sensibilidade_pressao STRING,
  score_prioridade INT64,
  urgencia_comercial STRING,
  status_funil STRING,
  data_entrada DATE
);

-- Tabela 2: Catálogo de Equipamentos e Insumos
CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.catalogo_produtos` (
  sku STRING NOT NULL,
  categoria STRING,
  fabricante STRING,
  modelo STRING,
  descricao STRING,
  faixa_pressao_cmh2o STRING,
  nivel_ruido_dba FLOAT64,
  umidificador_incluso STRING,
  peso_kg FLOAT64,
  preco_venda_brl NUMERIC,
  preco_aluguel_mensal_brl NUMERIC,
  indicacao_clinica STRING,
  itens_inclusos STRING,
  garantia_meses INT64,
  estoque_disponivel INT64
);

-- Tabela 3: Recomendações de Venda Geradas por IA (Gemini Copilot)
CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.recomendacoes_vendedor` (
  recomendacao_id STRING NOT NULL,
  lead_id STRING NOT NULL,
  nome_paciente STRING,
  equipamento_principal_sku STRING,
  equipamento_principal_nome STRING,
  mascara_recomendada_sku STRING,
  mascara_recomendada_nome STRING,
  insumos_cross_sell STRING,
  valor_total_pacote_brl NUMERIC,
  condicao_comercial_sugerida STRING,
  argumentacao_venda_ia STRING,
  quebra_objecoes STRING,
  probabilidade_conversao FLOAT64
);

-- Tabela 4: Histórico de Trocas e Reabastecimento de Insumos (Recorrência)
CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.historico_compras_trocas` (
  historico_id STRING NOT NULL,
  paciente_id STRING NOT NULL,
  nome_paciente STRING,
  produto_sku STRING,
  data_compra DATE,
  data_ultima_troca_mascara DATE,
  data_ultima_troca_filtro DATE,
  dias_desde_troca_mascara INT64,
  alerta_reposicao STRING,
  valor_recorrente_estimado_brl NUMERIC
);
"""

with open(os.path.join(BASE_DIR, "bigquery", "schema.sql"), "w", encoding="utf-8") as f:
    f.write(SQL_SCHEMA)
print("[OK] SQL Schema gerado.")

SQL_QUERIES = f"""-- BigQuery Analytics & BigQuery AI Queries para a Demonstração Luminar Saúde

-- 1. Visão 360 do Vendedor: Junção Lead + Catálogo + Prescrição Médica
SELECT 
  l.lead_id,
  l.nome_paciente,
  l.idade,
  l.iah AS indice_apneia_iah,
  CASE 
    WHEN l.iah >= 30 THEN 'Grave (Urgente)'
    WHEN l.iah >= 15 THEN 'Moderada'
    ELSE 'Leve'
  END AS classificacao_severidade,
  l.pressao_titulada_cmh2o,
  l.respiracao_predominante,
  r.equipamento_principal_nome,
  r.mascara_recomendada_nome,
  r.valor_total_pacote_brl,
  r.probabilidade_conversao,
  r.argumentacao_venda_ia
FROM `{PROJECT_ID}.{DATASET_ID}.leads_pacientes` l
JOIN `{PROJECT_ID}.{DATASET_ID}.recomendacoes_vendedor` r ON l.lead_id = r.lead_id
ORDER BY l.score_prioridade DESC;

-- 2. Oportunidades de Venda Recorrente (Insumos e Troca de Máscara com > 6 meses)
SELECT 
  paciente_id,
  nome_paciente,
  dias_desde_troca_mascara,
  alerta_reposicao,
  valor_recorrente_estimado_brl
FROM `{PROJECT_ID}.{DATASET_ID}.historico_compras_trocas`
WHERE dias_desde_troca_mascara > 180;

-- 3. Exemplo de Consulta BigQuery AI com ML.GENERATE_TEXT (Gemini 1.5 Flash na Vertex AI / BigQuery)
/*
SELECT 
  lead_id,
  nome_paciente,
  ml_generate_text_result['candidates'][0]['content']['parts'][0]['text'] AS pitch_comercial_customizado
FROM ML.GENERATE_TEXT(
  MODEL `{PROJECT_ID}.{DATASET_ID}.gemini_flash_model`,
  (
    SELECT 
      lead_id, 
      nome_paciente,
      CONCAT(
        'Você é o Copiloto Comercial da Luminar Saúde. Redija um pitch de WhatsApp empático e convincente para o paciente ', 
        nome_paciente, 
        ', diagnosticado com Apneia do Sono (IAH: ', CAST(iah AS STRING), 
        ', pressão prescrita: ', CAST(pressao_titulada_cmh2o AS STRING), ' cmH2O).',
        ' Equipamento sugerido: AirSense 11. Destaque o alívio imediato do cansaço e a garantia de adaptação de 30 dias.'
      ) AS prompt
    FROM `{PROJECT_ID}.{DATASET_ID}.leads_pacientes`
    WHERE score_prioridade >= 90
  ),
  STRUCT(
    0.3 AS temperature,
    500 AS max_output_tokens
  )
);
*/
"""

with open(os.path.join(BASE_DIR, "bigquery", "analytics_queries.sql"), "w", encoding="utf-8") as f:
    f.write(SQL_QUERIES)
print("[OK] SQL Queries gerado.")

# -------------------------------------------------------------
# 4. GENERATE REALISTIC PDF REPORTS FOR GCS & DRIVE
# -------------------------------------------------------------

def build_pdf_report(filename, title, subtitle, doctor_info, patient_dict, clinical_summary, conclusions):
    if not HAS_REPORTLAB:
        print(f"[SKIP] PDF '{os.path.basename(filename)}' ignorado (reportlab não instalado).")
        return
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#0D47A1")  # Dark Blue Luminar
    secondary_color = colors.HexColor("#00838F") # Cyan Medical
    text_dark = colors.HexColor("#1A237E")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=secondary_color,
        spaceAfter=12
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.black,
        spaceAfter=6
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.black
    )
    
    elements = []
    
    # Header Banner
    elements.append(Paragraph("<b>LUMINAR SAÚDE</b> | Medicina Respiratória & Terapias do Sono", title_style))
    elements.append(Paragraph(f"<b>{title}</b> — <i>{subtitle}</i>", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=12))
    
    # Doctor / Clinic Box
    doc_table_data = [
        [
            Paragraph(f"<b>Médico Responsável:</b> {doctor_info['nome']}", body_style),
            Paragraph(f"<b>CRM:</b> {doctor_info['crm']}", body_style)
        ],
        [
            Paragraph(f"<b>Especialidade:</b> {doctor_info['especialidade']}", body_style),
            Paragraph(f"<b>Centro Diagnóstico:</b> Instituto do Sono Luminar - Unidade Jardins", body_style)
        ]
    ]
    t_doc = Table(doc_table_data, colWidths=[270, 270])
    t_doc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F4F8")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#B0BEC5")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_doc)
    elements.append(Spacer(1, 10))
    
    # Patient Data Table
    elements.append(Paragraph("DADOS DO PACIENTE & DADOS CLÍNICOS", section_style))
    pt_table_data = [
        [
            Paragraph(f"<b>Paciente:</b> {patient_dict['nome_paciente']}", body_style),
            Paragraph(f"<b>Idade:</b> {patient_dict['idade']} anos ({patient_dict['genero']})", body_style)
        ],
        [
            Paragraph(f"<b>Convênio:</b> {patient_dict['convenio']}", body_style),
            Paragraph(f"<b>Cidade/UF:</b> {patient_dict['cidade']}/{patient_dict['estado']}", body_style)
        ],
        [
            Paragraph(f"<b>Diagnóstico:</b> {patient_dict['diagnostico_cid']}", bold_body_style),
            Paragraph(f"<b>Data do Exame:</b> {patient_dict['data_entrada']}", body_style)
        ]
    ]
    t_pt = Table(pt_table_data, colWidths=[270, 270])
    t_pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CFD8DC")),
    ]))
    elements.append(t_pt)
    elements.append(Spacer(1, 10))
    
    # Polysomnography Parameters Table
    elements.append(Paragraph("PARÂMETROS POLISSONOGRÁFICOS & TITULAÇÃO", section_style))
    psg_data = [
        ["Parâmetro Avaliado", "Resultado Obtido", "Valor de Referência", "Interpretação Clínica"],
        ["Índice de Apneia/Hipopneia (IAH)", f"{patient_dict['iah']} eventos/hora", "< 5 /h (Normal)", "Grave (Acurado)" if patient_dict['iah'] >= 30 else ("Moderada" if patient_dict['iah'] >= 15 else "Leve")],
        ["Saturação O2 Mínima (SpO2)", f"{patient_dict['spo2_minima']} %", "> 90 %", "Hipoxemia Severa" if patient_dict['spo2_minima'] < 80 else "Hipoxemia Moderada"],
        ["Saturação O2 Média", f"{patient_dict['spo2_media']} %", "> 95 %", "Abaixo do normal"],
        ["Pressão Titulada Recomendada", f"{patient_dict['pressao_titulada_cmh2o']} cmH2O", "Individual", "Pressão Ótima"],
        ["Padrão Respiratório", f"{patient_dict['respiracao_predominante']}", "Nasal", "Risco de ressecamento oral" if "Oral" in patient_dict['respiracao_predominante'] else "Normal"],
        ["Intensidade do Ronco", f"{patient_dict['presenca_ronco']}", "Ausente", "Frequente e audível"]
    ]
    t_psg = Table(psg_data, colWidths=[150, 110, 110, 170])
    t_psg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('PADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#90A4AE")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8F9FA"), colors.white])
    ]))
    elements.append(t_psg)
    elements.append(Spacer(1, 10))
    
    # Clinical Analysis text
    elements.append(Paragraph("DISCUSSÃO CLÍNICA & RECOMENDAÇÃO TERAPÊUTICA", section_style))
    for p in clinical_summary:
        elements.append(Paragraph(p, body_style))
    elements.append(Spacer(1, 8))
    
    # Conclusions & Prescribed Device
    elements.append(Paragraph("CONDUTA MÉDICA & PRESCRIÇÃO", section_style))
    concl_table_data = [
        [Paragraph(f"<b>Conduta:</b> {conclusions['conduta']}", bold_body_style)],
        [Paragraph(f"<b>Tipo de Equipamento Prescrito:</b> {conclusions['equipamento']}", body_style)],
        [Paragraph(f"<b>Interface / Máscara Recomendada:</b> {conclusions['mascara']}", body_style)],
        [Paragraph(f"<b>Acessórios / Umidificação:</b> {conclusions['acessorios']}", body_style)],
        [Paragraph(f"<b>Acompanhamento:</b> {conclusions['acompanhamento']}", body_style)]
    ]
    t_concl = Table(concl_table_data, colWidths=[540])
    t_concl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E8EAF6")),
        ('BOX', (0,0), (-1,-1), 1, primary_color),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_concl)
    elements.append(Spacer(1, 15))
    
    # Doctor Signature Footer
    elements.append(Paragraph(f"____________________________________________<br/><b>{doctor_info['nome']}</b><br/>{doctor_info['crm']} — {doctor_info['especialidade']}", ParagraphStyle(
        'DocSig', parent=styles['Normal'], alignment=1, fontSize=9, leading=12
    )))
    
    doc.build(elements)
    print(f"[OK] PDF Laudo gerado: {filename}")

# Generate PDFs for Top Patients
for pt in LEADS_PACIENTES:
    pdf_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", f"laudo_psg_{pt['nome_paciente'].split()[0].lower()}_{pt['nome_paciente'].split()[1].lower()}.pdf")
    txt_path = os.path.join(STORAGE_DIR, "laudos_polissonografia", f"laudo_psg_{pt['nome_paciente'].split()[0].lower()}_{pt['nome_paciente'].split()[1].lower()}.txt")
    
    doc_info = {
        "nome": pt['medico_prescritor'],
        "crm": pt['crm_medico'],
        "especialidade": pt['especialidade_medico']
    }
    
    clinical_summary = [
        f"Paciente de {pt['idade']} anos, encaminhado com histórico de sonolência diurna excessiva, roncos frequentes e paradas respiratórias observadas pelo cônjuge. Apresenta comorbidades: {pt['comorbidades']}.",
        f"A polissonografia noturna demonstrou arquitetura do sono fragmentada, com predomínio de sono superficial e supressão de sono REM. Foram registrados múltiplos eventos obstrutivos resultando em IAH de {pt['iah']} ev/h com queda acentuada de saturação para {pt['spo2_minima']}%.",
        f"Durante a segunda metade da noite (titulação pressórica com CPAP Auto), obteve-se abolição completa dos roncos e normalização do índice respiratório na pressão de {pt['pressao_titulada_cmh2o']} cmH2O."
    ]
    
    conclusions = {
        "conduta": "Indicação formal de terapia com Pressão Positiva Contínua nas Vias Aéreas (CPAP/BiPAP)",
        "equipamento": "CPAP Automático com alívio expiratório (AutoSet / EPR) ou BiPAP em caso de alta resistência.",
        "mascara": f"Máscara {'Facial / Oronasal (devido à respiração oral/mista e pressão elevada)' if 'Oral' in pt['respiracao_predominante'] else 'Nasal compacta ou Almofadas Nasais'}.",
        "acessorios": "Umidificador aquecido obrigatório para proteção de mucosa e tubo com controle de temperatura.",
        "acompanhamento": "Reavaliação clínica com relatório de adesão e eficácia do telemonitoramento (AirView) em 30 dias."
    }
    
    build_pdf_report(pdf_path, "LAUDO DE POLISSONOGRAFIA NOTURNA COM TITULAÇÃO DE CPAP", "Exame Diagnóstico Computadorizado de Sono", doc_info, pt, clinical_summary, conclusions)
    
    # Also write text version for text processing / RAG
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write(f"=== LAUDO POLISSONOGRAFIA LUMINAR SAÚDE ===\n")
        f_txt.write(f"Paciente: {pt['nome_paciente']}\nIdade: {pt['idade']} | Genero: {pt['genero']}\n")
        f_txt.write(f"Médico Prescritor: {pt['medico_prescritor']} ({pt['crm_medico']})\n")
        f_txt.write(f"Diagnóstico: {pt['diagnostico_cid']}\n")
        f_txt.write(f"IAH: {pt['iah']} ev/h | SpO2 Mínima: {pt['spo2_minima']}% | Pressão Titulada: {pt['pressao_titulada_cmh2o']} cmH2O\n")
        f_txt.write(f"Padrão: {pt['respiracao_predominante']} | Comorbidades: {pt['comorbidades']}\n")
        f_txt.write(f"Prescrição: {conclusions['equipamento']} + {conclusions['mascara']}\n")
    print(f"[OK] TXT Laudo gerado: {txt_path}")

# -------------------------------------------------------------
# 5. GENERATE WORKSPACE GMAIL TEMPLATES & PLAYBOOKS
# -------------------------------------------------------------

GMAIL_1 = """De: Dr. Fernando Albuquerque <fernando.albuquerque@clinicasul.med.br>
Para: Atendimento Luminar Saúde <consultores@luminarsaude.com.br>
Assunto: Encaminhamento de Paciente com Apneia Grave - Roberto Silveira Santos
Data: 20 de Agosto de 2026 às 14:32

Prezada equipe comercial e clínica da Luminar Saúde,

Encaminho em anexo o laudo polissonográfico e a receita médica do paciente Roberto Silveira Santos (52 anos).
Diagnóstico: Apneia Obstrutiva do Sono Grave (IAH 38.4/h, dessaturação até 74%).
Pressão titulada ótima em laboratório: 12 cmH2O.

Observações clínicas importantes para o vendedor:
- O paciente é respirador bucal/misto intenso durante a noite. Por favor, recomendem máscara Facial/Oronasal (ex: AirFit F20 tamanho G) para evitar escape de ar.
- Necessita umidificação aquecida ativa (tubo ClimateLine) devido a queixas de garganta seca.
- Solicito vincular o equipamento ao meu painel de telemonitoramento AirView para acompanhamento da adesão semanal.

Por favor, entrem em contato com o paciente e ofereçam o programa de adaptação assistida.

Atenciosamente,

Dr. Fernando Albuquerque
Pneumologista e Especialista em Medicina do Sono
CRM-SP 142.890
"""

with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "01_encaminhamento_medico.md"), "w", encoding="utf-8") as f:
    f.write(GMAIL_1)

GMAIL_2 = """De: Lucas Viana - Especialista do Sono <lucas.viana@luminarsaude.com.br>
Para: Roberto Silveira Santos <roberto.silveira@email.com>
Cc: Dr. Fernando Albuquerque <fernando.albuquerque@clinicasul.med.br>
Assunto: Proposta Personalizada de Tratamento CPAP - Luminar Saúde & Dr. Fernando
Data: 21 de Agosto de 2026 às 09:15

Olá, Sr. Roberto, tudo bem?

Recebemos o laudo do seu exame de sono e a prescrição detalhada enviada pelo Dr. Fernando Albuquerque.
Com base nas suas características (IAH 38.4 e respiração mista com pressão 12 cmH2O), estruturamos um pacote sob medida para que o senhor durma a primeira noite com conforto total, sem ruído e sem acordar com a boca seca.

📦 PACOTE RECOMENDADO: LUMINAR TOTAL COMFORT RESMED
1. CPAP Automático ResMed AirSense 11 AutoSet
   - Ajuste automático de pressão respiração a respiração.
   - Tecnologia EPR (alívio inteligente de pressão durante a expiração).
   - Conectividade 4G nativa para o Dr. Fernando acompanhar seu sono pelo app AirView.
2. Máscara Oronasal ResMed AirFit F20 (Silicone InfinitySeal)
   - Máxima vedação mesmo dormindo de lado, sem marcas no rosto.
3. Tubo Térmico ClimateLineAir
   - Mantém o ar na temperatura e umidade exatas, prevenindo água no tubo.
4. Kit de Filtros Hipoalergênicos + Frasco de Lenços de Limpeza CPAP Wipes (Cortesia Luminar)

💳 CONDIÇÕES COMERCIAIS EXCLUSIVAS:
- Valor Total do Pacote: R$ 7.345,00
- Parcelamento: 12x de R$ 612,08 sem juros no cartão
- Pagamento à vista (PIX): R$ 6.757,40 (8% de desconto)
- Ou Locação com opção de compra: R$ 290,00/mês

🛡️ GARANTIA LUMINAR ADAPTAÇÃO 30 DIAS:
Se o senhor não se adaptar com o modelo ou tamanho da máscara nos primeiros 30 dias, trocamos gratuitamente na sua residência!

Podemos agendar a visita do nosso fisioterapeuta na sua casa hoje às 16h ou amanhã pela manhã para entregar e configurar o equipamento?

Fico no aguardo!

Lucas Viana
Consultor Especialista em Terapias Respiratórias
Luminar Saúde | WhatsApp: (11) 99888-7766
"""

with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "02_proposta_comercial_paciente.md"), "w", encoding="utf-8") as f:
    f.write(GMAIL_2)

GMAIL_3 = """📲 SCRIPT OMNICHANNEL / WHATSAPP (VENDEDOR LUMINAR SAÚDE)

[MENSAGEM 1 - ABORDAGEM INICIAL EMPÁTICA]
"Olá, Roberto! Aqui é o Lucas, consultor especialista em sono da Luminar Saúde. O Dr. Fernando Albuquerque nos encaminhou seu laudo de polissonografia para prepararmos sua solução de CPAP com todo o carinho e agilidade. Como você está se sentindo hoje?"

[MENSAGEM 2 - APRESENTAÇÃO DA SOLUÇÃO E VÍDEO DEMO]
"Roberto, analisamos que sua pressão é 12 cmH2O e você respira pela boca à noite. Montamos um kit especial com o novo ResMed AirSense 11 e a máscara AirFit F20, que não machuca o rosto e evita que o ar escape.
Gravei um vídeo rápido de 1 minuto mostrando como ele é pequeno e silencioso: [Link Vídeo Luminar Demonstração]"

[MENSAGEM 3 - QUEBRA DE OBJEÇÃO DE PREÇO / MEDO DE NÃO ACOSTUMAR]
"Sei que começar a usar o CPAP pode gerar dúvidas se vai se acostumar. Por isso, a Luminar te dá o Programa 'Sono Perfeito 30 Dias': nosso fisioterapeuta vai na sua casa, ajusta a máscara no seu rosto e se precisar trocar o modelo, trocamos sem custo nenhum! Além disso, parcelamos em 12x sem juros ou você pode começar alugando."

[MENSAGEM 4 - CALL TO ACTION]
"Consigo reservar um AirSense 11 com o Dr. Fernando monitorando seu sono já a partir de amanhã à noite. Prefere que eu envie o link de pagamento ou agendamos a entrega presencial?"
"""

with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "03_script_whatsapp_vendedor.md"), "w", encoding="utf-8") as f:
    f.write(GMAIL_3)

GMAIL_4 = """De: Suporte Clínico Luminar Saúde <suporte@luminarsaude.com.br>
Para: Roberto Silveira Santos <roberto.silveira@email.com>
Assunto: 7 Dias de Terapia CPAP Concluídos! Parabéns pela Adesão! 🌟
Data: 28 de Agosto de 2026 às 10:00

Prezado Sr. Roberto,

Parabéns! Nosso sistema de telemonitoramento AirView registrou que o senhor utilizou seu AirSense 11 por uma média de 6 horas e 45 minutos por noite nos últimos 7 dias!
Seu índice de IAH caiu de 38.4 para impressionantes 1.2 eventos/hora (sono 100% reparador!).

Dicas para manter o tratamento perfeito:
1. Lembre-se de higienizar a almofada da máscara F20 diariamente com seus lenços CPAP Wipes.
2. Troque a água do umidificador diariamente por água filtrada/destilada.
3. Seus próximos filtros hipoalergênicos serão entregues automaticamente em seu endereço no mês que vem através do Clube Luminar Recorrência.

Qualquer dúvida, nossa equipe de fisioterapia está à sua disposição 24 horas por dia pelo WhatsApp.

Luminar Saúde — Respirar bem é viver melhor.
"""

with open(os.path.join(WORKSPACE_DIR, "gmail_templates", "04_pos_venda_adesao_telemonitoramento.md"), "w", encoding="utf-8") as f:
    f.write(GMAIL_4)

# -------------------------------------------------------------
# 6. GENERATE GOOGLE DRIVE PLAYBOOK & CLINICAL DOSSIER
# -------------------------------------------------------------

PLAYBOOK = """# 📘 Playbook de Vendas Luminar Saúde: Qualificação e Conversão de CPAP

## 1. Matriz de Decisão Clínica para o Consultor Comercial

| Perfil do Paciente | Sintomas & Exame | Equipamento Recomendado | Máscara Indicada | Insumos Cruzados (Cross-Sell) |
| :--- | :--- | :--- | :--- | :--- |
| **Apneia Grave + Respirador Oral** | IAH > 30, Pressão > 11 cmH2O, boca aberta | **AirSense 11 AutoSet** | **AirFit F20 (Facial)** | Tubo Térmico ClimateLineAir + Filtros Hipoalergênicos + Wipes |
| **Apneia Moderada + Claustrofobia** | IAH 15-30, Respiração Nasal, ansiedade | **AirSense 10 AutoSet** | **AirFit P10 (Almofadas)** | Filtros ultrafinos + Fixador Elástico reserva |
| **Pressões Extremas (> 14 cmH2O) / Cardiopatia** | IAH > 40, dessaturação < 75%, IC / FA | **AirCurve 10 VAuto (BiPAP)** | **Evora Full Face** | Tubo Aquecido + Umidificação Nível 5 + Telemonitoramento semanal |
| **Executivo / Viajante Frequente** | IAH leve-moderado, viagens semanais | **AirMini Portátil** | **AirFit N20 Nasal** | Cápsulas HumidX Plus + Bolsa de Viagem Premium |

## 2. Gatilhos de Venda Rápida
- **Gatilho da Saúde Preventiva**: Ligar o tratamento à redução de 70% no risco de infarto, AVC e hipertensão refratária.
- **Gatilho da Parceria Médica**: O médico de confiança (ex: Dr. Fernando) receberá relatórios semanais automáticos.
- **Gatilho da Garantia Incondicional**: Programa Luminar Adaptação 30 Dias (troca grátis de máscara).

## 3. Estratégia de Recorrência (LTV & Pós-Venda)
- Mês 1: Revisão de adesão via AirView e envio de novo filtro hipoalergênico.
- Mês 6: Troca obrigatória da almofada de silicone da máscara (evita perda de vedação e alergias).
- Mês 12: Troca completa do conjunto máscara + traqueia + câmara de água.
"""

with open(os.path.join(WORKSPACE_DIR, "google_drive", "Playbook_Vendas_Luminar_Saude.md"), "w", encoding="utf-8") as f:
    f.write(PLAYBOOK)

print("\n🎉 TODOS OS ASSETS FORAM GERADOS COM SUCESSO!")
