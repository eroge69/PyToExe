import openpyxl
import pyautogui as gui
import time
#import keyboard # nao funciona pq a maquina precisa de privilegios de adm ou configuracao especifica do TI
from collections import defaultdict
from datetime import datetime

print("Requisitos para rodar: \n- Deixe o capslock desativado \n- Mantenha o seu login e senha salvo do Serasa no navegador Edge")

#################################################################### UTIL - PYAUTOGUI
def ajustar_coordenadas(x, y, base_width=1920, base_height=1080):
    screen_width, screen_height = gui.size()
    x_adjusted = int((x / base_width) * screen_width)
    y_adjusted = int((y / base_height) * screen_height)
    return x_adjusted, y_adjusted

def detectar_movimento_mouse(posicao_inicial):
    """Verifica se o mouse foi movido pelo usuário."""
    return gui.position() != posicao_inicial

def click_com_verificacao(x, y):
    """Verifica se houve movimento do mouse antes de clicar."""
    posicao_inicial = gui.position()
    time.sleep(0.1)  # Pequena pausa para evitar detecção prematura

    if detectar_movimento_mouse(posicao_inicial):
        print("Movimento de mouse detectado! Automação interrompida.")
        exit()

    gui.click(*ajustar_coordenadas(x, y))
    time.sleep(0.5)  # Pequena pausa após o clique para evitar problemas
    
#################################################################### LEITURA DOS DADOS DO XLSX
# Caminho para o arquivo
arquivo_excel = "BASE DISTRIBUICAO.xlsx"

# Índices das colunas desejadas (base 0)
colunas_desejadas = [0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 27, 28]
# Carrega o arquivo
wb = openpyxl.load_workbook(arquivo_excel, data_only=True)

# Seleciona a planilha
ws = wb["Planilha1"]

# Inicializa o dicionário com listas vazias
colunas = {idx: [] for idx in colunas_desejadas}

# Percorre as linhas da planilha (ignorando a primeira linha)
for linha in list(ws.iter_rows(values_only=True))[1:]:
    for idx in colunas_desejadas:
        valor = linha[idx] if idx < len(linha) else None
        colunas[idx].append(valor)

# Índices das colunas que devem ser tratadas como data
colunas_data = [27, 28]

# Formata datas nas colunas específicas
for idx in colunas_data:
    if idx in colunas:
        col_formatada = []
        for item in colunas[idx]:
            if isinstance(item, datetime):
                col_formatada.append(item.strftime("%d%m%Y"))
            else:
                col_formatada.append(item)
        colunas[idx] = col_formatada

# Exibe os dados das colunas desejadas
for idx in colunas_desejadas:
    print(f"\nColuna {idx + 1}: {colunas[idx]}")

# Descobre o último índice útil na coluna 28
ultimo_indice_util = next((i for i in reversed(range(len(colunas[28]))) if colunas[28][i]), 0) + 1

# Fecha o arquivo
wb.close()  # talvez seja melhor deixar na ultima linha

#################################################################### AUTOMAÇÃO GUI
def btn_acessar():
    try:
        btn_location = gui.locateOnScreen('./assets/acessar.png', confidence=0.8)
        if btn_location is not None:
            x, y = gui.center(btn_location)
            gui.click(x, y)
        else:
            print("Botão 'Acessar' não encontrado na tela, tentando novamente...")
            btn_acessar()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        exit(0)

def popup_erro(i, colunas):
    max_tentativas = 3
    tentativas = 0
    search_region = (674, 904, 61, 97)  # exemplo de região (x, y, largura, altura)

    while tentativas < max_tentativas:
        try:
            btn_location = gui.locateOnScreen('./assets/erro_popup.png', confidence=0.8, region=search_region)
            if btn_location is not None:
                time.sleep(1)
                print(f"\nPop-up de erro encontrado para cliente (grupo/cota/CPF): {colunas[1][i]}/{colunas[2][i]}/{colunas[4][i]}. Inserindo dívida para próxima cota...")
                return True  # Erro encontrado
            else:
                tentativas += 1
                time.sleep(1)
        except Exception as e:
            print(f"Popup de erro nao encontrado: {e}")
            break
            
            #exit(0)

    return False  # Não encontrou erro




def abre_edge():
    # ABRE EDGE (considerando que vai abrir na tela do NOTEBOOK!)
    gui.press('win')
    time.sleep(0.5)
    gui.write('Microsoft Edge')
    time.sleep(0.5)

#    if keyboard.is_pressed('esc'):
#        print("Execução interrompida pelo usuário (ESC pressionado).")
#        exit(0)

    gui.press('enter')
    time.sleep(1)
    # entra no serasa
    click_com_verificacao(809, 63)
    gui.press('del')
    gui.write('https://empresas.serasaexperian.com.br/meus-produtos/login')

#    if keyboard.is_pressed('esc'):
#        print("Execução interrompida pelo usuário (ESC pressionado).")
#        exit(0)

    gui.press('enter')
    time.sleep(12)
    # ENTRA SERASA (considerando que a senha está salva)
    gui.press('enter')
    time.sleep(14)
    gui.hotkey('ctrl', 'f')
    time.sleep(2)
    gui.hotkey('ctrl', 'g')
    gui.write('ACESSAR')
    time.sleep(1)

#    if keyboard.is_pressed('esc'):
#        print("Execução interrompida pelo usuário (ESC pressionado).")
#        exit(0)

    #click_com_verificacao(272, 764)
    btn_acessar()
    time.sleep(8)
    #click_com_verificacao(183, 337)  # ENTRA EM INCLUSÃO DE DÍVIDA
    #time.sleep(4)

def automatiza():
    print("Iniciando automação...\n")
    abre_edge()
    for i in range(ultimo_indice_util):
        #abre_edge() #essa funcao AQUI é apenas para TESTAR, depois tira
        print(f"Iniciando inclusao para proximo grupo/cota/CPF:")
        print(f"{colunas[1][i]}/{colunas[2][i]}/{colunas[4][i]}")

        # Se não houver valor, encerra a função
        if not colunas[28][i]:
            print("\nAutomação finalizada.")
            exit(0)
        else:
            #se for o primeiro loop, vai pressionar tab 6 vezes, se nao preciona tab 2 vezes
            if i == 0:
                click_com_verificacao(183, 337)  # ENTRA EM INCLUSÃO DE DÍVIDA
                time.sleep(4)
                gui.press('tab', presses=6)
            if i > 0:
                click_com_verificacao(183, 337)  # ENTRA EM INCLUSÃO DE DÍVIDA
                time.sleep(4)
                gui.press('tab', presses=2) # 
                time.sleep(6) # para teste

#            if keyboard.is_pressed('esc'):
#                print("Execução interrompida pelo usuário (ESC pressionado).")
#                exit(0)

            time.sleep(1)
            gui.write('/0001-05') #

            gui.press('tab', presses=2)
            gui.write(f"{colunas[27][i]}")
            gui.press('tab', presses=2)
            gui.write(f"{colunas[28][i]}")
            gui.press('tab')
            
            #if keyboard.is_pressed('esc'):
            #    print("Execução interrompida pelo usuário (ESC pressionado).")
            #    exit(0)

            gui.press('enter')
            time.sleep(1)
            gui.press('down', presses=18)

#            if keyboard.is_pressed('esc'):
#                print("Execução interrompida pelo usuário (ESC pressionado).")
#                exit(0)

            gui.press('enter')
            gui.press('tab')
            gui.write(f"{colunas[1][i]}") #GRUPO 
            gui.write(f"/")
            gui.write(f"{colunas[2][i]}") #
            gui.press('tab', presses=2)
            gui.write(f"{colunas[4][i]}") #CPF
            gui.press('tab')

#            if keyboard.is_pressed('esc'):
#                print("Execução interrompida pelo usuário (ESC pressionado).")
#                exit(0)

            #gui.write(f"{colunas[0][i].lower()}") #NOME #botar um upper case aqui
            gui.write(f"{colunas[0][i]}", interval=0.1)
            gui.press('tab')
            gui.write(f"{colunas[12][i]}") #
            time.sleep(2)
            gui.press('tab')

            #ESSES DADOS N ESTAO PADRONIZADOS NO 
            gui.write(f"{colunas[6][i]}", interval=0.1) #
            gui.press('tab')
            gui.write(f"{colunas[7][i]}") #
            gui.press('tab')

#            if keyboard.is_pressed('esc'):
#                print("Execução interrompida pelo usuário (ESC pressionado).")
#                exit(0)

            gui.write(f"{colunas[8][i]}", interval=0.1) #
            gui.press('tab')
            gui.write(f"{colunas[9][i]}", interval=0.1) #
            gui.press('tab')
            gui.write(f"{colunas[11][i]}", interval=0.1) #
            gui.press('tab')
            gui.write(f"{colunas[10][i]}", interval=0.1) 

            # ENVIANDO A INCLUSAO DE DIVIDA
            gui.hotkey('ctrl', 'f')
            time.sleep(2)
            gui.hotkey('ctrl', 'g')
            gui.write('enviar')
            time.sleep(1)
            gui.moveTo(1756, 964)

            time.sleep(2)

#            if keyboard.is_pressed('esc'):
#                print("Execução interrompida pelo usuário (ESC pressionado).")
#                exit(0)

#################################################################### P/ TESTE 
            # vou adicionar uma confirmaçao aqui na cli
            #print("Clique na tela para confirmar o envio da inclusao de divida.")
            #print("Aperte 'Enter' para continuar.")
            #input()
####################################################################
            click_com_verificacao(1756, 964)
            time.sleep(2)

            # Se NÃO encontrou erro, confirma com tab + enter
            if not popup_erro(i, colunas):
                gui.press('tab', presses=2)
                gui.press('enter')
                print(f"Dívida enviada com sucesso para o GRUPO/COTA/CPF:")
            else:
                #exit(0) # TESTAR AQUI
                print("\nErro detectado. Pulando para o próximo...")
                #Atualiza pagina para limpar o formulario
                gui.press('f5')
                time.sleep(4)

            print(f"{colunas[1][i]}/{colunas[2][i]}/{colunas[4][i]}")


automatiza()