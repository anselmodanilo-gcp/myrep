# 🎬 Roteiro Oficial de Apresentação da Demo — Luminar Saúde
**Google Cloud & Workspace para Terapias Respiratórias e Medicina do Sono**

---

## 🎯 Objetivo da Demonstração
Demonstrar como a **Luminar Saúde** utiliza o **Google Cloud (Vertex AI, Gemini, BigQuery, Cloud Storage e Cloud Run)** e o **Google Workspace (Gmail e Drive)** para equipar seus consultores comerciais com um **Copiloto Inteligente**, acelerando o ciclo comercial de semanas para minutos, aumentando a taxa de conversão e a receita recorrente de insumos (LTV).

---

## 🧭 Estrutura da Apresentação em 5 Atos

```
[Ato 1: O Desafio] ➡️ [Ato 2: Cockpit & Laudos] ➡️ [Ato 3: Matching Clínico IA] ➡️ [Ato 4: Live Lead Simulator] ➡️ [Ato 5: Recorrência & LTV]
```

---

### 📍 ATO 1: O Desafio do Negócio (1 a 2 minutos)
* **Narrativa do Apresentador:**
  > "Na medicina respiratória e do sono, o vendedor não vende apenas um produto, ele vende uma terapia médica. Quando um paciente é diagnosticado com apneia obstrutiva do sono, o vendedor recebe laudos polissonográficos com termos complexos: IAH, saturação mínima, pressão titulada em cmH2O. Traduzir isso na máscara certa, no CPAP ideal e quebrar o medo de claustrofobia do paciente demorava dias. Com a plataforma de IA da Luminar Saúde, o consultor comercial tem um Copiloto em tempo real."

---

### 📍 ATO 2: Cockpit Comercial & Extração Multimodal de Laudos (3 minutos)
* **Onde clicar na tela:** Menu Lateral 👉 **`1. Cockpit Comercial & Qualificação`**
* **O que mostrar:**
  1. Destaque os cartões de métricas superiores: **Taxa de prioridade alta (80%)**, **Ticket Médio com Cross-Sell** e **Ciclo Comercial reduzido em 55%**.
  2. Selecione o paciente **Roberto Silveira Santos**.
  3. Aponte o alerta vermelho: **Apneia Obstrutiva Grave (IAH 38.4 ev/h, SpO2 mínima de 74%)**.
  4. Mostre a caixa à direita com o **extrato do Laudo Polissonográfico** extraído diretamente do PDF armazenado no Cloud Storage (`gs://abiding-arch-505313-m3-luminar-saude`).
* **Mensagem de Impacto:**
  > "O Gemini leu o laudo em PDF em milissegundos, estruturou os parâmetros no BigQuery e classificou a urgência médica imediatamente."

---

### 📍 ATO 3: Copiloto de Recomendação & Matching de Catálogo (3 minutos)
* **Onde clicar na tela:** Menu Lateral 👉 **`2. Copiloto de Recomendação (CPAP/Máscaras)`**
* **O que mostrar:**
  1. Veja o pacote montado pela IA para o **Roberto Silveira Santos**:
     - **Equipamento:** *ResMed AirSense 11 AutoSet* (com alívio expiratório EPR e conexão celular).
     - **Máscara:** *ResMed AirFit F20 Full Face* (Tamanho G).
     - **Insumos Cross-Sell:** *Tubo Térmico ClimateLineAir + Filtros Hipoalergênicos + CPAP Wipes*.
  2. Leia o **Racional Clínico da IA**: *Como o paciente respira pela boca e a pressão é alta (12 cmH2O), a máscara facial é obrigatória para evitar vazamento de ar e ressecamento.*
  3. Mostre a seção **Quebra de Objeções**: argumentos prontos para contornar o medo do paciente com o programa *Luminar Adaptação 30 Dias* (troca grátis de máscara).
  4. Clique nos botões de ação rápida: **`📲 Disparar Proposta no WhatsApp`** e **`📧 Gerar E-mail Formal`**.

---

### 📍 ATO 4: Criação de Lead em Tempo Real (Live Lead Simulator) (3 minutos)
* **Onde clicar na tela:** Menu Lateral 👉 **`3. Gerador de Clientes em Tempo Real`**
* **O que demonstrar ao vivo:**
  1. Mostre os botões de **1-Clique**:
     - Clique em **`🤧 Paciente Rinite & Claustrofobia`** ou **`✈️ Paciente Executivo Viagem`**.
     - O sistema injetará instantaneamente o novo lead no BigQuery e atualizará a base!
  2. Volte ao **Cockpit** e mostre que a paciente **Juliana Silveira** (com rinite e claustrofobia) já foi qualificada, e a IA recomendou a **Máscara AirFit P10 (de apenas 45g)** e **Filtros Antialérgicos**.
* **Mensagem de Impacto:**
  > "Isso demonstra a reatividade em tempo real da arquitetura: qualquer nova receita recebida via formulário, WhatsApp ou integração de clínicas médicas é qualificada instantaneamente."

---

### 📍 ATO 5: Agent Platform, MCP Tools & Workspace Integrado (3 minutos)
* **Onde clicar na tela:** Menu Lateral 👉 **`4. Agent Platform & MCP Playground`** e **`5. Simulador Workspace`**
* **O que demonstrar:**
  1. No **Agent Playground**, faça uma pergunta interativa ou selecione:
     - *"O paciente Carlos Eduardo tem pressão de 15 cmH2O e queixa de cansaço. Devo indicar CPAP ou BiPAP?"*
     - Mostre o Agent chamando a Tool MCP `consultar_paciente` e explicando clinicamente por que o **BiPAP AirCurve 10** é indispensável para proteger a saúde cardiovascular do paciente.
  2. No **Simulador Workspace**, mostre o e-mail de encaminhamento do Pneumologista no Gmail, a proposta personalizada enviada ao paciente e o acompanhamento de telemetria após 7 dias de uso.
  3. Finalize na aba **`6. Recorrência & LTV`**, mostrando como o sistema gera receita recorrente identificando almofadas de silicone com mais de 6 meses de uso.

---

## 🏆 Resumo do Valor de Negócio (Fechamento)
1. **+35% de Conversão Comercial**: O vendedor fala com a linguagem do médico e quebra o medo do paciente com autoridade.
2. **Zero Erro de Compatibilidade**: Máscaras, traqueias e pressões sempre 100% corretas para a prescrição.
3. **+22% de Receita Recorrente (LTV)**: Automação da reposição periódica de filtros e almofadas.
