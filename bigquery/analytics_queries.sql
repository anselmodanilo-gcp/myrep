-- BigQuery Analytics & BigQuery AI Queries para a Demonstração Luminar Saúde

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
FROM `abiding-arch-505313-m3.luminar_saude.leads_pacientes` l
JOIN `abiding-arch-505313-m3.luminar_saude.recomendacoes_vendedor` r ON l.lead_id = r.lead_id
ORDER BY l.score_prioridade DESC;

-- 2. Oportunidades de Venda Recorrente (Insumos e Troca de Máscara com > 6 meses)
SELECT 
  paciente_id,
  nome_paciente,
  dias_desde_troca_mascara,
  alerta_reposicao,
  valor_recorrente_estimado_brl
FROM `abiding-arch-505313-m3.luminar_saude.historico_compras_trocas`
WHERE dias_desde_troca_mascara > 180;

-- 3. Exemplo de Consulta BigQuery AI com ML.GENERATE_TEXT (Gemini 1.5 Flash na Vertex AI / BigQuery)
/*
SELECT 
  lead_id,
  nome_paciente,
  ml_generate_text_result['candidates'][0]['content']['parts'][0]['text'] AS pitch_comercial_customizado
FROM ML.GENERATE_TEXT(
  MODEL `abiding-arch-505313-m3.luminar_saude.gemini_flash_model`,
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
    FROM `abiding-arch-505313-m3.luminar_saude.leads_pacientes`
    WHERE score_prioridade >= 90
  ),
  STRUCT(
    0.3 AS temperature,
    500 AS max_output_tokens
  )
);
*/
