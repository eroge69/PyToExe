import random

# Listas de coisas aleatórias
cores = ["vermelho", "azul", "verde", "amarelo", "roxo", "rosa", "preto", "branco"]
nomes = ["João", "Maria", "Pedro", "Ana", "Lucas", "Júlia", "Rafa", "Bia"]
emojis = ["😂", "🔥", "💀", "😎", "🤡", "🚀", "🐱", "🍕"]

# Gerador de coisa aleatória
def gerar_coisa_aleatoria():
    numero = random.randint(1, 1000)
    cor = random.choice(cores)
    nome = random.choice(nomes)
    emoji = random.choice(emojis)
    
    print(f"🎲 Número: {numero}")
    print(f"🎨 Cor: {cor}")
    print(f"👤 Nome: {nome}")
    print(f"😜 Emoji: {emoji}")

# Bora rodar!
gerar_coisa_aleatoria()
