# 📄 visualizacao.py
# (Versão COMPLETA E CORRIGIDA, com as 4 funções)

import matplotlib.pyplot as plt

def plotar_fisica_base(tempo, altitudes, velocidades):
    """
    GRÁFICO 1: O PROBLEMA (FÍSICA PURA)
    Mostra o "Cenário Base" (Item 3.5.1) sem nenhuma intervenção.
    """
    print("Visualizando [Gráfico 1]: Simulação da Física Pura...")
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(tempo, altitudes)
    plt.title('Altitude vs. Tempo (Real)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Altitude (m)')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(tempo, velocidades)
    plt.title('Velocidade Vertical vs. Tempo (Real)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade (m/s)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plotar_justificativa_filtro(tempo, vel_real, vel_estimada_gnss):
    """
    GRÁFICO 2: A JUSTIFICATIVA (SENSORES SUJOS)
    Mostra por que precisamos de um filtro. Compara o dado real
    com o dado "sujo" e caótico vindo do GNSS derivado.
    """
    print("Visualizando [Gráfico 2]: Justificativa do Filtro (Dados Sujos)...")
    plt.figure(figsize=(10, 6))
    plt.plot(tempo, vel_real, 'b-', label='Velocidade Real (Perfeita)')
    plt.plot(tempo, vel_estimada_gnss, 'm-', alpha=0.3, label='Velocidade (Estimada pelo GNSS)')
    plt.title('Estimativa de Velocidade (Derivada do GNSS)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade (m/s)')
    plt.ylim(vel_real.min() * 1.5, vel_real.max() * 1.5) # Zoom
    plt.legend()
    plt.grid(True)
    plt.show()

def plotar_solucao_filtro(tempo, vel_real, vel_estimada_gnss, vel_filtrada_gnss):
    """
    GRÁFICO 3: A SOLUÇÃO DE ENGENHARIA (FILTRO)
    Mostra o filtro em ação "limpando" o sinal sujo.
    """
    print("Visualizando [Gráfico 3]: Resultado do Filtro (Média Móvel)...")
    plt.figure(figsize=(10, 6))
    plt.plot(tempo, vel_real, 'b-', label='Velocidade Real (Perfeita)')
    plt.plot(tempo, vel_estimada_gnss, 'm-', alpha=0.15, label='Velocidade GNSS (Sujo)')
    plt.plot(tempo, vel_filtrada_gnss, 'r-', linewidth=2, label='Velocidade FILTRADA (Suavizada)')
    plt.title('Resultado do Filtro de Média Móvel')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade (m/s)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plotar_decisao_final(tempo, risco_calculado_fuzzy, severidade_pid, pitch_sensor_giro):
    """
    GRÁFICO 4: O "CÉREBRO" EM AÇÃO (A DECISÃO)
    O gráfico mais importante. Mostra o Risco Fuzzy sendo calculado
    com base nos inputs (PID e Pitch).
    """
    print("Visualizando [Gráfico 4]: Decisão Final do Sistema Fuzzy...")
    plt.figure(figsize=(14, 8))

    # Gráfico 1: A Saída do Risco Fuzzy
    plt.subplot(2, 1, 1)
    plt.plot(tempo, risco_calculado_fuzzy, 'r-', linewidth=2, label='Risco de Queda (Saída Fuzzy)')
    plt.title('Decisão do Sistema Fuzzy (Risco de Queda)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Risco Calculado (0 a 100)')
    plt.legend()
    plt.grid(True)

    # Gráfico 2: Os Inputs mais importantes
    plt.subplot(2, 1, 2)
    plt.plot(tempo, severidade_pid, 'b--', alpha=0.7, label='Severidade PID (Input)')
    plt.plot(tempo, pitch_sensor_giro, 'g--', alpha=0.7, label='Pitch (Input)')
    plt.title('Principais Sinais de Entrada (Contexto)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Valor do Sinal')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # (Cole isso no final do visualizacao.py)

def plotar_altitude_gnss(tempo, alt_real, altitude_gnss, p):
    """
    GRÁFICO ADICIONAL: Sensor de Altitude GNSS (Bruto)
    Mostra o comportamento do sensor GNSS simulado.
    """
    print("Visualizando [Gráfico Adicional]: Sensor Altitude GNSS (Bruto)...")
    plt.figure(figsize=(10, 6))
    plt.plot(tempo, alt_real, 'b-', label='Altitude Real (Perfeita)')
    plt.plot(tempo, altitude_gnss, 'r.', markersize=2, label=f'Leitura GNSS (5 Hz, $\sigma$={p.sigma_ruido_gnss}m)')
    plt.title('Simulação do Altímetro GNSS')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Altitude (m)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plotar_aceleracao_imu(tempo, acel_real, aceleracao_imu):
    """
    GRÁFICO ADICIONAL: Sensor de Aceleração IMU (Bruto)
    Mostra o comportamento do acelerômetro simulado.
    """
    print("Visualizando [Gráfico Adicional]: Sensor Aceleração IMU (Bruto)...")
    plt.figure(figsize=(10, 6))
    plt.plot(tempo, acel_real, 'b-', label='Aceleração Real (Perfeita)')
    plt.plot(tempo, aceleracao_imu, 'g-', alpha=0.7, label=f'Leitura IMU (com Bias e Ruído)')
    plt.title('Simulação do Acelerômetro (IMU)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Aceleração (m/s^2)')
    plt.legend()
    plt.grid(True)
    plt.show()