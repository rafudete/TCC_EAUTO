# 📄 logica_decisao.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from simple_pid import PID
from collections import deque
from regras_fuzzy import definir_regras

def calcular_severidade_pid(p, tempo, velocidade_filtrada):
    """
    Roda a lógica do PID para gerar o sinal de "Severidade".
    """
    print("Calculando severidade (PID)...")
    pid = PID(p.PID_Kp, p.PID_Ki, p.PID_Kd, setpoint=0.0, output_limits=(0, 100))
    
    if len(tempo) > 1:
        dt_constante = tempo[1] - tempo[0]
    else:
        dt_constante = 1.0

    saida_pid_severidade = []
    for i in range(len(tempo)):
        leitura_atual_velocidade = velocidade_filtrada[i]
        severidade = pid(leitura_atual_velocidade, dt=dt_constante)
        saida_pid_severidade.append(severidade)
    
    return np.array(saida_pid_severidade), dt_constante # Retorna a severidade E o dt_constante calculado

def criar_e_calcular_risco_fuzzy(p, tempo, dados_sensores, severidade_pid, dt_constante):
    """
    Cria e executa o sistema de Lógica Fuzzy.
    """
    print("Criando sistema de Lógica Fuzzy...")
    
    # --- A. FUZZIFICAÇÃO (Passo 14) ---
    universo_severidade = np.arange(0, 101, 1)
    sev_pid = ctrl.Antecedent(universo_severidade, 'severidade_pid')
    sev_pid['Suave'] = fuzz.trimf(universo_severidade, [0, 0, 50])
    sev_pid['Moderado'] = fuzz.trimf(universo_severidade, [20, 50, 80])
    sev_pid['Crítico'] = fuzz.trimf(universo_severidade, [60, 100, 100])

    universo_pitch = np.arange(-90, 91, 1)
    pitch = ctrl.Antecedent(universo_pitch, 'pitch')
    pitch['Negativo'] = fuzz.trimf(universo_pitch, [-90, -90, -5])
    pitch['Neutro'] = fuzz.trimf(universo_pitch, [-20, 0, 20])
    pitch['Positivo'] = fuzz.trimf(universo_pitch, [5, 90, 90])

    universo_altitude = np.arange(0, 1001, 1)
    altitude = ctrl.Antecedent(universo_altitude, 'altitude')
    altitude['Baixa'] = fuzz.trimf(universo_altitude, [0, 0, 300])
    altitude['Média'] = fuzz.trimf(universo_altitude, [200, 500, 800])
    altitude['Alta'] = fuzz.trimf(universo_altitude, [600, 1000, 1000])

    universo_vel_v = np.arange(-60, 11, 1)
    vel_v = ctrl.Antecedent(universo_vel_v, 'velocidade_vertical')
    vel_v['Baixa'] = fuzz.trimf(universo_vel_v, [-15, -8, 0])
    vel_v['Moderada'] = fuzz.trimf(universo_vel_v, [-30, -20, -10])
    vel_v['Alta'] = fuzz.trimf(universo_vel_v, [-60, -45, -25])

    universo_acel = np.arange(-15, 6, 1)
    acel_v = ctrl.Antecedent(universo_acel, 'aceleracao_vertical')
    acel_v['Leve'] = fuzz.trimf(universo_acel, [-5, 0, 5])
    acel_v['Moderada'] = fuzz.trimf(universo_acel, [-10, -7, -3])
    acel_v['Acentuada'] = fuzz.trimf(universo_acel, [-15, -12, -8])

    universo_risco = np.arange(0, 101, 1)
    risco_de_queda = ctrl.Consequent(universo_risco, 'risco_de_queda')
    risco_de_queda['Baixo'] = fuzz.trimf(universo_risco, [0, 0, 40])
    risco_de_queda['Moderado'] = fuzz.trimf(universo_risco, [20, 50, 80])
    risco_de_queda['Alto'] = fuzz.trimf(universo_risco, [70, 100, 100])

    # --- B. DEFINIR REGRAS (Chamando o arquivo externo) ---
    # Chama a função do regras_fuzzy.py, passando as variáveis criadas na Fuzzificação
    lista_de_regras = definir_regras(
        sev_pid, pitch, altitude, vel_v, acel_v, risco_de_queda
    )

    # --- C. SISTEMA DE CONTROLE (Usando a lista de regras) ---
    print("Montando o sistema de controle Fuzzy...")
    sistema_de_controle = ctrl.ControlSystem(lista_de_regras) # Passa a lista retornada
    simulador_risco = ctrl.ControlSystemSimulation(sistema_de_controle)
    print("Sistema Fuzzy pronto.") 

    # --- Lógica de Persistência ---
    pitch_negativo_persistente = [] # <-- NOVA LISTA PARA GUARDAR O RESULTADO DA ANÁLISE
    tempo_persistencia_pitch = 3.0 # Segundos - Quanto tempo o pitch precisa ficar negativo?
    num_amostras_persistencia = int(tempo_persistencia_pitch / dt_constante) # Calcula quantos pontos de dados cabem em 3s
    historico_pitch = deque(maxlen=num_amostras_persistencia) # Fila com tamanho máximo
    limiar_pitch_negativo = -10.0 # Graus - Consideramos negativo abaixo disso (mais seguro que -5)
    # -----------------------------
    
    # --- D. EXECUTAR SIMULAÇÃO FUZZY (Passo 17) ---
    print("Processando dados com a Lógica Fuzzy...")
    risco_calculado_fuzzy = []
    
    for i in range(len(tempo)):
        # --- Análise de Persistência do Pitch ---
        pitch_atual = dados_sensores['pitch_sensor_giro'][i]
        historico_pitch.append(pitch_atual) # Adiciona o pitch atual à memória

        # Verifica se a memória está cheia E se TODOS os valores na memória são negativos
        persistente = False
        # Só podemos verificar a persistência se a memória estiver cheia
        if len(historico_pitch) == num_amostras_persistencia:
            if all(p < limiar_pitch_negativo for p in historico_pitch):
                persistente = True

        # Se a memória não está cheia ainda, consideramos como não persistente        
        pitch_negativo_persistente.append(persistente) # Guarda True ou False
        # ------------------------------------
        
        # Alimenta o "cérebro" com os dados do "pacote"
        simulador_risco.input['severidade_pid'] = severidade_pid[i]
        simulador_risco.input['pitch'] = dados_sensores['pitch_sensor_giro'][i]
        simulador_risco.input['altitude'] = dados_sensores['altitude_gnss'][i]
        simulador_risco.input['velocidade_vertical'] = dados_sensores['velocidade_filtrada_gnss'][i]
        simulador_risco.input['aceleracao_vertical'] = dados_sensores['aceleracao_imu'][i]

        simulador_risco.compute()
        try: 
            # Tenta ler a saída normalmente
            risco_calculado_fuzzy.append(simulador_risco.output['risco_de_queda'])
        except KeyError: # Se der KeyError (nenhuma regra ativada)...
            print(f"--- ALERTA FUZZY ---")
            print(f"Nenhuma regra ativada no instante t={tempo[i]:.2f}s.")
            print(f"Inputs que causaram o erro:")
            print(f"  - severidade_pid: {severidade_pid[i]:.2f}")
            print(f"  - pitch: {dados_sensores['pitch_sensor_giro'][i]:.2f}")
            print(f"  - altitude: {dados_sensores['altitude_gnss'][i]:.2f}")
            print(f"  - velocidade_vertical: {dados_sensores['velocidade_filtrada_gnss'][i]:.2f}")
            print(f"  - aceleracao_vertical: {dados_sensores['aceleracao_imu'][i]:.2f}")
            print(f"Assumindo Risco = 0 (seguro) para este instante.")
            print(f"--- FIM ALERTA ---")
            risco_calculado_fuzzy.append(0) # Assume risco 0 (seguro) como fallback
    
    print("Processamento Fuzzy e Análise de Persistência concluídos.")
    # Retorna as duas listas agora
    return risco_calculado_fuzzy, pitch_negativo_persistente

def analisar_disparo(p, tempo, risco_calculado_fuzzy, pitch_persistente):
    """
    Verifica se as condições de disparo foram atingidas.
    """
    print("\n--- Análise da Tomada de Decisão (Item 3.3.2) ---")
    intervalo_tempo_dt = tempo[1] - tempo[0]
    contador_tempo_seguro = 0.0
    disparado = False

    for i in range(len(risco_calculado_fuzzy)):
        if i < len(pitch_persistente) and risco_calculado_fuzzy[i] > p.limiar_disparo_risco and pitch_persistente[i] == True:
            contador_tempo_seguro += intervalo_tempo_dt
        else:
            contador_tempo_seguro = 0.0 # Reseta o contador se QUALQUER condição falhar

        if contador_tempo_seguro >= p.tempo_minimo_disparo and not disparado:
            print(f"\n*** DISPARO DO PARAQUEDAS ACIONADO! ***")
            print(f"Cenário: {p.cenario_nome}")
            print(f"Tempo da simulação: {tempo[i]:.2f} segundos.")
            print(f"Condição: Risco ({risco_calculado_fuzzy[i]:.1f}) > {p.limiar_disparo_risco} por {contador_tempo_seguro:.2f}s.")
            disparado = True
            # (Dentro do if que printa o disparo)
            print(f"Condição: Risco ({risco_calculado_fuzzy[i]:.1f}) > {p.limiar_disparo_risco} E Pitch Negativo Persistente")
            print(f"          por {contador_tempo_seguro:.2f}s (>= {p.tempo_minimo_disparo}s).")
            break # Para o loop, já disparou

    if not disparado:
        print("\nSistema permaneceu estável. Paraquedas não foi acionado.")
        print(f"O risco máximo atingido foi: {np.max(risco_calculado_fuzzy):.2f}")