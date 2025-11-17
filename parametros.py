# 📄 parametros.py

import numpy as np

class Parametros:
    def __init__(self):
        """
        Define TODOS os parâmetros DEFAULTS da simulação.
        """
        # --- PARÂMETROS FÍSICOS DO VANT ---
        self.m = 5.0          # Massa do VANT (kg)
        self.g = 9.81         # Aceleração da gravidade (m/s^2)
        self.rho = 1.225      # Densidade do ar (kg/m^3)
        self.C_d = 0.8        # Coeficiente de arrasto (adimensional)
        self.A = 0.5          # Área de referência (m^2)

        # --- CÁLCULO AUTOMÁTICO DA VELOCIDADE TERMINAL ---
        # v_t = sqrt( (2 * m * g) / (rho * A * C_d) )
        # Usamos -np.sqrt(...) porque é uma velocidade de queda (negativa)
        try:
            self.v_terminal = -np.sqrt( (2 * self.m * self.g) / (self.rho * self.A * self.C_d) )
        except ZeroDivisionError:
            self.v_terminal = -100.0 # Valor de segurança
        # --- FIM DO CÁLCULO ---

        # --- CONDIÇÕES INICIAIS DA SIMULAÇÃO ---
        self.altitude_inicial = 1000.0
        self.velocidade_inicial_padrao = 0.0
        self.tempo_simulacao_max = 60 # segundos
        
        # --- PARÂMETROS ESPECÍFICOS DE FÍSICA ---
        # Para Cenário de Pouso
        self.velocidade_descida_pouso = -5.0 # m/s (uma descida controlada)
        self.K_pouso_vel = 150.0 # Ganho do "controlador" que mantém a vel. de pouso (15x mais)
        # Ganho do "controlador" que mantém o voo nivelado (Vz=0)
        self.K_nivelado_vel = 150.0
        # Força das rajadas de turbulência (em Newtons)
        self.forca_rajada_turbulencia = 50.0 # Newtons (ex: 50N para cima ou para baixo)

        # --- PARÂMETROS DOS SENSORES (RUÍDO, BIAS, FILTRO) ---
        self.taxa_atualizacao_gnss = 5.0 # Hz
        self.sigma_ruido_gnss = 2.0    # metros
        self.sigma_ruido_acel = 0.05   # m/s^2
        self.bias_acel = 0.02          # m/s^2
        self.sigma_ruido_giro = 0.5    # graus
        self.tamanho_janela_filtro = 25  # pontos

        # --- PARÂMETROS DE ANÁLISE TEMPORAL ---
        self.tempo_analise_altitude = 5.0 # Segundos
        self.limiar_queda_lenta = -2.0  # m/s
        self.limiar_queda_rapida = -8.0 # m/s
        self.tempo_persistencia_pitch = 3.0 # Segundos
        self.limiar_pitch_negativo = -10.0  # Graus

        # --- PARÂMETROS DA LÓGICA DE DECISÃO (PID, FUZZY) ---
        self.PID_Kp = 5.0
        self.PID_Ki = 1.0
        self.PID_Kd = 0.5
        self.limiar_disparo_risco = 85.0 # Risco > 85
        self.limiar_reset_timer = 80.0 # --- NOVO PARÂMETRO DE HISTERESE ---
        self.tempo_minimo_disparo = 2.0  # por 2 segundos
        
        # --- PARÂMETROS DO CENÁRIO ESPECÍFICO ---
        # (Estes serão SOBRESCRITOS pelas funções abaixo)
        self.cenario_nome = "Default"
        self.tempo_inicio_mergulho = 0.0
        self.pitch_mergulho_graus = 0.0
        self.pitch_base_graus = 0.0
        self.tempo_inicio_turbulencia = 0.0
        self.duracao_turbulencia = 0.0
        self.amplitude_pitch_turbulencia = 0.0


# --- FUNÇÕES GERADORAS DE CENÁRIO ---
# (O main.ipynb vai chamar estas funções)

def get_cenario_1_queda():
    p = Parametros()
    
    p.cenario_nome = "Cenário 1: Queda LOC-I"
    p.tempo_inicio_mergulho = 2.0
    p.pitch_mergulho_graus = -45.0
    
    return p

def get_cenario_2_pouso():
    p = Parametros()
    
    p.cenario_nome = "Cenário 2: Pouso Normal"
    p.tempo_inicio_mergulho = 2.0  
    p.pitch_mergulho_graus = -5.0 # Única diferença física do Cenário 1
    
    return p

def get_cenario_3_turbulencia():
    p = Parametros()
    
    p.cenario_nome = "Cenário 3: Turbulência Moderada"
    p.pitch_base_graus = 0.0
    p.tempo_inicio_turbulencia = 10.0
    p.duracao_turbulencia = 20.0
    p.amplitude_pitch_turbulencia = 15.0
    
    return p

def get_cenario_4_flat_spin():
    p = Parametros()

    # Simula um "Flat Spin" (Giro Chato)
    # A física é de queda livre (como C1 e C3)
    # O Pitch é nivelado (neutro), sem oscilações

    p.cenario_nome = "Cenário 4: Flat Spin (Giro Chato)"

    # Usa a lógica da "Turbulência" no simulacao_sensores.py,
    # mas com duração zero, para que o pitch fique sempre no 'base'.
    p.pitch_base_graus = 0.0
    p.tempo_inicio_turbulencia = 0.0
    p.duracao_turbulencia = 0.0 # <-- Duração zero = sem oscilação
    p.amplitude_pitch_turbulencia = 0.0

    return p


def get_cenario_5_pouso_turbulencia():
    p = Parametros()

    p.cenario_nome = "Cenário 5: Pouso com Turbulência"

    # 1. Parâmetros da Física de Pouso (Alvo = -5 m/s)
    # (Já estão nos defaults, mas confirmamos)
    p.velocidade_descida_pouso = -5.0
    p.K_pouso_vel = 150.0 

    # 2. Parâmetros da Física de Turbulência (Adiciona Rajadas)
    # (Já está nos defaults, mas confirmamos)
    p.forca_rajada_turbulencia = 50.0 

    # 3. Parâmetros do Sensor de Pitch (Oscilação)
    # O Pitch agora oscila em torno da atitude de pouso (-5)!
    p.pitch_base_graus = -5.0 # <-- MUITO IMPORTANTE!
    p.tempo_inicio_turbulencia = 0.0 # Turbulência durante todo o pouso
    p.duracao_turbulência = 60.0   # Dura a simulação inteira
    p.amplitude_pitch_turbulencia = 15.0 # Mesma amplitude de antes

    return p