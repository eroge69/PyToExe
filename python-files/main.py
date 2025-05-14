pip install pyinstaller
import tkinter as tk
from tkinter import messagebox


# Função para verificar a senha
def verificar_senha():
    senhas_validas = {"GITNXI", "R2PNDQ", "BPT316", "X4OY68", "7UX04I"}
    senha = entry_senha.get()
    if senha in senhas_validas:
        janela_senha.destroy()
        criar_interface()
    else:
        messagebox.showerror("Erro", "Senha inválida!")

# Função para criar a interface gráfica com a tabela
def criar_interface():
    def somar_itens():
        totais = {i: 0 for i in range(10, 21)}  # Para os níveis 10 a 20
        for conta in range(1, num_contas + 1):
            for item in range(10, 20):
                try:
                    quantidade = int(entries[conta-1][item-10].get())
                except ValueError:
                    quantidade = 0
                totais[item] += quantidade

        # Transformações
        for lvl in range(10, 20):
            if totais[lvl] >= 2:
                totais[lvl + 1] += totais[lvl] // 2
                totais[lvl] = totais[lvl] % 2

        # Atualizar os rótulos
        for lvl in range(10, 21):
            label_totais[lvl - 10].config(text=f"Nível {lvl}: {totais[lvl]}")

    def iniciar_tabela():
        global num_contas  # Corrigido aqui

        try:
            num_contas = int(entry_num_contas.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido.")
            return

        if not 1 <= num_contas <= 10:
            messagebox.showerror("Erro", "Número de contas deve estar entre 1 e 10.")
            return

        # Esconder entrada inicial
        label_num_contas.grid_forget()
        entry_num_contas.grid_forget()
        botao_iniciar.grid_forget()

        global entries
        entries = []

        # Cabeçalho com níveis
        for i, item in enumerate(range(10, 20)):
            tk.Label(janela_principal, text=str(item)).grid(row=0, column=i + 1)

        # Preencher tabela de entradas
        for conta in range(1, num_contas + 1):
            tk.Label(janela_principal, text=f"Conta {conta}").grid(row=conta, column=0)
            linha = []
            for item in range(10, 20):
                e = tk.Entry(janela_principal, width=5)
                e.grid(row=conta, column=item - 9)
                linha.append(e)
            entries.append(linha)

        # Botão de somar
        botao_somar.grid(row=num_contas + 1, column=0, columnspan=10, pady=10)

        # Totais
        global label_totais
        label_totais = []
        for i, lvl in enumerate(range(10, 21)):
            lbl = tk.Label(janela_principal, text=f"Nível {lvl}: 0")
            lbl.grid(row=num_contas + 2 + i, column=0, columnspan=10, sticky="w", padx=10)
            label_totais.append(lbl)

    janela_principal = tk.Tk()
    janela_principal.title("Tabela de Contas")

    # Entrada do número de contas
    label_num_contas = tk.Label(janela_principal, text="Quantas contas (1-10)?")
    label_num_contas.grid(row=0, column=0, columnspan=2, pady=10)

    entry_num_contas = tk.Entry(janela_principal)
    entry_num_contas.grid(row=1, column=0, columnspan=2, pady=10)

    botao_iniciar = tk.Button(janela_principal, text="Iniciar", command=iniciar_tabela)
    botao_iniciar.grid(row=2, column=0, columnspan=2, pady=10)

    botao_somar = tk.Button(janela_principal, text="Somar Itens", command=somar_itens)

    janela_principal.mainloop()

# Tela de senha inicial
janela_senha = tk.Tk()
janela_senha.title("Autenticação")

label_senha = tk.Label(janela_senha, text="Digite a senha:")
label_senha.grid(row=0, column=0, padx=10, pady=10)

entry_senha = tk.Entry(janela_senha, show="*")
entry_senha.grid(row=1, column=0, padx=10, pady=10)

botao_verificar = tk.Button(janela_senha, text="Verificar", command=verificar_senha)
botao_verificar.grid(row=2, column=0, padx=10, pady=10)

janela_senha.mainloop()