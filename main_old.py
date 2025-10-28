# 📄 main.py
# O "cérebro" principal que orquestra toda a simulação.

# 1. Importar os módulos que criamos
import parametros as p
import simulacao_fisica as fisica
import simulacao_sensores as sensores
import logica_decisao as cerebro
import visualizacao as plots

# 2. Executar a Simulação da Física
# (Passa os parâmetros 'p' e recebe os dados 'perfeitos')
(tempo, alt_real, vel_real, acel_real) = fisica.executar_simulacao(p)

# 3. Executar a Simulação dos Sensores
# (Passa os dados 'perfeitos' e recebe os dados 'sujos' e 'filtrados')
dados_sensores = sensores.simular_sensores_e_filtros(
    p, tempo, alt_real, vel_real, acel_real
)

# 4. Executar a Lógica de Decisão (PID e Fuzzy)
# A. Calcular Severidade (PID)
severidade_pid = cerebro.calcular_severidade_pid(
    p, tempo, dados_sensores['velocidade_filtrada_gnss']
)

# B. Calcular Risco (Fuzzy)
risco_final = cerebro.criar_e_calcular_risco_fuzzy(
    p, tempo, dados_sensores, severidade_pid
)

# 5. Visualizar o Resultado Principal
plots.plotar_decisao_final(
    tempo, 
    risco_final, 
    severidade_pid, 
    dados_sensores['pitch_sensor_giro']
)

# 6. Analisar o Disparo
cerebro.analisar_disparo(p, tempo, risco_final)

print("\n--- Simulação Completa Concluída ---")