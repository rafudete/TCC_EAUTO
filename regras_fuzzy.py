# 📄 regras_fuzzy.py
# Este arquivo centraliza a definição da Base de Regras Fuzzy.

import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

def definir_variaveis_fuzzy(p):
    """
    Cria todas as variáveis Fuzzy (Antecedents e Consequents)
    e retorna os pacotes 'fuzzy_vars' (objetos) e 'fuzzy_defs' (strings).
    """

    # --- A. FUZZIFICAÇÃO (Definição das Variáveis) ---
    
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

    universo_acel = np.arange(-15, 6, 1)
    acel_v = ctrl.Antecedent(universo_acel, 'aceleracao_vertical')
    acel_v['Leve'] = fuzz.trimf(universo_acel, [-5, 0, 5])
    acel_v['Moderada'] = fuzz.trimf(universo_acel, [-10, -7, -3])
    acel_v['Acentuada'] = fuzz.trimf(universo_acel, [-15, -12, -8])

    universo_pitch_medio = np.arange(-90, 91, 1)
    pitch_medio = ctrl.Antecedent(universo_pitch_medio, 'pitch_medio')
    pitch_medio['Negativo_Medio'] = fuzz.trimf(universo_pitch_medio, [-90, -90, -8])
    pitch_medio['Neutro_Medio'] = fuzz.trimf(universo_pitch_medio, [-15, 0, 15])
    pitch_medio['Positivo_Medio'] = fuzz.trimf(universo_pitch_medio, [8, 90, 90])

    # --- PROXIMIDADE DA VELOCIDADE TERMINAL ---
    universo_prox_v_term = np.arange(0, 1.01, 0.01) # (Um ratio de 0.0 a 1.0)
    proximidade_v_terminal = ctrl.Antecedent(universo_prox_v_term, 'proximidade_v_terminal')
    
    proximidade_v_terminal['Baixa'] = fuzz.trimf(universo_prox_v_term, [0.0, 0.0, 0.5])
    proximidade_v_terminal['Media'] = fuzz.trimf(universo_prox_v_term, [0.3, 0.6, 0.9])
    proximidade_v_terminal['Alta'] = fuzz.trimf(universo_prox_v_term, [0.6, 1.0, 1.0]) # Ajustado para [0.6, 1.0, 1.0]

    universo_risco = np.arange(0, 101, 1)
    risco_de_queda = ctrl.Consequent(universo_risco, 'risco_de_queda')
    risco_de_queda['Baixo'] = fuzz.trimf(universo_risco, [0, 0, 40])
    risco_de_queda['Moderado'] = fuzz.trimf(universo_risco, [20, 50, 80])
    risco_de_queda['Alto'] = fuzz.trimf(universo_risco, [70, 100, 100])

    # --- PACOTE DE DEFINIÇÕES FUZZY (relatório) ---
    fuzzy_defs = {
        'sev_pid': {'Suave': '[0, 0, 50]', 'Moderado': '[20, 50, 80]', 'Crítico': '[60, 100, 100]'},
        'pitch': {'Negativo': '[-90, -90, -5]', 'Neutro': '[-20, 0, 20]', 'Positivo': '[5, 90, 90]'},
        'altitude': {'Baixa': '[0, 0, 300]', 'Média': '[200, 500, 800]', 'Alta': '[600, 1000, 1000]'},
        'acel_v': {'Leve': '[-5, 0, 5]', 'Moderada': '[-10, -7, -3]', 'Acentuada': '[-15, -12, -8]'},
        'pitch_medio': {'Negativo_Medio': '[-90, -90, -8]', 'Neutro_Medio': '[-15, 0, 15]', 'Positivo_Medio': '[8, 90, 90]'},
        'risco_de_queda': {'Baixo': '[0, 0, 40]', 'Moderado': '[20, 50, 80]', 'Alto': '[70, 100, 100]'},
        'proximidade_v_terminal': {'Baixa': '[0.0, 0.0, 0.5]','Media': '[0.3, 0.6, 0.9]','Alta': '[0.6, 1.0, 1.0]'}
    }
    # --- FIM DO PACOTE DE DEFINIÇÕES ---

    # --- PACOTE DE VARIÁVEIS FUZZY (para o relatório) ---
    fuzzy_vars = {'pitch': pitch, 'altitude': altitude, 'acel_v': acel_v, 
                  'sev_pid': sev_pid,
                  'pitch_medio': pitch_medio, 'proximidade_v_terminal':proximidade_v_terminal, 'risco_de_queda': risco_de_queda}

    return (fuzzy_vars, fuzzy_defs, 
            sev_pid,
            pitch, altitude, acel_v, 
            pitch_medio, proximidade_v_terminal, risco_de_queda)


def definir_regras(sev_pid,
                   pitch, altitude, acel_v, 
                   pitch_medio, proximidade_v_terminal, risco_de_queda):
    """
    Define e retorna a lista de regras Fuzzy para o sistema.
    """

    # Regra 1: MERGULHO (Pitch Negativo)
    regra_mergulho = ctrl.Rule(
        pitch_medio['Negativo_Medio'] & (proximidade_v_terminal['Alta'] | sev_pid['Crítico']),
        risco_de_queda['Alto'])

    # Regra 3: MERGULHO ACELERADO
    regra_emergencia_3 = ctrl.Rule(
        pitch_medio['Negativo_Medio'] & acel_v['Acentuada'], risco_de_queda['Alto'])

    # Regra 4: REGRA DE SEGURANÇA (BAIXO)
    regra_segura = ctrl.Rule(
        (pitch_medio['Neutro_Medio'] & proximidade_v_terminal['Baixa'] & altitude['Baixa']) |
        pitch_medio['Positivo_Medio'],
        risco_de_queda['Baixo'])

    # Regra 5: REGRA "PEGA-TUDO" (DEFAULT)
    regra_default_segura = ctrl.Rule(
        (pitch_medio['Neutro_Medio'] | pitch_medio['Positivo_Medio']) & ~sev_pid['Crítico'],
        risco_de_queda['Baixo'])

    # Regra 6: FLAT SPIN (V5.0) - ATUALIZADA
    regra_flat_spin = ctrl.Rule(
        pitch_medio['Neutro_Medio'] & proximidade_v_terminal['Alta'] & sev_pid['Crítico'],
        risco_de_queda['Alto'])
    
    
    return [regra_mergulho, regra_emergencia_3, regra_segura, regra_default_segura, regra_flat_spin]