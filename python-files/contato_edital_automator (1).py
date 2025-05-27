# -*- coding: utf-8 -*-
"""
Script para automatizar a busca de contatos a partir de editais em PDF no site FireBuscas.

Fluxo:
1. Abre o navegador e pede ao usuário para fazer login manualmente.
2. Pede ao usuário o caminho do arquivo PDF do edital.
3. Extrai Nomes e Placas do PDF.
4. Navega para a página de busca Interbusca.
5. Para cada Nome/Placa:
   - Busca por Nome.
   - Se múltiplos resultados, busca CPF pela Placa na página Placa Master.
   - Se CPF encontrado, busca por CPF na Interbusca.
   - Extrai o Telefone.
6. Gera um arquivo Excel com os resultados.

Requerimentos:
- Python 3
- Bibliotecas: pandas, selenium
  (Instalar com: pip install pandas selenium)
- Utilitário pdftotext (geralmente parte do poppler-utils)
  (Instalar no Ubuntu/Debian: sudo apt-get update && sudo apt-get install poppler-utils)
- WebDriver para o seu navegador (ex: ChromeDriver para Google Chrome) instalado e no PATH.
"""

import time
import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configurações --- 
LOGIN_URL = "https://firebuscas.com/auth/login"
INTERBUSCA_URL = "https://firebuscas.com/app/modulos/interbusca"
PLACA_MASTER_URL = "https://firebuscas.com/app/modulos/placa-master"
WAIT_TIMEOUT = 20 # Segundos de espera máxima para elementos aparecerem
OUTPUT_FILENAME = "resultados_contatos_editais.xlsx"

# --- Funções Auxiliares --- 

def extract_data_from_pdf_text(text_content):
    """
    Extrai Nome e Placa do conteúdo de texto extraído do PDF (via pdftotext -layout).
    Assume uma estrutura tabular onde Nome e Placa estão em colunas.
    Ajustes podem ser necessários dependendo da variabilidade dos PDFs.
    """
    data = []
    lines = text_content.split('\n')
    print(f"Analisando {len(lines)} linhas do texto extraído...")
    
    # Regex para identificar linhas que provavelmente contêm os dados principais
    # Procura por uma data no início, seguida por texto (Nome), Placa, AIT, etc.
    # Captura Nome (grupo 1) e Placa (grupo 2)
    # Este regex é um ponto de partida e pode precisar de ajustes finos.
    # Considera nomes com espaços, mas tenta evitar capturar cabeçalhos ou texto genérico.
    # A robustez depende da consistência do formato do PDF.
    line_regex = re.compile(r"^(
*\d{2}/\d{2}/\d{4}\s+ # Data no início da linha
*([A-ZÀ-Ú][A-ZÀ-Ú\s]+?) # Nome (letras maiúsculas e espaços, captura não-gulosa)
*\s{2,}              # Pelo menos dois espaços separando Nome da Placa
*([A-Z]{3}[0-9][A-Z0-9][0-9]{2}) # Placa (formato Mercosul ou antigo)
*\s+                 # Espaço após a placa
*.*                  # Restante da linha
*)$", re.VERBOSE | re.MULTILINE)

    matches = line_regex.finditer(text_content)
    
    for match in matches:
        nome = ' '.join(match.group(2).split()) # Limpa espaços extras no nome
        placa = match.group(3)
        # Evitar adicionar nomes muito curtos ou que pareçam cabeçalhos
        if len(nome) > 3 and nome != "NOME":
             data.append({'Nome': nome, 'Placa': placa})
        else:
             # print(f"Skipping potential header or short name: {nome}")
             pass

    if not data:
        print("WARN: Nenhum dado extraído com o regex principal. Tentando método alternativo (baseado na placa)...")
        # Método alternativo: Encontrar placas e tentar pegar o nome antes delas
        plate_regex = re.compile(r'\b([A-Z]{3}[0-9][A-Z0-9][0-9]{2})\b')
        for i, line in enumerate(lines):
            plate_match = plate_regex.search(line)
            if plate_match and len(line.split()) > 3: # Linha com placa e provavelmente outros dados
                plate = plate_match.group(1)
                parts = line.split(plate)[0] # Pega a parte da linha ANTES da placa
                # Tenta extrair o nome dessa parte (ex: remover data e espaços)
                potential_name_parts = re.split(r'\s{2,}', parts.strip())
                if len(potential_name_parts) > 1:
                    potential_name = potential_name_parts[-1].strip()
                    if len(potential_name) > 3 and potential_name.isupper(): # Verifica se parece um nome (maiúsculas)
                        data.append({'Nome': potential_name, 'Placa': plate})

    # Remove duplicatas e retorna
    if not data:
        print("Erro: Não foi possível extrair dados de Nome/Placa do PDF.")
        return []
        
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=['Nome', 'Placa'], inplace=True)
    unique_data = df.to_dict('records')
    
    print(f"Extraídos {len(unique_data)} pares únicos de Nome/Placa.")
    if unique_data:
        print("Exemplo dos dados extraídos:", unique_data[0])
    return unique_data

def setup_driver():
    """Configura e retorna o WebDriver do Selenium."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Descomente para rodar sem abrir janela do navegador (pode dificultar login manual)
    # options.add_argument("user-data-dir=./chrome_profile") # Opcional: Tentar manter sessão
    print("Configurando WebDriver...")
    try:
        driver = webdriver.Chrome(options=options)
        print("WebDriver configurado.")
        return driver
    except Exception as e:
        print(f"Erro ao configurar o WebDriver: {e}")
        print("Verifique se o Google Chrome e o ChromeDriver compatível estão instalados e no PATH do sistema.")
        return None

def wait_for_manual_login(driver):
    """Abre a página de login e aguarda confirmação do usuário."""
    driver.get(LOGIN_URL)
    print("-" * 70)
    print(f"Navegador aberto em: {LOGIN_URL}")
    print("*** POR FAVOR, FAÇA O LOGIN MANUALMENTE NESTA JANELA DO NAVEGADOR ***")
    input("*** Após completar o login, pressione Enter aqui para o script continuar... ***")
    print("Login confirmado pelo usuário. Iniciando a automação das buscas...")
    print("-" * 70)

def get_pdf_path():
    """Solicita ao usuário o caminho do arquivo PDF."""
    while True:
        pdf_path = input("Por favor, arraste o arquivo PDF do edital para esta janela ou cole o caminho completo e pressione Enter:\n").strip()
        pdf_path = pdf_path.replace("'", "").replace("\"", "") # Limpa aspas
        if os.path.exists(pdf_path) and pdf_path.lower().endswith(".pdf"):
            print(f"Arquivo PDF selecionado: {pdf_path}")
            return pdf_path
        else:
            print("Erro: Arquivo não encontrado ou não é um PDF válido. Tente novamente.")

# --- Lógica Principal --- 
def main():
    driver = setup_driver()
    if not driver:
        return

    try:
        wait_for_manual_login(driver)
        pdf_path = get_pdf_path()

        # 1. Extrair texto do PDF
        txt_output_path = "/home/ubuntu/edital_temp_output.txt"
        print(f"Extraindo texto do PDF usando 'pdftotext' para {txt_output_path}...")
        # Usar '-layout' tenta preservar a estrutura original das colunas
        # Usar '-enc UTF-8' para garantir a codificação correta
        os.system(f'pdftotext -layout -enc UTF-8 "{pdf_path}" "{txt_output_path}"')

        if not os.path.exists(txt_output_path):
             print("Erro Crítico: Falha ao extrair texto do PDF com pdftotext. Verifique se 'poppler-utils' está instalado.")
             return

        with open(txt_output_path, 'r', encoding='utf-8', errors='ignore') as f:
            pdf_text_content = f.read()
        os.remove(txt_output_path) # Limpa arquivo temporário
        print("Texto extraído com sucesso.")

        # 2. Parsear texto para obter dados (Nome, Placa)
        extracted_data = extract_data_from_pdf_text(pdf_text_content)
        if not extracted_data:
            return # Erro já reportado na função

        # Lista para armazenar os resultados finais
        results_list = []
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        # 3. Navegar para Interbusca e preparar
        print(f"Navegando para a página Interbusca: {INTERBUSCA_URL}...")
        driver.get(INTERBUSCA_URL)
        
        print("Selecionando tipo de busca 'Nome/Endereço'...")
        # --- !!! SELETOR REAL NECESSÁRIO AQUI !!! ---
        # Este é um EXEMPLO. Inspecione a página real para obter o seletor correto.
        # Pode ser um input radio, um botão, um link, etc.
        try:
            # Exemplo: Procurar por um input radio com um valor específico ou um label associado
            # search_type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='nome_endereco']"))) 
            # Ou por um label:
            search_type_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Nome/Endereço')]"))) # Ajustar texto se necessário
            search_type_label.click()
            print("Tipo de busca 'Nome/Endereço' selecionado.")
        except TimeoutException:
            print("ALERTA: Não foi possível selecionar automaticamente 'Nome/Endereço'. Verifique o seletor ou selecione manualmente se necessário.")
            # Considerar pausar e pedir confirmação manual?
            # input("Verifique se 'Nome/Endereço' está selecionado no navegador e pressione Enter...")
            pass # Continua mesmo assim, assumindo que pode já estar selecionado ou o campo de busca é o mesmo

        # --- !!! SELETORES REAIS NECESSÁRIOS PARA OS CAMPOS E BOTÕES ABAIXO !!! ---
        # Identifique os seletores corretos inspecionando o HTML das páginas no FireBuscas
        INTERBUSCA_INPUT_SELECTOR = (By.ID, "campoDeBuscaInterbusca") # EXEMPLO
        INTERBUSCA_BUTTON_SELECTOR = (By.ID, "botaoBuscarInterbusca") # EXEMPLO
        INTERBUSCA_RESULTS_AREA_SELECTOR = (By.ID, "divResultadosInterbusca") # EXEMPLO
        INTERBUSCA_RESULT_ITEM_SELECTOR = (By.CLASS_NAME, "itemResultado") # EXEMPLO
        INTERBUSCA_TELEFONE_SELECTOR = (By.CLASS_NAME, "telefoneNoResultado") # EXEMPLO
        
        PLACA_MASTER_INPUT_SELECTOR = (By.ID, "campoPlacaMaster") # EXEMPLO
        PLACA_MASTER_BUTTON_SELECTOR = (By.ID, "botaoBuscarPlacaMaster") # EXEMPLO
        PLACA_MASTER_CPF_SELECTOR = (By.ID, "campoResultadoCPF") # EXEMPLO

        # 4. Loop de Busca
        total_items = len(extracted_data)
        print(f"\nIniciando buscas para {total_items} registros...")
        for index, item in enumerate(extracted_data):
            nome = item['Nome']
            placa = item['Placa']
            cpf_encontrado = ''
            telefone_encontrado = ''
            status = "Não encontrado"
            
            print(f"\n[{index + 1}/{total_items}] Buscando Nome: '{nome}' (Placa: {placa}) ...")

            try:
                # Garante que está na página Interbusca (caso tenha navegado para Placa Master)
                if driver.current_url != INTERBUSCA_URL:
                    print(f"Retornando para {INTERBUSCA_URL}...")
                    driver.get(INTERBUSCA_URL)
                    # Pode ser necessário re-selecionar o tipo de busca aqui também
                    try:
                        search_type_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Nome/Endereço')]"))) 
                        search_type_label.click()
                    except: pass # Ignora se não encontrar/precisar

                # Realiza busca por nome
                campo_busca = wait.until(EC.visibility_of_element_located(INTERBUSCA_INPUT_SELECTOR))
                botao_buscar = wait.until(EC.element_to_be_clickable(INTERBUSCA_BUTTON_SELECTOR))
                
                campo_busca.clear()
                campo_busca.send_keys(nome)
                botao_buscar.click()
                print(f"Busca por '{nome}' enviada.")
                time.sleep(1) # Pequena pausa para a busca iniciar

                # Verifica resultados
                try:
                    resultados_area = wait.until(EC.visibility_of_element_located(INTERBUSCA_RESULTS_AREA_SELECTOR))
                    itens_resultado = resultados_area.find_elements(*INTERBUSCA_RESULT_ITEM_SELECTOR)
                    num_resultados = len(itens_resultado)
                    print(f"Resultados encontrados para '{nome}': {num_resultados}")

                    if num_resultados == 1:
                        # Tenta extrair telefone do resultado único
                        try:
                            telefone_element = itens_resultado[0].find_element(*INTERBUSCA_TELEFONE_SELECTOR)
                            telefone_encontrado = telefone_element.text.strip()
                            status = "Telefone encontrado (Nome)"
                            print(f"  -> Telefone: {telefone_encontrado}")
                        except NoSuchElementException:
                            print("  -> Telefone não encontrado no resultado único.")
                            status = "Nome encontrado, sem telefone"

                    elif num_resultados > 1:
                        print("  -> Múltiplos resultados. Tentando busca por Placa para obter CPF...")
                        status = "Nome duplicado, buscando CPF"
                        # Navega para Placa Master
                        driver.get(PLACA_MASTER_URL)
                        campo_placa = wait.until(EC.visibility_of_element_located(PLACA_MASTER_INPUT_SELECTOR))
                        botao_placa = wait.until(EC.element_to_be_clickable(PLACA_MASTER_BUTTON_SELECTOR))
                        
                        campo_placa.clear()
                        campo_placa.send_keys(placa)
                        botao_placa.click()
                        print(f"  -> Busca por Placa '{placa}' enviada.")
                        
                        # Extrai CPF
                        try:
                            cpf_element = wait.until(EC.visibility_of_element_located(PLACA_MASTER_CPF_SELECTOR))
                            cpf_encontrado = cpf_element.text.strip()
                            # Validar formato básico do CPF se necessário
                            if cpf_encontrado and len(cpf_encontrado) >= 11:
                                print(f"  -> CPF encontrado: {cpf_encontrado}")
                                status = "CPF encontrado, buscando telefone"
                                # Volta para Interbusca
                                driver.get(INTERBUSCA_URL)
                                # Seleciona busca por CPF (ou usa o mesmo campo? Assumindo mesmo campo)
                                print(f"  -> Buscando por CPF '{cpf_encontrado}' na Interbusca...")
                                # Re-selecionar tipo de busca se necessário (ex: CPF)
                                # campo_busca = wait.until(...) # Re-localizar campo
                                # botao_buscar = wait.until(...) # Re-localizar botão
                                campo_busca.clear()
                                campo_busca.send_keys(cpf_encontrado)
                                botao_buscar.click()
                                time.sleep(1)
                                
                                # Extrai telefone após busca por CPF
                                try:
                                    resultados_area_cpf = wait.until(EC.visibility_of_element_located(INTERBUSCA_RESULTS_AREA_SELECTOR))
                                    telefone_element_cpf = resultados_area_cpf.find_element(*INTERBUSCA_TELEFONE_SELECTOR)
                                    telefone_encontrado = telefone_element_cpf.text.strip()
                                    status = "Telefone encontrado (CPF)"
                                    print(f"  -> Telefone: {telefone_encontrado}")
                                except (NoSuchElementException, TimeoutException):
                                    print("  -> Telefone não encontrado na busca por CPF.")
                                    status = "CPF encontrado, sem telefone"
                            else:
                                print("  -> CPF inválido ou não encontrado na Placa Master.")
                                status = "Nome duplicado, CPF não encontrado"
                                
                        except TimeoutException:
                            print("  -> CPF não encontrado na busca por Placa.")
                            status = "Nome duplicado, CPF não encontrado"
                            
                    else: # num_resultados == 0
                        print("  -> Nenhum resultado encontrado para o nome.")
                        status = "Nome não encontrado"

                except TimeoutException:
                    print("  -> Nenhum resultado encontrado ou área de resultados não carregou.")
                    status = "Nome não encontrado (Timeout)"
                except Exception as e_res:
                    print(f"  -> Erro ao processar resultados para '{nome}': {e_res}")
                    status = f"Erro nos resultados: {e_res}"

            except Exception as e_busca:
                print(f"Erro geral ao buscar '{nome}': {e_busca}")
                status = f"Erro na busca: {e_busca}"
            
            # Adiciona à lista de resultados
            results_list.append({
                'Nome Original': nome,
                'Placa Original': placa,
                'CPF Encontrado': cpf_encontrado,
                'Telefone Encontrado': telefone_encontrado,
                'Status': status
            })
            
            # Pausa curta para não sobrecarregar
            time.sleep(0.5)

        # 5. Gerar arquivo Excel
        if results_list:
            print(f"\nGerando arquivo Excel: {OUTPUT_FILENAME}...")
            df_results = pd.DataFrame(results_list)
            try:
                df_results.to_excel(OUTPUT_FILENAME, index=False, engine='openpyxl') # Requer 'openpyxl' (pip install openpyxl)
                abs_path = os.path.abspath(OUTPUT_FILENAME)
                print(f"Arquivo '{OUTPUT_FILENAME}' gerado com sucesso.")
                print(f"Caminho completo: {abs_path}")
                # Considerar notificar o usuário aqui com anexo
            except Exception as e_excel:
                 print(f"Erro ao gerar arquivo Excel: {e_excel}")
                 print("Verifique se a biblioteca 'openpyxl' está instalada (pip install openpyxl)")
                 # Tentar salvar como CSV como fallback
                 try:
                     csv_filename = OUTPUT_FILENAME.replace('.xlsx', '.csv')
                     df_results.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                     abs_path_csv = os.path.abspath(csv_filename)
                     print(f"Salvo como CSV: {csv_filename}")
                     print(f"Caminho completo: {abs_path_csv}")
                 except Exception as e_csv:
                     print(f"Erro ao salvar como CSV: {e_csv}")
        else:
            print("Nenhum resultado coletado para gerar arquivo.")

    except Exception as e_geral:
        print(f"\n--- ERRO INESPERADO NO SCRIPT --- ")
        print(e_geral)
    finally:
        print("\nScript finalizado. Fechando o navegador em 10 segundos...")
        time.sleep(10)
        if driver:
            driver.quit()

# --- Ponto de Entrada --- 
if __name__ == "__main__":
    # Verifica dependências básicas
    try:
        import pandas
        from selenium import webdriver
        # Verificar pdftotext?
    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Certifique-se de ter as bibliotecas 'pandas' e 'selenium' instaladas (pip install pandas selenium).",
              "\nE também o 'poppler-utils' (contém pdftotext) e o WebDriver apropriado.")
    else:
        main()

