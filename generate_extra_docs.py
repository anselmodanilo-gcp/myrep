import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
REC_DIR = os.path.join(BASE_DIR, "storage", "receitas_medicas")
CAT_DIR = os.path.join(BASE_DIR, "storage", "catalogos_manuais")

# Receita 1
r1 = """CLÍNICA SUL DE MEDICINA RESPIRATÓRIA E DO SONO
Dr. Fernando Albuquerque - CRM-SP 142.890 | RQE 78.901
Pneumologia e Medicina do Sono

RECEITUÁRIO MÉDICO ESPECIALIZADO

Paciente: Roberto Silveira Santos
Data: 20/08/2026

PRESCRIÇÃO TERAPÊUTICA:

1. Pressão Positiva Contínua em Vias Aéreas (CPAP) com ajuste automático de pressão (AutoSet / Auto-CPAP).
   - Pressão Mínima: 8.0 cmH2O
   - Pressão Máxima: 16.0 cmH2O
   - Pressão Titulada em Laboratório: 12.0 cmH2O
   - Alívio de Pressão Expiratório (EPR / SensAwake): Nível 3 (Máximo conforto).
   - Modo de Rampa: Automático (início com 4.0 cmH2O durante 20 min).

2. Interface Respiratória (Máscara):
   - Modelo Facial / Oronasal (devido à respiração predominantemente bucal e queixas de escape de ar). Sugestão: ResMed AirFit F20 (Tamanho G).

3. Umidificação Ativa com Tubo Aquecido:
   - Nível de umidificação 4 com controle térmico (ClimateLine) para prevenção de rinite e ressecamento de via aérea superior.

4. Telemonitoramento:
   - Conectar o equipamento ao sistema de acompanhamento remoto AirView e liberar acesso ao médico assistente.

Dr. Fernando Albuquerque
Assinatura Digital ICP-Brasil: 7f8a9e01-23bc-45de-67f8-9a0b1c2d3e4f
"""

with open(os.path.join(REC_DIR, "receita_medica_roberto_silveira.txt"), "w", encoding="utf-8") as f:
    f.write(r1)

# Receita 2
r2 = """INSTITUTO DE OTORRINOLARINGOLOGIA E CIRURGIA CÉRVICO-FACIAL
Dra. Beatriz Mendes - CRM-SP 178.432

RECEITUÁRIO MÉDICO

Paciente: Mariana Costa Andrade
Data: 21/08/2026

PRESCRIÇÃO:
1. Auto-CPAP com algoritmos de alívio de pressão.
   - Faixa de pressão: 6.0 a 11.0 cmH2O (pressão ideal 8.5 cmH2O).
2. Máscara de Almofadas Nasais (Pillow Mask) ultraleve (ex: AirFit P10) - Paciente refere claustrofobia com máscaras faciais.
3. Filtros ultrafinos hipoalergênicos (histórico de rinite alérgica crônica).
4. Reavaliação em 30 dias com dados do cartão SD ou telemetria.

Dra. Beatriz Mendes
"""

with open(os.path.join(REC_DIR, "receita_medica_mariana_costa.txt"), "w", encoding="utf-8") as f:
    f.write(r2)

# Catalogo Spec Sheet
c1 = """ESPECIFICAÇÕES TÉCNICAS - RESMED AIRSENSE 11 AUTOSET
Categoria: CPAP Automático Premium
Fabricante: ResMed Ltd.

1. Recursos Principais:
- Algoritmo AutoSet e AutoSet for Her para titulação dinâmica respiração a respiração.
- Conectividade Celular 4G integrada com envio diário de dados ao ecossistema AirView.
- Assistente de Cuidado Pessoal (Care Check-In) com orientações interativas na tela touchscreen.
- Tecnologia EPR (Expiratory Pressure Relief) para redução suave da pressão na expiração.
- Umidificador HumidAir integrado com controle climático automático (Climate Control Auto).

2. Dimensões e Ruído:
- Peso: 1.130 g com câmara de água vazia.
- Dimensões: 94.5 mm x 259.4 mm x 138.5 mm.
- Nível de Ruído: 25 dBA (praticamente inaudível no quarto de dormir).

3. Compatibilidade de Acessórios:
- Tubos: SlimLine (15 mm), Padrão (22 mm), ClimateLineAir 11 (aquecido).
- Filtros: Padrão e Hipoalergênicos.
- Alimentação: Fonte bivolt automática 100-240V, 50-60Hz (consumo típico 56W).
"""

with open(os.path.join(CAT_DIR, "especificacao_resmed_airsense11.txt"), "w", encoding="utf-8") as f:
    f.write(c1)

print("[OK] Documentos complementares criados.")
