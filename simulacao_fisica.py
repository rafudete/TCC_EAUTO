# 📄 simulacao_fisica.py
import numpy as np
from scipy.integrate import solve_ivp

# As funções de física precisam ler os parâmetros
# Por isso, passamos 'p' (de parametros) para elas.

def _modelo_dinamica_queda(t, state, p):
    """
    Define as Equações Diferenciais Ordinárias (EDOs) da queda.
    AGORA COM LÓGICA DIFERENTE PARA O CENÁRIO DE POUSO.
    """
    h, v = state

    # --- CALCULAR FORÇAS NATURAIS (SEMPRE PRESENTES) ---
    forca_peso = -p.m * p.g
    # Arrasto baseado na velocidade ATUAL (v)
    forca_arrasto = 0.5 * p.rho * p.C_d * p.A * (v * abs(v)) * (-1)


    # --- LÓGICA DEPENDENTE DO CENÁRIO ---

    # CASO 1: POUSO COM TURBULÊNCIA (O mais específico)
    if "Pouso com Turbulência" in p.cenario_nome:
        # OBJETIVO: Manter -5 m/s ENQUANTO luta contra rajadas

        # Força do Piloto Automático (tentando ficar em -5 m/s)
        erro_velocidade = p.velocidade_descida_pouso - v
        forca_controle = p.K_pouso_vel * erro_velocidade

        # Força da Turbulência (Rajada Vertical Aleatória)
        forca_rajada = np.random.normal(0, p.forca_rajada_turbulencia / 3)

        # Força Total = Peso + Arrasto + Controle + Rajada
        forca_total = forca_peso + forca_arrasto + forca_controle + forca_rajada

    # CASO 2: SÓ POUSO (Sem turbulência)
    elif "Pouso" in p.cenario_nome:
        # OBJETIVO: Manter -5 m/s (sem rajadas)
        erro_velocidade = p.velocidade_descida_pouso - v
        forca_controle = p.K_pouso_vel * erro_velocidade
        forca_total = forca_peso + forca_arrasto + forca_controle

    # CASO 3: SÓ TURBULÊNCIA (Voo nivelado)
    elif "Turbulência" in p.cenario_nome:
        # OBJETIVO: Manter 0 m/s ENQUANTO luta contra rajadas
        erro_velocidade = 0.0 - v 
        forca_controle = p.K_nivelado_vel * erro_velocidade
        forca_rajada = np.random.normal(0, p.forca_rajada_turbulencia / 3)
        forca_total = forca_peso + forca_arrasto + forca_controle + forca_rajada

    # CASO 4: QUEDA ou FLAT SPIN (Física original)
    else:
        forca_total = forca_peso + forca_arrasto

    # --- CALCULAR DERIVADAS (Leis de Newton) ---
    dh_dt = v 
    dv_dt = forca_total / p.m # A aceleração agora depende do cenário!

    return [dh_dt, dv_dt]

def _atingiu_solo(t, state):
    """Evento de parada (não precisa de 'p')"""
    return state[0]
_atingiu_solo.terminal = True
_atingiu_solo.direction = -1

def executar_simulacao(p):
    """
    Função principal deste módulo.
    Executa a simulação da física "perfeita".
    Recebe: p (os parâmetros do arquivo parametros.py)
    Devolve: (tempo, altitude_real, velocidade_real, aceleracao_real)
    """
    print(f"Iniciando simulação da física para: {p.cenario_nome}...")
    
    # Define a velocidade inicial com base no cenário
    if "Pouso" in p.cenario_nome:
        v_inicial = p.velocidade_descida_pouso 
        print(f"   -> Usando velocidade inicial de pouso: {v_inicial} m/s")
    else:
        v_inicial = p.velocidade_inicial_padrao # Usa 0.0 para outros cenários
        print(f"   -> Usando velocidade inicial padrão: {v_inicial} m/s")

    estado_inicial = [p.altitude_inicial, v_inicial] # Usa v_inicial

    tempo_simulacao = (0, p.tempo_simulacao_max)

    solucao = solve_ivp(
        lambda t, state: _modelo_dinamica_queda(t, state, p), 
        tempo_simulacao,
        estado_inicial, # Passa o estado inicial correto
        method='RK45',
        events=_atingiu_solo,
        dense_output=True
    )
    
    # Preparar resultados
    tempo_grafico = np.linspace(solucao.t[0], solucao.t[-1], 500)
    estados_grafico = solucao.sol(tempo_grafico)
    
    altitude_real = estados_grafico[0]
    velocidade_real = estados_grafico[1]
    
    # Calcular aceleração real
    aceleracao_real = np.diff(velocidade_real) / np.diff(tempo_grafico)
    aceleracao_real = np.insert(aceleracao_real, 0, 0)
    
    return (tempo_grafico, altitude_real, velocidade_real, aceleracao_real)