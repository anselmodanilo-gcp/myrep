# 🫁 Luminar Saúde — Demo de Qualificação de Leads e Recomendações de CPAP com IA

**Projeto Argolis:** `abiding-arch-505313-m3`  
**Dataset BigQuery:** `luminar_saude`  
**Bucket Cloud Storage:** `gs://abiding-arch-505313-m3-luminar-saude`  
**Vertical:** Healthcare & Life Sciences / Medical Devices / Vendas Consultivas  

---

## 🎯 Visão Geral do Cenário de Negócio

A **Luminar Saúde** é uma empresa especializada em medicina do sono e soluções respiratórias (CPAPs, BiPAPs, máscaras, traqueias e insumos).

### O Desafio do Vendedor:
- Receber laudos de polissonografia complexos e receitas médicas com termos técnicos (IAH, SpO2, pressão titulada em cmH2O, respiração oral vs nasal).
- Traduzir a prescrição em um **pacote de produtos compatível** (Equipamento + Máscara adequada + Tubo aquecido + Filtros).
- Quebrar objeções comuns do paciente (claustrofobia, receio do ruído, preço) com argumentos empáticos e científicos.
- Acompanhar a **recorrência** (troca de almofadas a cada 6 meses e filtros a cada 60 dias).

### A Solução com Google Cloud & Workspace:
Equipar os consultores comerciais com um **Copiloto com Gemini e BigQuery**, acelerando o ciclo comercial de semanas para poucos minutos.

---

## 🏗️ Estrutura de Assets Criados

```bash
demo_saude/
├── app.py                          # Aplicação Web Streamlit (Painel Interativo do Vendedor)
├── deploy_gcp.sh                   # Script de automação CLI (gcloud / bq / storage)
├── deploy_gcp.py                   # Script de automação Python (google-cloud SDKs)
├── generate_assets.py              # Gerador de CSVs, PDFs de laudos, SQLs e templates
│
├── bigquery/                       # Assets BigQuery
│   ├── schema.sql                  # DDL de criação das 4 tabelas
│   ├── analytics_queries.sql       # Consultas analíticas e BigQuery AI (ML.GENERATE_TEXT)
│   └── data/                       # Dados tabulares (CSV)
│       ├── leads_pacientes.csv
│       ├── catalogo_produtos.csv
│       ├── recomendacoes_vendedor.csv
│       └── historico_compras_trocas.csv
│
├── storage/                        # Assets Cloud Storage (gs://abiding-arch-505313-m3-luminar-saude)
│   ├── laudos_polissonografia/     # Laudos reais gerados em PDF e TXT para OCR multimodal
│   │   ├── laudo_psg_roberto_silveira.pdf
│   │   ├── laudo_psg_mariana_costa.pdf
│   │   └── ...
│   ├── receitas_medicas/           # Prescrições médicas com CRM e dosagem de pressão
│   └── catalogos_manuais/          # Fichas técnicas e especificações de fabricantes
│
└── workspace/                      # Assets Google Workspace & Drive
    ├── gmail_templates/            # Modelos de e-mail e scripts de WhatsApp
    │   ├── 01_encaminhamento_medico.md
    │   ├── 02_proposta_comercial_paciente.md
    │   ├── 03_script_whatsapp_vendedor.md
    │   └── 04_pos_venda_adesao_telemonitoramento.md
    ├── google_drive/               # Playbooks de vendas e matrizes de decisão
    │   └── Playbook_Vendas_Luminar_Saude.md
    └── google_sheets/              # Planilhas formatadas para importação imediata
        ├── CRM_Leads_Luminar_Saude.csv
        └── Catalogo_Produtos_Precos.csv
```

---

## 🚀 Como Executar a Demonstração

### 1. Iniciar a Aplicação Web Interativa (Streamlit)
```bash
cd /usr/local/google/home/anselmodanilo/dev/demo_saude
source venv/bin/activate
streamlit run app.py
```
Acesse no navegador através do endereço local exibido no terminal.

### 2. Realizar o Deploy dos Assets no Projeto GCP (`abiding-arch-505313-m3`)
```bash
./deploy_gcp.sh
```
*Ou via Python:*
```bash
python deploy_gcp.py
```

---

## 💡 Roteiro de Demonstração (Demo Script)

1. **Abertura (Contexto de Saúde):**
   - Apresente o lead **Roberto Silveira Santos** no Radar de Leads.
   - Mostre que ele tem **Apneia Grave (IAH 38.4)** e respira pela boca com pressão alta (**12 cmH2O**).
   - Mostre o **Laudo em PDF** gerado pela clínica anexado no Storage.

2. **Copiloto de Recomendação de Produtos (Matching Inteligente):**
   - Mostre a sugestão da IA: **AirSense 11 AutoSet** + **Máscara Facial F20** + **Tubo Aquecido ClimateLine**.
   - Destaque o racional da IA: a máscara facial é crítica para quem respira pela boca com mais de 10 cmH2O, e o tubo aquecido evita água condensada.
   - Mostre a **Quebra de Objeções** personalizada para o vendedor falar com segurança sobre o programa "Adaptação 30 Dias".

3. **Comunicação Omnichannel (Gmail / WhatsApp):**
   - Mostre o e-mail comercial personalizado enviado com 1 clique.
   - Mostre o script empático de WhatsApp pronto para envio.

4. **Recorrência & LTV:**
   - Mostre a aba de **Recorrência** identificando pacientes que usam a mesma máscara há mais de 6 meses (oportunidade automática de upsell de insumos).

5. **BigQuery & Gemini na Nuvem:**
   - Exiba a consulta SQL no BigQuery unificando leads e recomendações em tempo real.
