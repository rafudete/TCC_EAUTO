# 📄 regras_fuzzy.py
# Este arquivo centraliza a definição da Base de Regras Fuzzy.

import skfuzzy as fuzz
from skfuzzy import control as ctrl

def definir_regras(sev_pid, pitch, altitude, vel_v, acel_v, risco_de_queda):
    """
    Define e retorna a lista de regras Fuzzy para o sistema.
    
    Recebe: Os objetos Antecedent e Consequent já criados.
    Retorna: Uma lista de objetos ctrl.Rule.
    """
    print("Definindo Base de Regras Fuzzy...")

    # Regra 1: EMERGÊNCIA REAL (Mergulho em alta velocidade)
    regra_emergencia_1 = ctrl.Rule(
        sev_pid['Crítico'] & pitch['Negativo'] & vel_v['Alta'],
        risco_de_queda['Alto']
    )

    # Regra 2: EMERGÊNCIA DO NOSSO CENÁRIO (Mergulho em vel. terminal)
    regra_emergencia_2 = ctrl.Rule(
        sev_pid['Crítico'] & pitch['Negativo'] & vel_v['Moderada'],
        risco_de_queda['Alto']
    )

    # Regra 3: EMERGÊNCIA (Mergulho acelerado)
    regra_emergencia_3 = ctrl.Rule(
        pitch['Negativo'] & acel_v['Acentuada'],
        risco_de_queda['Alto']
    )

    # Regra 4: POUSO NORMAL
    regra_pouso_normal = ctrl.Rule(
        (sev_pid['Suave'] | sev_pid['Moderado']) & 
        pitch['Neutro'] & 
        altitude['Baixa'] & 
        vel_v['Baixa'],
        risco_de_queda['Baixo']
    )

    # Regra 5: REGRA "PEGA-TUDO" (DEFAULT) - Voo não em mergulho
    regra_default_segura = ctrl.Rule(
        pitch['Neutro'] | pitch['Positivo'], 
        risco_de_queda['Baixo']
    )

    print("Regras criadas.")
    
    # Retorna a lista completa de regras
    return [
        regra_emergencia_1, regra_emergencia_2, regra_emergencia_3, 
        regra_pouso_normal, regra_default_segura
    ]