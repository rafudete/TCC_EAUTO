# 📄 logica_decisao.py

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from simple_pid import PID # <-- IMPORTANTE
from collections import deque
from regras_fuzzy import definir_regras, definir_variaveis_fuzzy


def criar_e_calcular_risco_fuzzy(p, tempo, dados_sensores):
    """
    Cria e executa o sistema de Lógica Fuzzy.
    AGORA TAMBÉM CALCULA A SEVERIDADE PID.
    """
    print("Criando sistema de Lógica Fuzzy...")
    # --- A. FUZZIFICAÇÃO (Chamando o arquivo externo) ---
    (fuzzy_vars, fuzzy_defs,
     sev_pid,
     pitch, altitude, acel_v,
     pitch_medio, proximidade_v_terminal, risco_de_queda) = definir_variaveis_fuzzy(p)

    # --- B. DEFINIR REGRAS (Chamando o arquivo externo) ---
    lista_de_regras = definir_regras(
        sev_pid, # <-- REATIVADO
        pitch, altitude, acel_v,
        pitch_medio, proximidade_v_terminal, risco_de_queda
    )

    # --- C. SISTEMA DE CONTROLE ---
    sistema_de_controle = ctrl.ControlSystem(lista_de_regras)
    simulador_risco = ctrl.ControlSystemSimulation(sistema_de_controle)

    # --- D. INICIALIZAÇÃO DOS CÁLCULOS (ANTES DO LOOP) ---
    risco_calculado_fuzzy = []
    lista_pitch_medio = []
    lista_prox_v_terminal = []
    
    # --- CORREÇÃO DO PID (INÍCIO) ---
    # 1. O PID é criado UMA VEZ, fora do loop.
    #    Isso permite que o termo "I" (Integral) acumule.
    pid_controller_severidade = PID(
        p.PID_Kp, p.PID_Ki, p.PID_Kd, 
        setpoint=0.0,           # O objetivo é velocidade vertical ZERO
        output_limits=(0, 100)  # A saída é a "Severidade" (0 a 100)
    )
    # 2. Lista para armazenar a saída do PID
    lista_severidade_pid = []
    # --- CORREÇÃO DO PID (FIM) ---

    # --- CÁLCULO DO dt_constante ---
    if len(tempo) > 1:
        dt_constante = tempo[1] - tempo[0]
    else:
        dt_constante = 1.0 # Um valor seguro para evitar divisão por zero

    # --- INICIALIZAR MEMÓRIAS (DEQUES) ANTES DO LOOP ---
    num_amostras_pitch_medio = int(p.tempo_persistencia_pitch / dt_constante)
    if num_amostras_pitch_medio < 1: num_amostras_pitch_medio = 1 # Garantia mínima
    historico_pitch_tendencia = deque(maxlen=num_amostras_pitch_medio)
    
    risco_anterior = 0.0

    # --- INÍCIO DO LOOP PRINCIPAL ---
    for i in range(len(tempo)):
        
        # --- 1. LER DADOS ATUAIS ---
        pitch_atual = dados_sensores['pitch_sensor_giro'][i]
        altitude_atual = dados_sensores['altitude_gnss'][i]
        tempo_atual = tempo[i]
        velocidade_atual_filtrada = dados_sensores['velocidade_filtrada_gnss'][i] # <-- Pego aqui
        
        # --- 2. ATUALIZAR O PID ---
        #    (O PID é ATUALIZADO, não recriado)
        #    Ele recebe a velocidade ATUAL e o dt
        severidade_atual = pid_controller_severidade(velocidade_atual_filtrada, dt=dt_constante)
        lista_severidade_pid.append(severidade_atual) # Salva o resultado

        # --- 3. CALCULAR MÉDIA DO PITCH ---
        historico_pitch_tendencia.append(pitch_atual)
        
        pitch_medio_recente = pitch_atual # Default
        if len(historico_pitch_tendencia) == num_amostras_pitch_medio:
             pitch_medio_recente = np.mean(historico_pitch_tendencia) 

        # --- 4. CÁLCULO DA PROXIMIDADE V-TERMINAL ---
        velocidade_atual_abs = abs(velocidade_atual_filtrada)
        v_terminal_abs = abs(p.v_terminal) 

        prox_v_terminal = 0.0 # Default seguro
        if v_terminal_abs > 0.1: # Evita divisão por zero
            prox_v_terminal = min(velocidade_atual_abs / v_terminal_abs, 1.0)


        # --- 5. SALVAR VALORES PARA RELATÓRIO ---
        lista_pitch_medio.append(pitch_medio_recente)
        lista_prox_v_terminal.append(prox_v_terminal)
              
        # --- 6. ALIMENTAR O CÉREBRO FUZZY ---
        simulador_risco.input['severidade_pid'] = severidade_atual # <-- REATIVADO
        simulador_risco.input['altitude'] = altitude_atual
        simulador_risco.input['aceleracao_vertical'] = dados_sensores['aceleracao_imu'][i]
        simulador_risco.input['pitch_medio'] = pitch_medio_recente
        simulador_risco.input['proximidade_v_terminal'] = prox_v_terminal
    
        # --- 7. COMPUTAR, SALVAR SAÍDA E DEBUGAR O "FLICKER" ---
        try: 
            simulador_risco.compute()
            risco_atual = simulador_risco.output['risco_de_queda']
            risco_calculado_fuzzy.append(risco_atual)
            
            # --- DEBUG V2.0 (POR QUE AS REGRAS 'ALTO' FALHAM?) ---
            if (risco_atual < p.limiar_reset_timer and risco_anterior > p.limiar_disparo_risco):
                
                # Calcular pertinências
                pert_pitch_neutro = fuzz.interp_membership(
                    pitch_medio.universe, pitch_medio['Neutro_Medio'].mf, pitch_medio_recente
                )
                pert_sev_critico = fuzz.interp_membership(
                    sev_pid.universe, sev_pid['Crítico'].mf, severidade_atual # <-- USA O VALOR ATUAL
                )
                pert_prox_v_alta = fuzz.interp_membership(
                    proximidade_v_terminal.universe, proximidade_v_terminal['Alta'].mf, prox_v_terminal
                )

                # Imprime o relatório da "falha"
                print("\n--- DEBUG DO \"FLICKER\" (FALHA 'ALTO') DETECTADO! ---")
                print(f"Instante: t={tempo[i]:.2f}s")
                print(f"RISCO DESPENCOU: {risco_anterior:.2f} -> {risco_atual:.2f}\n")
                
                print("--- ANÁLISE DOS INPUTS (O que oscilou?) ---")
                print(f"Input 'Severidade PID': {severidade_atual:.2f}\n")
                
                print("--- PERTINÊNCIA (Nível de 'Verdade' das regras 'ALTO') ---")
                print(f"regra_flat_spin:")
                print(f"  ...Pertinência 'Pitch é Neutro': {pert_pitch_neutro:.2%}")
                print(f"regra_v_terminal:")
                print(f"  ...Pertinência 'Proximidade V-Term é Alta': {pert_prox_v_alta:.2%}")
                print(f"  ...Pertinência 'Severidade PID é Crítico': {pert_sev_critico:.2%}")
                print("---------------------------------------------------\n")

            risco_anterior = risco_atual # Atualiza a memória para o próximo passo

        except KeyError: 
            print(f"--- ALERTA FUZZY ---")
            print(f"Nenhuma regra ativada no instante t={tempo[i]:.2f}s.")
            print(f"Assumindo Risco = 0 (seguro) para este instante.")
            risco_calculado_fuzzy.append(0)
            risco_anterior = 0.0 # Reseta a memória em caso de erro
    
    #print("Processamento Fuzzy concluído.")
    
    # --- 8. RETORNAR RESULTADOS ---
    return (risco_calculado_fuzzy, 
            lista_severidade_pid, # <-- RETORNO NOVO
            lista_pitch_medio, lista_prox_v_terminal, fuzzy_vars, fuzzy_defs)