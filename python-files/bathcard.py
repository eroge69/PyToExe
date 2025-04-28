import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Simulação de "banco de dados" de cartões
cartoes_db = {}

# Gera número de cartão (usando algoritmo de Luhn simplificado)
def gerar_numero_cartao():
    def luhn_checksum(card_number):
        def digits_of(n): return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        total = sum(odd_digits)
        for d in even_digits:
            total += sum(digits_of(d * 2))
        return total % 10

    base = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(14)]
    check_digit = [str((10 - luhn_checksum(int(''.join(map(str, base)) + '0'))) % 10)]
    return ''.join(map(str, base)) + check_digit[0]

# Formata saldo como R$ x.xxx,xx
def formatar_saldo(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# App principal
class BathCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BathCard Tracking")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.logo_img = None
        self.carregar_tela_login()

    def carregar_logo(self, frame):
        try:
            logo = Image.open("logo.png").resize((180, 100))
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(frame, image=self.logo_img).pack(pady=10)
        except:
            tk.Label(frame, text="[Logo não encontrada]", font=("Arial", 14)).pack(pady=10)

    def carregar_tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(frame, text="Login - BathCard Tracking", font=("Arial", 16)).pack(pady=10)

        tk.Label(frame, text="Usuário:").pack()
        user_entry = tk.Entry(frame)
        user_entry.pack()

        tk.Label(frame, text="Senha:").pack()
        pass_entry = tk.Entry(frame, show="*")
        pass_entry.pack()

        def login_falso():
            self.carregar_tela_menu()

        tk.Button(frame, text="Entrar", command=login_falso).pack(pady=10)

    def carregar_tela_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        self.carregar_logo(frame)

        tk.Label(frame, text="Bem-vindo ao BathCard Tracking!", font=("Arial", 14, "bold")).pack(pady=5)

        tk.Button(frame, text="💳 Consultar Saldo", width=25, command=self.carregar_tela_consulta).pack(pady=10)
        tk.Button(frame, text="💰 Gerar Novo Cartão", width=25, command=self.carregar_tela_gerar).pack(pady=5)

    def carregar_tela_consulta(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(frame, text="Consultar Saldo", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(frame, text="Digite o número do cartão:").pack()
        cartao_entry = tk.Entry(frame, width=30)
        cartao_entry.pack()

        def consultar():
            num = cartao_entry.get().strip()
            if num == "":
                messagebox.showwarning("Erro", "Digite um número de cartão.")
                return
            if num not in cartoes_db:
                saldo = random.randint(2000, 45000)
                cartoes_db[num] = saldo
            else:
                saldo = cartoes_db[num]
            messagebox.showinfo("Saldo Encontrado", f"Saldo do cartão:\n{formatar_saldo(saldo)}")

        tk.Button(frame, text="Consultar", command=consultar).pack(pady=10)
        tk.Button(frame, text="Voltar", command=self.carregar_tela_menu).pack()

    def carregar_tela_gerar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(frame, text="Novo Cartão Gerado", font=("Arial", 14, "bold")).pack(pady=10)

        novo_cartao = gerar_numero_cartao()
        saldo = random.randint(2000, 45000)
        cartoes_db[novo_cartao] = saldo

        tk.Label(frame, text=f"Número: {novo_cartao}", font=("Arial", 12)).pack(pady=5)
        tk.Label(frame, text=f"Saldo: {formatar_saldo(saldo)}", font=("Arial", 12, "bold")).pack(pady=5)

        tk.Button(frame, text="Voltar", command=self.carregar_tela_menu).pack(pady=10)

# Executar
if __name__ == "__main__":
    root = tk.Tk()
    app = BathCardApp(root)
    root.mainloop()
