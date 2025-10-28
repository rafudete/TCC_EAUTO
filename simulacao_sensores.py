# 📄 simulacao_sensores.py
import numpy as np
import pandas as pd

def simular_sensores_e_filtros(p, tempo, alt_real, vel_real, acel_real):
    """
    Função principal: "Suja" todos os dados e aplica filtros.
    Recebe: p (parâmetros), e os dados "perfeitos" da simulação física.
    Devolve: um dicionário com todos os dados "sujos" e "filtrados".
    """
    print("Iniciando simulação dos sensores...")

    # --- 1. Simular Altímetro GNSS ---
    intervalo_gnss = 1.0 / p.taxa_atualizacao_gnss
    altitude_gnss = np.zeros_like(alt_real)
    ultima_leitura_gnss = alt_real[0] + np.random.normal(0, p.sigma_ruido_gnss)
    proxima_atualizacao_gnss = 0.0

    for i in range(len(tempo)):
        if tempo[i] >= proxima_atualizacao_gnss:
            ultima_leitura_gnss = alt_real[i] + np.random.normal(0, p.sigma_ruido_gnss)
            proxima_atualizacao_gnss += intervalo_gnss
        altitude_gnss[i] = ultima_leitura_gnss

    # --- 2. Simular Acelerômetro (IMU) ---
    ruido_branco_acel = np.random.normal(0, p.sigma_ruido_acel, len(acel_real))
    aceleracao_imu = acel_real + p.bias_acel + ruido_branco_acel

    # --- 3. Simular Velocidade (Derivada do GNSS) ---
    velocidade_estimada_gnss = np.diff(altitude_gnss) / np.diff(tempo)
    velocidade_estimada_gnss = np.insert(velocidade_estimada_gnss, 0, 0)

    # --- 4. FILTRAR Velocidade (Pré-processamento) ---
    print("Aplicando filtro de média móvel...")
    velocidade_suja_series = pd.Series(velocidade_estimada_gnss)
    velocidade_filtrada_gnss = velocidade_suja_series.rolling(
        window=p.tamanho_janela_filtro, min_periods=1
    ).mean().to_numpy()

    # --- 5. Simular Pitch (Giroscópio) - LÓGICA AUTOMÁTICA DE CENÁRIO ---
    print(f"Simulando Pitch para: {p.cenario_nome}...")
    pitch_real_graus = np.zeros_like(tempo)
    
    # Loop para calcular o pitch baseado no cenário definido em parametros.py
    for i in range(len(tempo)):
        
        # --- Lógica para Cenários de Mergulho ou Pouso ---
        if "Queda" in p.cenario_nome or "Pouso" in p.cenario_nome:
            if tempo[i] < p.tempo_inicio_mergulho:
                pitch_real_graus[i] = 0.0 # Começa nivelado
            else:
                # Simula a transição suave para o pitch final do cenário
                fracao = min(1.0, (tempo[i] - p.tempo_inicio_mergulho) / 3.0) 
                # Usa p.pitch_mergulho_graus (que será -45 ou -5 dependendo do cenário ativo)
                pitch_real_graus[i] = fracao * p.pitch_mergulho_graus
                
        # --- Lógica para Cenário de Turbulência ---
        elif "Turbulência" in p.cenario_nome:
            tempo_fim_turbulencia = p.tempo_inicio_turbulencia + p.duracao_turbulencia
            # Verifica se estamos DENTRO do período de turbulência
            if p.tempo_inicio_turbulencia <= tempo[i] < tempo_fim_turbulencia:
                # Adiciona oscilação aleatória
                oscilacao = np.random.normal(0, p.amplitude_pitch_turbulencia / 3)
                pitch_real_graus[i] = p.pitch_base_graus + oscilacao
            else:
                # Fora da turbulência, mantém o pitch base
                pitch_real_graus[i] = p.pitch_base_graus
                
        # --- (Opcional) Adicionar Lógica para Outros Cenários Aqui ---
        # elif "Outro Cenário" in p.cenario_nome:
        #     # ... lógica específica ...
        
        else:
             # Caso padrão se o nome do cenário não for reconhecido: mantém nivelado
             pitch_real_graus[i] = 0.0

    # Adiciona o ruído normal do sensor (como antes, fora do loop if/elif)
    ruido_giro = np.random.normal(0, p.sigma_ruido_giro, len(pitch_real_graus))
    pitch_sensor_giro = pitch_real_graus + ruido_giro
    print("Simulação do sensor de Pitch concluída.")
    # ---------------------------------------------------------------------
    
    print("Simulação dos sensores concluída.")

    # Retorna tudo em um "pacote" (dicionário)
    return {
        "altitude_gnss": altitude_gnss,
        "aceleracao_imu": aceleracao_imu,
        "velocidade_estimada_gnss": velocidade_estimada_gnss,
        "velocidade_filtrada_gnss": velocidade_filtrada_gnss,
        "pitch_sensor_giro": pitch_sensor_giro
    }