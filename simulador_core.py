# 📄 simulador_core.py

# Esta é a "receita" principal da simulação.
# Ele faz todo o trabalho, recebendo 'p' como argumento.

# 1. Importar os módulos
import simulacao_fisica as fisica
import simulacao_sensores as sensores
import logica_decisao as cerebro
import visualizacao as plots
import numpy as np # Adicionado por segurança
import pandas as pd # Adicionado por segurança
import matplotlib.pyplot as plt # Adicionado por segurança

def rodar_simulacao_completa(p):
    """
    Executa UMA simulação completa, do início ao fim,
    baseado no objeto de parâmetros 'p' fornecido.
    """
    
    # 2. Executar a Simulação da Física
    (tempo, alt_real, vel_real, acel_real) = fisica.executar_simulacao(p)

    # Plotar Gráfico 1 (O Problema)
    plots.plotar_fisica_base(tempo, alt_real, vel_real)

    # 3. Executar a Simulação dos Sensores
    dados_sensores = sensores.simular_sensores_e_filtros(p, tempo, alt_real, vel_real, acel_real)

    # --- BLOCO DE PLOTAGEM ATUALIZADO ---
    dados_reais = {
        'altitude': alt_real,
        'velocidade': vel_real,
        'aceleracao': acel_real
    }
    # Chama o NOVO gráfico consolidado
    plots.plotar_sensores_consolidados(p, tempo, dados_reais, dados_sensores)

    # 4. Executar a Lógica de Decisão (PID e Fuzzy)
    #    (O PID agora é calculado DENTRO da função fuzzy)

    # B. Calcular Risco (Fuzzy)
    (risco_final, 
     severidade_pid_final, # <-- CAPTURA A SAÍDA DO PID
     pitch_medio_final, prox_v_term_final, fuzzy_vars, fuzzy_defs) = cerebro.criar_e_calcular_risco_fuzzy(
        p, tempo, dados_sensores
    )

    # 5. Visualizar o Resultado Principal
    # Plotar Gráfico 3 (A Decisão)
    plots.plotar_decisao_final(
        tempo, 
        risco_final, 
        severidade_pid_final, # <-- PASSA O PID PARA O GRÁFICO
        dados_sensores['pitch_sensor_giro']
    )

    # 6. Analisar e Reportar os Resultados (em visualizacao.py)
    plots.analisar_resultados(
        p, tempo, dados_sensores, 
        severidade_pid_final, # <-- PASSA O PID PARA A ANÁLISE
        risco_final, 
        pitch_medio_final, prox_v_term_final, fuzzy_vars, fuzzy_defs
    )

    print(f"\n--- Simulação Completa Concluída ({p.cenario_nome}) ---")