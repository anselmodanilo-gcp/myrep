# 🎬 Roteiro Oficial de Demonstração — Luminar Saúde com Gemini Enterprise
**Google Cloud & Gemini Enterprise para Terapias Respiratórias e Medicina do Sono**

---

## 🎯 Conceito Arquitetural da Demo

1. **Gemini Enterprise (Ponto de Acesso Único do Usuário):**
   - É a interface única onde o consultor comercial interage para consultar dados de pacientes no **BigQuery**, ler laudos e prescrições em PDF no **Cloud Storage** e acionar ferramentas do **MCP Server**.
2. **Gerenciador da Demo no Cloud Run (Backstage & Control Plane):**
   - Ambiente de controle para o apresentador injetar novos leads, gerar cenários ao vivo e resetar a base de dados.

---

## 🧭 Estrutura da Apresentação em 5 Atos com Prompts do Gemini Enterprise

```
[Ato 1: O Desafio & Fila de Leads] ➡️ [Ato 2: Leitura de PDF no Storage] ➡️ [Ato 3: Matching CPAP & Proposta] ➡️ [Ato 4: Injeção de Lead ao Vivo] ➡️ [Ato 5: Recorrência LTV]
```

---

### 📍 ATO 1: O Desafio Comercial & Consulta ao BigQuery (2 minutos)
* **Onde interagir:** No **Gemini Enterprise**.
* **Prompt para executar no Gemini Enterprise:**
  > *"Quais são os pacientes com apneia do sono grave na nossa base do BigQuery que exigem contato imediato da equipe de vendas? Apresente o IAH, saturação mínima e médico prescritor de cada um."*
* **Resultado:** O Gemini Enterprise consulta a tabela `luminar_saude.leads_pacientes` e lista os casos graves (como Roberto Silveira Santos, IAH 38.4).

---

### 📍 ATO 2: Extração Multimodal do Laudo em PDF no Cloud Storage (3 minutos)
* **Onde interagir:** No **Gemini Enterprise**.
* **Prompt para executar no Gemini Enterprise:**
  > *"Abra o laudo polissonográfico do paciente Roberto Silveira Santos no Cloud Storage e resuma: qual foi a pressão titulada recomendada pelo Dr. Fernando Albuquerque e qual é o padrão respiratório dele?"*
* **Resultado:** O Gemini lê o PDF no Storage e extrai: pressão de **12.0 cmH2O**, IAH **38.4 ev/h** e respiração **bucal/mista**.

---

### 📍 ATO 3: Matching de CPAP, Máscara e Quebra de Objeções (3 minutos)
* **Onde interagir:** No **Gemini Enterprise**.
* **Prompt para executar no Gemini Enterprise:**
  > *"Com base no laudo e na respiração bucal do Roberto Silveira, qual modelo de CPAP e qual máscara do nosso catálogo devo ofertar? Gere também uma proposta comercial com quebra de objeções sobre adaptação para envio via WhatsApp."*
* **Resultado:**
  - **CPAP:** *ResMed AirSense 11 AutoSet*
  - **Máscara:** *AirFit F20 Full Face* (obrigatória para quem respira pela boca e tem pressão de 12 cmH2O).
  - **Cross-Sell:** Tubo aquecido *ClimateLineAir* para evitar ressecamento.
  - **Quebra de Objeções:** Argumento sobre o programa *"Luminar Adaptação 30 Dias"* (troca grátis de modelo de máscara).

---

### 📍 ATO 4: Injeção de Novo Lead em Tempo Real (3 minutos)
* **Passo 1 (No Gerenciador Cloud Run):**
  - Acesse o menu **`2. Gerador de Dados Sintéticos`** e clique em **`🚀 Injetar Paciente 3: Juliana Silveira (Rinite & Claustrofobia)`**.
* **Passo 2 (No Gemini Enterprise):**
  - Execute o prompt:
  > *"A paciente Juliana Silveira acabou de ser cadastrada. Ela tem rinite alérgica crônica e queixa de claustrofobia com máscaras faciais grandes. O que você recomenda para o caso dela?"*
* **Resultado:** A IA recomenda imediatamente a **Máscara AirFit P10 (Almofadas Nasais de apenas 45g)** e **Filtros Hipoalergênicos**.

---

### 📍 ATO 5: Gestão de Recorrência e LTV de Insumos (2 minutos)
* **Onde interagir:** No **Gemini Enterprise**.
* **Prompt para executar no Gemini Enterprise:**
  > *"Consulte o histórico de compras no BigQuery e liste quais clientes estão usando a mesma almofada de máscara há mais de 180 dias. Redija um lembrete empático de saúde para enviar aos pacientes elegíveis para troca."*
* **Resultado:** Identifica pacientes que precisam de substituição de insumos e gera mensagem focada em vedação, higiene e qualidade do sono.

---

## 🏆 Resumo do Valor de Negócio
1. **Ponto Único de Acesso:** Toda a inteligência e consultas unificadas no **Gemini Enterprise**.
2. **Dados Estruturados + Não Estruturados:** BigQuery e PDFs no Cloud Storage trabalhando juntos.
3. **Produtividade Comercial:** Ciclo de vendas reduzido de semanas para minutos com zero erro de compatibilidade.
