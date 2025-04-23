import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import random
import string
import time

# ==== NOMES humanizados e gamers ====
nomes_base = [
    # Nomes comuns/brasileiros
    "alex", "joao", "maria", "enzo", "lara", "isa", "kaique", "aline", "davi", "sofia", 
    "miguel", "beatriz", "luan", "julinha", "felipe", "luis", "bia", "rafa", "carol", "nath",
    "pedro", "lucas", "gabriel", "daniela", "vitoria", "augusto", "bia", "renata", "matheus", "carla",
    "bianca", "rodrigo", "elisa", "sandro", "patricia", "rafaela", "jose", "renato", "mariana", "luana",
    "andrea", "caroline", "igor", "julia", "aline", "mario", "luiz", "andre", "carla", "antonio",
    "vinicius", "aline", "paula", "sergio", "valeria", "simon", "juliana", "joana", "alice", "marcio",
    "edson", "roberta", "diana", "samanta", "giselle", "roberto", "patricia", "carla", "renato", "renata",
    "augusto", "bruna", "alessandra", "bruna", "amanda", "luciana", "alves", "rafael", "barbara", "esther",
    "michele", "eliane", "tania", "josefina", "giovana", "luciene", "renata", "paula", "gisele", "marilia",
    "fabiana", "tatiane", "teresa", "marilia", "catarina", "giselle", "lidiane", "luciana", "flavia", "renata",
    "marcia", "edson", "patricia", "celia", "marlene", "vanessa", "adriana", "fabiana", "sueli", "ana", "marta",
    "carla", "aline", "lilian", "naomi", "suzana", "priscila", "jaqueline", "eduarda", "karen", "luana",
    "fabiana", "monique", "rosana", "regina", "ricardo", "frederico", "mariana", "jose", "regina", "debora",
    "thais", "natalia", "josefina", "yara", "marcia", "sergio", "luana", "carla", "erica", "maria", "priscila", "valeria", "luana", "graziela", "eliane", "marcia", "gilda", "vera", "margarida", "roberto", "graziela", "erica", "carla", "rebecca", "milena",

    # Nomes internacionais
    "jordan", "mika", "lucas", "sam", "noah", "ryan", "chloe", "mia", "bella", "zoe",
    "leo", "mark", "ash", "toby", "jen", "ethan", "ava", "emily", "ella", "harry",
    "william", "liam", "lucas", "maya", "evan", "zoey", "james", "olivia", "emma", "jack",
    "grace", "mia", "riley", "oliver", "sophia", "jacob", "noah", "jasmine", "benjamin", "lily",
    "elizabeth", "jackson", "charlotte", "lucy", "leo", "lily", "aaron", "violet", "willow", "scarlett",
    "ella", "ariana", "sydney", "luke", "emma", "isaac", "matthew", "jack", "evan", "ryan",
    "jordan", "caleb", "harper", "mason", "gabrielle", "charlie", "mila", "cooper", "olga", "finn",
    "molly", "annie", "madeline", "olga", "ryan", "clara", "kylie", "emilia", "lucas", "henry", "lucas",
    "adam", "ashley", "michael", "nathan", "bethany", "savannah", "chase", "vaughn", "andrew", "alison",
    "jessie", "cameron", "isaac", "jonathan", "noelle", "gregory", "ella", "daniel", "louis", "julia", 
    "ellen", "gabe", "danny", "melissa", "ella", "victoria", "melissa", "george", "rosemary", "taylor", 
    "caleb", "brandon", "alice", "clara", "kevin", "noel", "paul", "aidan", "jasmine", "zoe", "nash", "charlie", "spencer",
    "lindsay", "hunter", "ian", "maya", "kaitlyn", "vivian", "angela", "jacob", "erin", "gail", "bryce", "jameson", "harry", "simon", "freddie", "oscar",

    # Estilo gamer
    "shadow", "dark", "ninja", "sniper", "killer", "ghost", "storm", "frost", "blaze", "wolf",
    "skull", "legend", "venom", "rage", "phantom", "cyber", "byte", "drift", "sn4ke", "vortex",
    "myst", "doom", "reaper", "slayer", "crusher", "specter", "freeze", "arcade", "nova", "xeno",
    "blitz", "tornado", "savage", "clash", "brawler", "viper", "talon", "shadowblade", "devil", "rex",
    "outlaw", "serpent", "cyberwolf", "blaze", "neon", "deathstorm", "avenger", "falcon", "stealth", "rageblade",
    "maverick", "drifter", "vengeance", "reaper", "destroyer", "duelist", "spartan", "colossus", "tornado", "wildfire",
    "strikeforce", "phoenix", "steel", "panther", "stormbreaker", "vanguard", "plague", "godmode", "quickdraw", "hyperion",
    "gladiator", "nightmare", "darkwing", "spike", "wraith", "roamer", "vigilante", "blackhawk", "saboteur", "ironclad",
    "thunder", "arctic", "comet", "blackout", "stormchaser", "overdrive", "reckoner", "savant", "blowtorch", "skydragon",
    "zephyr", "radar", "nightwolf", "cyclone", "phantom", "emissary", "hypernova", "barrage", "battleground", "spectrum",
    "frostbite", "ripclaw", "blazing", "ironwolf", "mojo", "recoil", "radiant", "zodiac", "raze", "spectra", "warhead",
    "lightning", "nightshadow", "flameburst", "turbine", "oblivion", "pulse", "shrapnel", "fury", "vortexblade", "barricade",
    
    # Anime / geek
    "goku", "naruto", "itachi", "luffy", "eren", "levi", "gojo", "deku", "zoro", "tanjiro",
    "killua", "sasuke", "rimuru", "kakashi", "jiraya", "madara", "bakugo", "shoto", "neji", "gohan",
    "saitama", "yusuke", "light", "kirito", "akame", "kaguya", "inuyasha", "yuno", "misaki", "raku",
    "homura", "kaori", "todoroki", "ryuko", "mugen", "kyo", "kaneki", "sebastian", "grell", "makunouchi",
    "yoriichi", "rengoku", "zenitsu", "tanjiro", "hinata", "sakura", "kikyo", "saber", "shizune", "laxus",
    "asuna", "ichigo", "ram", "rhea", "holo", "yuuki", "hitsuji", "saiki", "ryuji", "nanatsu", "iori",
    "gintoki", "maka", "zeref", "ichiraku", "saber", "lucy", "kanao", "miku", "minato", "karen", "takashi",
    "ken", "milly", "kanna", "shiro", "hikari", "zero", "saber", "soshite", "neko", "tsukasa", "miyuki",
    "neji", "komatsu", "yuri", "shinra", "yugi", "asuka", "katsura", "yuuto", "subaru", "xenon", "keiji", 
    "musashi", "zoro", "luffy", "chopper", "jotaro", "jojo", "hunter", "laxus", "rin", "katsuo", "satoshi", "shinobi",
    "arisa", "keiko", "susanoo", "sara", "naoya", "mari", "kira", "aizen", "chihiro", "miyu", "kenji", "azuma", 
    "junpei", "saigo", "haku", "mayumi", "okabe", "masashi", "riko", "isami", "maki", "arashi", "chihiro", "kenji"

    #animais
    "leão", "tigre", "urso", "lobo", "gato", "cavalo", "raposa", "coelho", "rato", "pato",
    "iguana", "búfalo", "jacaré", "cobra", "lince", "onça", "sapo", "guará", "puma", "baleia",
    "golfinho", "pinguim", "siriema", "garça", "galo", "pica-pau", "cágado", "tucano", "pavo",
    "marreco", "guaxinim", "gambá", "muçum", "jacaré", "andorinha", "pica-pau", "pavão", "pombo",
    "galo", "corvo", "cuíca", "marreco", "calango", "gavião", "sabiá", "bagre", "bisonte",
    "veado", "codorna", "macaco", "boi", "mula", "cavalo", "paca", "guará", "raposa", "tucano",
    "corvo", "piapara", "tilápia", "tucunaré", "peixe", "sururu", "piranha", "jacaré", "caranguejo",
    "salmão", "tilápia", "tartaruga", "camurça", "baleia", "lula", "corvo", "sucuri", "jacaré",
    "siriema", "mandrião", "camundongo", "beija-flor", "carcará", "falco", "gavião", "aguia",
    "tarzan", "jararaca", "mutum", "marrecos", "biu", "guara", "mamute", "beija-flor", "calango",
    "beija-flor", "guará", "polvo", "siri", "bicho-preguiça", "andorinha", "galo-cipó", "tarzan"
]

# Sufixos permitidos
sufixos = [
    "x", "z", "ão", "it", "os", "to", "ix", "in", "on", "or", "er", "us", "an", "as", "el", 
    "ys", "ox", "es", "ys", "us", "za", "zo", "ka", "ma", "na", "do", "ta", "ne", "ve", "bo", 
    "la", "ca", "me", "be", "za", "fi", "ra", "ta", "zo", "sa", "ja", "pe", "ke", "ri", "tu", 
    "li", "mi", "pa", "ta", "si", "fi", "co", "ro", "ja", "yo", "zo", "lu", "jo", "no"
]

# ==== Gerador de login válido ====
def gerar_usuario():
    while True:
        base = random.choice(nomes_base)
        sufixo = random.choice(sufixos)
        nome_raw = base + sufixo
        nome_clean = ''.join(filter(str.isalnum, nome_raw))
        if not nome_clean or not nome_clean[0].isalpha():
            continue
        nome_clean = nome_clean[:random.randint(4, 8)]
        login = nome_clean + str(random.randint(0, 99))
        if 6 <= len(login) <= 11:
            break

    senha = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(6, 10)))
    email = f"{login.lower()}{random.randint(1,9999)}@gmail.com"
    return login, senha, email

# ==== Envio para o site ====
def registrar_conta(login, senha, email):
    url = "https://auth0407.pcrows.com/plaza/index.php"

    payload = {
        "username": login,
        "nickname": login,
        "password": senha,
        "mail_addr": email,
        "mail_code": "",
        "pid": 0,
        "gid": 0,
        "UUID": "6805c1c4835c7890791434efb189d025e2494bbe92053a0a439a7d",
        "lang": "en",
        "vlang": "zh",
        "action": "regAccbyMailCode"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        res_json = response.json()
        if res_json.get("result") is True:
            return True, "Conta criada com sucesso!"
        else:
            return False, res_json.get("info", "Erro do site.")
    except Exception as e:
        return False, f"Erro de conexao: {str(e)}"

# ==== Interface Tkinter ====
class App:
    def __init__(self, master):
        self.master = master
        master.title("Gerador de Contas | NightCrows")
        master.geometry("600x500")
        master.resizable(False, False)

        self.text_area = scrolledtext.ScrolledText(master, width=70, height=20, font=("Consolas", 10))
        self.text_area.pack(pady=10)
        self.text_area.tag_configure("conta_gerada", font=("Consolas", 10))

        self.btn_frame = tk.Frame(master)
        self.btn_frame.pack(pady=5)

        self.gerar_btn = tk.Button(self.btn_frame, text="Gerar Contas", command=self.gerar_contas, bg="green", fg="white", width=15)
        self.gerar_btn.grid(row=0, column=0, padx=5)

        self.limpar_btn = tk.Button(self.btn_frame, text="Limpar Lista", command=self.limpar_lista, bg="orange", fg="black", width=15)
        self.limpar_btn.grid(row=0, column=1, padx=5)

        self.salvar_btn = tk.Button(self.btn_frame, text="Salvar em .txt", command=self.salvar_txt, bg="blue", fg="white", width=15)
        self.salvar_btn.grid(row=0, column=2, padx=5)

        self.status = tk.Label(master, text="", fg="gray")
        self.status.pack()

        self.lista_contas = []

        self.quantidade_label = tk.Label(master, text="Quantidade de Contas:")
        self.quantidade_label.pack(pady=5)

        self.quantidade_entry = tk.Entry(master, width=10)
        self.quantidade_entry.pack(pady=5)

    def gerar_contas(self):
        try:
            quantidade = int(self.quantidade_entry.get())
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")

            self.status.config(text="⏳ Gerando contas...")
            self.master.update()
            self.lista_contas = []
            self.text_area.delete('1.0', tk.END)

            for i in range(quantidade):
                login, senha, email = gerar_usuario()
                sucesso, msg = registrar_conta(login, senha, email)
                if sucesso:
                    bloco = f"{i+1}\nLOGIN: {login}\nSENHA: {senha}\nEMAIL: {email}\n====================\n"
                    self.text_area.insert(tk.END, bloco, "conta_gerada")
                    self.lista_contas.append((login, senha, email))
                else:
                    erro = f"{i+1}\nERRO: {login}: {msg}\n====================\n"
                    self.text_area.insert(tk.END, erro, "conta_gerada")
                time.sleep(random.uniform(0.3, 0.7))

            self.status.config(text="✅ Contas geradas com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def salvar_txt(self):
        try:
            if not self.lista_contas:
                raise ValueError("Nenhuma conta foi gerada para salvar.")
            with open("contas_geradas.txt", "w") as file:
                for i, (login, senha, email) in enumerate(self.lista_contas, 1):
                    file.write(f"{i}\nLOGIN: {login}\nSENHA: {senha}\nEMAIL: {email}\n====================\n")
            messagebox.showinfo("Sucesso", "Contas salvas com sucesso em 'contas_geradas.txt'.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar as contas: {str(e)}")

    def limpar_lista(self):
        self.lista_contas.clear()
        self.text_area.delete('1.0', tk.END)
        self.status.config(text="Lista de contas limpa.")

# ==== Iniciar a interface ====
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()