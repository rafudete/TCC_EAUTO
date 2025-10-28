# 📄 simulacao_fisica.py
import numpy as np
from scipy.integrate import solve_ivp

# As funções de física precisam ler os parâmetros
# Por isso, passamos 'p' (de parametros) para elas.

def _modelo_dinamica_queda(t, state, p):
    """Função interna da EDO. Note o 'p' extra."""
    h, v = state
    
    # Lê os parâmetros de física do objeto 'p'
    forca_peso = -p.m * p.g
    forca_arrasto = 0.5 * p.rho * p.C_d * p.A * (v * abs(v)) * (-1)
    forca_total = forca_peso + forca_arrasto
    
    dh_dt = v
    dv_dt = forca_total / p.m #antes era so m
    
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
    
    estado_inicial = [p.altitude_inicial, p.velocidade_inicial]
    tempo_simulacao = (0, p.tempo_simulacao_max)

    solucao = solve_ivp(
        lambda t, state: _modelo_dinamica_queda(t, state, p), # 'lambda' para passar 'p'
        tempo_simulacao,
        estado_inicial,
        method='RK45',
        events=_atingiu_solo,
        dense_output=True
    )

    print("Simulação da física concluída.")
    
    # Preparar resultados
    tempo_grafico = np.linspace(solucao.t[0], solucao.t[-1], 500)
    estados_grafico = solucao.sol(tempo_grafico)
    
    altitude_real = estados_grafico[0]
    velocidade_real = estados_grafico[1]
    
    # Calcular aceleração real
    aceleracao_real = np.diff(velocidade_real) / np.diff(tempo_grafico)
    aceleracao_real = np.insert(aceleracao_real, 0, 0)
    
    return (tempo_grafico, altitude_real, velocidade_real, aceleracao_real)