-- BigQuery DDL: Dataset `abiding-arch-505313-m3.luminar_saude`
-- Solução Luminar Saúde: Qualificação de Leads e Recomendações de CPAP com IA

CREATE SCHEMA IF NOT EXISTS `abiding-arch-505313-m3.luminar_saude`
OPTIONS(
  location="US",
  description="Dataset de CRM, Diagnósticos de Sono e Catálogo Respiratório Luminar Saúde"
);

-- Tabela 1: Leads e Pacientes Qualificados
CREATE OR REPLACE TABLE `abiding-arch-505313-m3.luminar_saude.leads_pacientes` (
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
CREATE OR REPLACE TABLE `abiding-arch-505313-m3.luminar_saude.catalogo_produtos` (
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
CREATE OR REPLACE TABLE `abiding-arch-505313-m3.luminar_saude.recomendacoes_vendedor` (
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
CREATE OR REPLACE TABLE `abiding-arch-505313-m3.luminar_saude.historico_compras_trocas` (
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
