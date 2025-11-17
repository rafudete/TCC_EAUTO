# 📄 simulacao_sensores.py
import numpy as np
import pandas as pd

def simular_sensores_e_filtros(p, tempo, alt_real, vel_real, acel_real):
    """
    Função principal: "Suja" todos os dados e aplica filtros.
    """
    print("Iniciando simulação dos sensores...")

    # --- 1. INICIALIZAÇÃO ---
    
    # Inicializa arrays vazios que serão preenchidos DENTRO do loop
    altitude_gnss = np.zeros_like(alt_real)
    pitch_real_graus = np.zeros_like(tempo)
    
    # Variáveis de estado para o GNSS
    ultima_leitura_gnss = alt_real[0] + np.random.normal(0, p.sigma_ruido_gnss)
    proxima_atualizacao_gnss = 0.0
    intervalo_gnss = 1.0 / p.taxa_atualizacao_gnss
    
    # Variáveis de estado para a Turbulência
    tempo_fim_turbulencia = p.tempo_inicio_turbulencia + p.duracao_turbulencia

    # --- 2. LOOP PRINCIPAL DE SIMULAÇÃO DE SENSORES ---
    # (UM ÚNICO LOOP para calcular tudo que depende do tempo)
    
    for i in range(len(tempo)):
        t = tempo[i] # Tempo atual

        # --- Lógica do Altímetro GNSS (passo-a-passo) ---
        if t >= proxima_atualizacao_gnss:
            ultima_leitura_gnss = alt_real[i] + np.random.normal(0, p.sigma_ruido_gnss)
            proxima_atualizacao_gnss += intervalo_gnss
        altitude_gnss[i] = ultima_leitura_gnss # Salva a leitura (nova ou antiga)

        # --- Lógica do Pitch ---

        # CASO 1: POUSO COM TURBULÊNCIA (O mais específico)
        if "Pouso com Turbulência" in p.cenario_nome:
            tempo_fim_turbulencia = p.tempo_inicio_turbulencia + p.duracao_turbulencia
            if p.tempo_inicio_turbulencia <= t < tempo_fim_turbulencia:
                # Oscila em torno do pitch base de POUSO (-5)
                oscilacao = np.random.normal(0, p.amplitude_pitch_turbulencia / 3)
                pitch_real_graus[i] = p.pitch_base_graus + oscilacao 
            else:
                pitch_real_graus[i] = p.pitch_base_graus # Mantém -5

        # CASO 2: SÓ QUEDA ou SÓ POUSO (Sem turbulência no sensor)
        elif "Queda" in p.cenario_nome or "Pouso" in p.cenario_nome:
            if t < p.tempo_inicio_mergulho:
                pitch_real_graus[i] = 0.0
            else:
                fracao = min(1.0, (t - p.tempo_inicio_mergulho) / 3.0) 
                pitch_real_graus[i] = fracao * p.pitch_mergulho_graus # (-45 ou -5)

        # CASO 3: SÓ TURBULÊNCIA (Voo nivelado)
        elif "Turbulência" in p.cenario_nome:
            tempo_fim_turbulencia = p.tempo_inicio_turbulencia + p.duracao_turbulencia
            if p.tempo_inicio_turbulencia <= t < tempo_fim_turbulencia:
                # Oscila em torno do pitch base NIVELADO (0)
                oscilacao = np.random.normal(0, p.amplitude_pitch_turbulencia / 3)
                pitch_real_graus[i] = p.pitch_base_graus + oscilacao # (p.pitch_base_graus é 0)
            else:
                pitch_real_graus[i] = p.pitch_base_graus

    else:
         pitch_real_graus[i] = 0.0
    # --- FIM DA LÓGICA DO PITCH ---
    # --- FIM DO LOOP PRINCIPAL ---

    # --- 3. CÁLCULOS PÓS-LOOP (Baseados em arrays completos) ---
    
    # Adiciona ruído ao Pitch (agora que pitch_real_graus está preenchido)
    ruido_giro = np.random.normal(0, p.sigma_ruido_giro, len(pitch_real_graus))
    pitch_sensor_giro = pitch_real_graus + ruido_giro
    
    # Simular Acelerômetro (IMU)
    ruido_branco_acel = np.random.normal(0, p.sigma_ruido_acel, len(acel_real))
    aceleracao_imu = acel_real + p.bias_acel + ruido_branco_acel

    # Simular Velocidade (Derivada do GNSS)
    velocidade_estimada_gnss = np.diff(altitude_gnss) / np.diff(tempo)
    velocidade_estimada_gnss = np.insert(velocidade_estimada_gnss, 0, 0)

    # FILTRAR Velocidade (Pré-processamento)
    velocidade_suja_series = pd.Series(velocidade_estimada_gnss)
    velocidade_filtrada_gnss = velocidade_suja_series.rolling(
        window=p.tamanho_janela_filtro, min_periods=1
    ).mean().to_numpy()

    return {
        "altitude_gnss": altitude_gnss,
        "aceleracao_imu": aceleracao_imu,
        "velocidade_estimada_gnss": velocidade_estimada_gnss,
        "velocidade_filtrada_gnss": velocidade_filtrada_gnss,
        "pitch_sensor_giro": pitch_sensor_giro
    }