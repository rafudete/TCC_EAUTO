# 📄 parametros.py
# Seu "painel de controle" para definir QUAL cenário você quer rodar.

# --- PARÂMETROS FÍSICOS DO VANT ---
# (Valores fictícios do VANT, m, g, rho, etc.)
m = 5.0          # Massa do VANT (kg)
g = 9.81         # Aceleração da gravidade (m/s^2)
rho = 1.225      # Densidade do ar (kg/m^3)
C_d = 0.8        # Coeficiente de arrasto (adimensional)
A = 0.5          # Área de referência (m^2)

# --- CONDIÇÕES INICIAIS DA SIMULAÇÃO ---
altitude_inicial = 1000.0
velocidade_inicial = 0.0
tempo_simulacao_max = 60 # segundos

# --- PARÂMETROS DOS SENSORES (RUÍDO, BIAS, FILTRO) ---
taxa_atualizacao_gnss = 5.0 # Hz
sigma_ruido_gnss = 2.0    # metros
sigma_ruido_acel = 0.05   # m/s^2
bias_acel = 0.02          # m/s^2
sigma_ruido_giro = 0.5    # graus
tamanho_janela_filtro = 25  # pontos

# --- PARÂMETROS DA LÓGICA DE DECISÃO (PID, FUZZY) ---
# Ganhos do PID
PID_Kp = 5.0
PID_Ki = 1.0
PID_Kd = 0.5

# Limiares de Disparo
limiar_disparo_risco = 85.0 # Risco > 85
tempo_minimo_disparo = 2.0  # por 2 segundos

# ---------- PARÂMETROS DO CENÁRIO ESPECÍFICO -------------

# ---------- Cenário 1: Queda (Mergulho) (Comentado)
# cenario_nome = "Cenário 1: Queda LOC-I"
# tempo_inicio_mergulho = 2.0  # Usado pela lógica "Queda" ou "Pouso"
# pitch_mergulho_graus = -45.0 # Usado pela lógica "Queda" ou "Pouso"

# ---------- Cenário 2: Pouso Normal (Comentado)
# cenario_nome = "Cenário 2: Pouso Normal"
# tempo_inicio_mergulho = 2.0  # Usado pela lógica "Queda" ou "Pouso"
# pitch_mergulho_graus = -5.0  # Usado pela lógica "Queda" ou "Pouso"

# ---------- Cenário 3: Turbulência (ATIVO)
cenario_nome = "Cenário 3: Turbulência Moderada"

# Variáveis específicas para a lógica de Turbulência:
pitch_base_graus = 0.0             # O VANT tenta voar reto (0 graus)
tempo_inicio_turbulencia = 10.0    # Começa aos 10 segundos
duracao_turbulencia = 20.0         # Dura 20 segundos (até t=30s)
amplitude_pitch_turbulencia = 15.0 # Oscilações aleatórias de até +/- 15 graus

# (As variáveis tempo_inicio_mergulho e pitch_mergulho_graus não são usadas neste cenário)