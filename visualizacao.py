# 📄 visualizacao.py

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from IPython.display import display, Markdown

def plotar_fisica_base(tempo, altitudes, velocidades):
    """
    GRÁFICO 1: O PROBLEMA (FÍSICA PURA)
    Mostra o "Cenário Base" (Item 3.5.1) sem nenhuma intervenção.
    """
    print("Visualizando [Gráfico 1]: Simulação da Física Pura...")
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(tempo, altitudes)
    plt.title('Altitude vs. Tempo (Real)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Altitude (m)')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(tempo, velocidades)
    plt.title('Velocidade Vertical vs. Tempo (Real)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade (m/s)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plotar_decisao_final(tempo, risco_calculado_fuzzy, 
                         severidade_pid,
                         pitch_sensor_giro):
    """
    GRÁFICO 3: O "CÉREBRO" EM AÇÃO (A DECISÃO)
    O gráfico mais importante. Mostra o Risco Fuzzy sendo calculado
    com base nos inputs (PID e Pitch).
    """
    print("Visualizando [Gráfico 3]: Decisão Final do Sistema Fuzzy...")
    plt.figure(figsize=(14, 8))

    # Gráfico 1: A Saída do Risco Fuzzy
    plt.subplot(2, 1, 1) # <-- 2 linhas, gráfico 1
    plt.plot(tempo, risco_calculado_fuzzy, 'r-', linewidth=2, label='Risco de Queda (Saída Fuzzy)')
    plt.title('Decisão do Sistema Fuzzy (Risco de Queda)')
    plt.ylabel('Risco Calculado (0 a 100)')
    plt.legend()
    plt.grid(True)

    # Gráfico 2: Os Inputs mais importantes
    plt.subplot(2, 1, 2) # <-- 2 linhas, gráfico 2
    plt.plot(tempo, severidade_pid, 'b--', alpha=0.7, label='Severidade PID (Input)') # <-- REATIVADO
    plt.plot(tempo, pitch_sensor_giro, 'g--', alpha=0.7, label='Pitch (Input)')
    plt.title('Principais Sinais de Entrada (Contexto)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Valor do Sinal')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def plotar_sensores_consolidados(p, tempo, dados_reais, dados_sensores):
    """
    GRÁFICO 2/3 CONSOLIDADOS: Mostra todos os sensores brutos e filtrados.
    """
    print("Visualizando [Gráfico 2]: Sensores (Brutos e Filtrados)...")
    plt.figure(figsize=(12, 10)) # Figura alta para 3 gráficos

    # --- Gráfico 1: Altitude GNSS ---
    plt.subplot(3, 1, 1) # 3 linhas, 1 coluna, gráfico 1
    plt.plot(tempo, dados_reais['altitude'], 'b-', label='Altitude Real (Perfeita)')
    plt.plot(tempo, dados_sensores['altitude_gnss'], 'r.', markersize=2, label=f'Leitura GNSS (5 Hz, $\sigma$={p.sigma_ruido_gnss}m)')
    plt.title('Simulação do Altímetro GNSS (Input Bruto)')
    plt.ylabel('Altitude (m)')
    plt.legend()
    plt.grid(True)

    # --- Gráfico 2: Aceleração IMU ---
    plt.subplot(3, 1, 2) # 3 linhas, 1 coluna, gráfico 2
    plt.plot(tempo, dados_reais['aceleracao'], 'b-', label='Aceleração Real (Perfeita)')
    plt.plot(tempo, dados_sensores['aceleracao_imu'], 'g-', alpha=0.7, label=f'Leitura IMU (com Bias e Ruído)')
    plt.title('Simulação do Acelerômetro (Input Bruto)')
    plt.ylabel('Aceleração (m/s^2)')
    plt.legend()
    plt.grid(True)

    # --- Gráfico 3: Filtro de Velocidade ---
    plt.subplot(3, 1, 3) # 3 linhas, 1 coluna, gráfico 3
    plt.plot(tempo, dados_reais['velocidade'], 'b-', label='Velocidade Real (Perfeita)')
    plt.plot(tempo, dados_sensores['velocidade_estimada_gnss'], 'm-', alpha=0.15, label='Velocidade GNSS (Sujo)')
    plt.plot(tempo, dados_sensores['velocidade_filtrada_gnss'], 'r-', linewidth=2, label='Velocidade FILTRADA (Suavizada)')
    
    fronteira_perigosa = p.v_terminal * 0.5 
    plt.axhline(y=fronteira_perigosa, color='cyan', linestyle='--', linewidth=2, 
                label=f'Fronteira "Baixo Risco" ({fronteira_perigosa:.2f} m/s)')
    
    plt.title('Resultado do Filtro de Média Móvel (Input Pré-processado)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade (m/s)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def analisar_resultados(p, tempo, dados_sensores, 
                        severidade_pid, # <-- REATIVADO
                        risco_calculado_fuzzy, 
                        pitch_medio, lista_prox_v_terminal, 
                        fuzzy_vars, fuzzy_defs):
    """
    Analisa os resultados e imprime o RELATÓRIO EM TABELA DETALHADO.
    (Versão com PRINTS DE DEBUG no timer)
    """
    print("\n--- Análise da Tomada de Decisão (Item 3.3.2) ---")
    intervalo_tempo_dt = tempo[1] - tempo[0]
    contador_tempo_seguro = 0.0
    disparado = False
    i_disparo = -1 

    # --- NOVO BLOCO DE DEBUG ---
    print("\n--- DEBUG DO TIMER DE DISPARO (Limiar > %.2f por %.1fs) ---" % (p.limiar_disparo_risco, p.tempo_minimo_disparo))
    timer_ativo_na_iteracao_anterior = False
    # --- FIM DO NOVO BLOCO ---

    for i in range(len(risco_calculado_fuzzy)):
        risco_atual = risco_calculado_fuzzy[i] # Pega o risco atual

        # (Novo timer com HISTERESE, dentro de analisar_resultados)
        # CONDIÇÃO DE ATIVAÇÃO: Risco > 85
        if risco_atual > p.limiar_disparo_risco:
            contador_tempo_seguro += intervalo_tempo_dt

            if not timer_ativo_na_iteracao_anterior:
                print(f"t={tempo[i]:.2f}s: CONDIÇÃO ATIVADA (Risco {risco_atual:.2f} > {p.limiar_disparo_risco}). Timer INICIADO.")
            timer_ativo_na_iteracao_anterior = True

        # CONDIÇÃO DE RESET: Risco < 80 (o novo limiar)
        elif risco_atual < p.limiar_reset_timer: 
            if timer_ativo_na_iteracao_anterior:
                print(f"t={tempo[i]:.2f}s: CONDIÇÃO FALHOU (Risco {risco_atual:.2f} <= {p.limiar_reset_timer}). Timer RESETADO para 0.0s!")

            contador_tempo_seguro = 0.0
            timer_ativo_na_iteracao_anterior = False

        else: # Risco está na "zona segura" (entre 80 e 85)
            if timer_ativo_na_iteracao_anterior:
                # O timer já estava rodando? Ótimo, continua rodando!
                contador_tempo_seguro += intervalo_tempo_dt
        
        if contador_tempo_seguro >= p.tempo_minimo_disparo and not disparado:
            print(f"\n*** DISPARO DO PARAQUEDAS ACIONADO! ***")
            print(f"Cenário: {p.cenario_nome}")
            print(f"Tempo da simulação: {tempo[i]:.2f} segundos.")
            print(f"Condição: Risco ({risco_atual:.1f}) > {p.limiar_disparo_risco} (Sustentado por {contador_tempo_seguro:.2f}s)")
            disparado = True
            i_disparo = i
            break 

    print("--- FIM DO DEBUG DO TIMER ---") # <-- DEBUG

    # --- INÍCIO DO RELATÓRIO DETALHADO EM TABELA ---
    i_critico = -1
    if disparado:
        i_critico = i_disparo
    else:
        print("\nSistema permaneceu estável. Paraquedas não foi acionado.")
        i_critico = np.argmax(risco_calculado_fuzzy) # Índice do risco máximo

    if i_critico == -1: i_critico = 0 

    print(f"\n--- RELATÓRIO DO INSTANTE CRÍTICO (t={tempo[i_critico]:.2f}s) ---")

    # 1. Pega os valores "críticos"
    val_risco = risco_calculado_fuzzy[i_critico]
    val_sev_pid = severidade_pid[i_critico] # <-- REATIVADO
    val_pitch_medio = pitch_medio[i_critico]
    val_alt_raw = dados_sensores['altitude_gnss'][i_critico]
    val_acel_raw = dados_sensores['aceleracao_imu'][i_critico]
    val_prox_v_term = lista_prox_v_terminal[i_critico]

    # 2. Pega as definições das variáveis Fuzzy do "pacote"
    v = fuzzy_vars # Apenas um apelido

    # 3. Função auxiliar para calcular pertinência e achar faixas
    def get_pertinencia(fuzzy_var_obj, var_name_str, valor):
        """
        Calcula a pertinência e busca a definição da faixa no 'fuzzy_defs'.
        """
        pertinencias = []
        for term_name, term_obj in fuzzy_var_obj.terms.items():
            p_val = fuzz.interp_membership(fuzzy_var_obj.universe, term_obj.mf, valor)

            if p_val > 0.01: # Só mostra se for > 1%
                try:
                    faixa_str = fuzzy_defs[var_name_str][term_name]
                except KeyError:
                    faixa_str = "[Definição não encontrada]"

                pertinencias.append(f"**{p_val*100:.1f}% '{term_name}'** (Faixa: {faixa_str})")

        return "<br>".join(pertinencias) if pertinencias else "Nenhuma"

    # 4. Construir a Tabela Markdown
    md_string = f"| Variável (Input Fuzzy) | Valor no Instante | Análise de Pertinência (Como o 'Cérebro' Viu) |\n"
    md_string += "| :--- | :--- | :--- |\n"
    md_string += f"| 1. Pitch Médio (Média 3s) | **{val_pitch_medio:.2f} graus** | {get_pertinencia(v['pitch_medio'], 'pitch_medio', val_pitch_medio)} |\n"
    md_string += f"| 2. Proximidade V-Terminal | **{val_prox_v_term*100:.1f}%** | {get_pertinencia(v['proximidade_v_terminal'], 'proximidade_v_terminal', val_prox_v_term)} |\n"
    md_string += f"| 3. Severidade PID | **{val_sev_pid:.2f}** | {get_pertinencia(v['sev_pid'], 'sev_pid', val_sev_pid)} |\n" # <-- REATIVADO
    md_string += f"| 4. Altitude (Bruta) | **{val_alt_raw:.2f} m** | {get_pertinencia(v['altitude'], 'altitude', val_alt_raw)} |\n"
    md_string += f"| 5. Aceleração (Bruta) | **{val_acel_raw:.2f} m/s^2** | {get_pertinencia(v['acel_v'], 'acel_v', val_acel_raw)} |\n"
    md_string += f"| **SAÍDA (Resultado)** | **{val_risco:.2f}** | **{get_pertinencia(v['risco_de_queda'], 'risco_de_queda', val_risco)}** |\n"

    # 5. Exibir a tabela no Notebook
    display(Markdown(md_string))

    print("\n--- CRITÉRIOS DE DISPARO (ANÁLISE TEMPORAL) ---")
    print(f"-> O Risco é > {p.limiar_reset_timer}? {'Sim' if val_risco > p.limiar_reset_timer else 'Não'}")