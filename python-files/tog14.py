import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from tkinter.ttk import Scrollbar
import pandas as pd
import os
import random
import re


def select_file():
    root = tk.Tk()
    root.withdraw()  # Fecha a janela principal do tkinter
    root.attributes('-topmost', True)  # Define o foco da janela para a frente

    file_path = filedialog.askopenfilename(parent=root, title="Selecione o arquivo CSV 'results'",
                                           filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")))

    if file_path:
        filename, file_extension = os.path.splitext(file_path)
        if file_extension.lower() != ".csv" or os.path.basename(file_path).lower() != "results.csv":
            print("Por favor, selecione um arquivo CSV chamado 'results.csv'.")
        else:
            process_sample(file_path)
            print("Arquivo CSV com as corridas selecionadas e o ID da amostra salvo com sucesso!")


def process_sample(csv_file):
    df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8', decimal=',')
    random_number = random.randint(1, 999999999)

    # Cria a janela e a barra de rolagem
    root = tk.Tk()
    root.title("Escolha de Corridas")
    frame = tk.Frame(root)
    frame.pack()

    scrollbar = Scrollbar(frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    # Obtém a lista de corridas (valores únicos da coluna 'No.')
    corridas = df['No.'].unique()

    # Cria a caixa de seleção para as corridas
    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, selectmode="multiple")
    for corrida in corridas:
        listbox.insert("end", corrida)
    listbox.pack(side="left", fill="both")

    scrollbar.config(command=listbox.yview)

    # Função para processar a seleção do usuário
    def ok():
        selected_indices = listbox.curselection()
        if len(selected_indices) != 2:
            messagebox.showerror("Erro", "Por favor, selecione exatamente duas corridas.")
            return

        selected_runs = [listbox.get(i) for i in selected_indices]

        # Filtra o DataFrame para incluir apenas as corridas selecionadas
        df_selected = df[df['No.'].isin(selected_runs)]

        # Solicita ao usuário o ID da amostra
        sample_id = simpledialog.askstring("ID da Amostra", "Digite o ID da amostra (8 dígitos):", parent=root)

        if not sample_id:
            messagebox.showerror("Erro", "ID da amostra não fornecido.")
            return

        # Verifica se o ID da amostra tem 8 dígitos
        if not re.match(r'^\d{8}$', sample_id):
            messagebox.showerror("Erro", "ID da amostra deve conter exatamente 8 dígitos numéricos.")
            return

        # Solicita ao usuário a confirmação da diluição 1x
        confirm_dilution = messagebox.askyesno("Confirmação de Diluição", "Confirma a diluição de 1x para a amostra?")

        if confirm_dilution:
            dilution = 1
        else:
            dilution = simpledialog.askinteger("Diluição", "Digite o valor da diluição (número inteiro):", parent=root)
            if dilution is None:
                messagebox.showerror("Erro", "Diluição não fornecida.")
                return

        # Insere o ID da amostra e a diluição na primeira coluna (coluna 'No.') e desloca as outras colunas
        df_selected.insert(0, 'ID da Amostra', sample_id)
        df_selected.insert(1, 'Diluição', dilution)

        # Transpõe as linhas e adiciona barras entre os valores das colunas
        df_selected = df_selected.T.apply(lambda x: '/'.join(map(str, x)), axis=1)

        # Salva o DataFrame transposto em um novo arquivo CSV com o nome 'ID' concatenado a um número aleatório
        random_number_sm = random.randint(1, 99999999999)
        file_name = f"ID_{random_number_sm}_Amostra_{sample_id}.csv"
        csv_file_path_sm = fr"\\sbcas219\PDAFolder\Parsing\TOG14\{file_name}"
        df_selected.to_csv(csv_file_path_sm, header=False)

        # Parte adicional para consultar a planilha e inserir a informação correspondente
        folder_name = os.path.basename(os.path.dirname(csv_file))  # Nome da pasta onde o arquivo foi selecionado
        df_dados_tog14 = pd.read_excel(r'\\sbcas219\PDAFolder\Planilhas de suporte\Dados TOG14.xlsx')

        # Encontra a linha correspondente ao folder_name na coluna Serialno
        row = df_dados_tog14[df_dados_tog14['Serialno'] == folder_name]

        if not row.empty:
            identity_value = row.iloc[0, 0]  # Pega o valor da primeira coluna (Identity)

            # Verifica e manipula o código da proveta
            proveta_code = row.iloc[0, 2]  # Pega o valor da coluna 'proveta'

            if pd.notna(proveta_code):  # Se o valor da proveta já existe
                confirm_proveta = messagebox.askyesno("Confirmação de Proveta",
                                                      f"O código da proveta é '{proveta_code}'. Deseja confirmá-lo?")
                if not confirm_proveta:
                    proveta_code = simpledialog.askstring("Código da Proveta",
                                                          "Digite o código da proveta (deve começar com 'PROVET' seguido de 4 dígitos):",
                                                          parent=root)
                    if not re.match(r'^PROVET\d{4}$', proveta_code):
                        messagebox.showerror("Erro", "Código da proveta inválido.")
                        return
                    # Atualiza o código da proveta na planilha
                    df_dados_tog14.loc[df_dados_tog14['Serialno'] == folder_name, 'proveta'] = proveta_code
                    df_dados_tog14.to_excel(r'\\sbcas219\PDAFolder\Planilhas de suporte\Dados TOG14.xlsx', index=False)
            else:
                proveta_code = simpledialog.askstring("Código da Proveta",
                                                      "Digite o código da proveta (deve começar com 'PROVET' seguido de 4 dígitos):",
                                                      parent=root)
                if not re.match(r'^PROVET\d{4}$', proveta_code):
                    messagebox.showerror("Erro", "Código da proveta inválido.")
                    return
                # Atualiza o código da proveta na planilha
                df_dados_tog14.loc[df_dados_tog14['Serialno'] == folder_name, 'proveta'] = proveta_code
                df_dados_tog14.to_excel(r'\\sbcas219\PDAFolder\Planilhas de suporte\Dados TOG14.xlsx', index=False)

            # Adiciona a informação de 'Identity' e 'Proveta' no arquivo gerado
            with open(csv_file_path_sm, 'a') as f:
                f.write(f'\nIdentity: {identity_value}\n')
                f.write(f'Proveta: {proveta_code}\n')

        print(
            f"Arquivo CSV com as corridas selecionadas, o ID da amostra '{sample_id}', a diluição '{dilution}', a identidade '{identity_value}' e a proveta '{proveta_code}' salvo em: {csv_file_path_sm}")

        # Pergunta ao operador se deseja entrar outra amostra
        another_sample = messagebox.askyesno("Outra Amostra", "Deseja entrar resultado de outra amostra?")
        if another_sample:
            root.destroy()
            select_file()
        else:
            root.destroy()

    # Botão para confirmar a seleção
    button = tk.Button(root, text="OK", command=ok)
    button.pack()

    root.mainloop()


if __name__ == "__main__":
    select_file()
