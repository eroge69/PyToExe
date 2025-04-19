# Este é um código base em Python

# Imprime uma mensagem na tela
print("Bem vinda")

# Declaração de uma variável
perguntas = [
    ("O Patrik e o cara mais forte do mundo", "sim/nao"),
    ("O Patrik e o cara mais foda do mundo", "sim/nao"),
    ("Voce namora com patrik?", "sim/nao") # Adicionei um exemplo de resposta sim/nao
]

for pergunta, tipo_de_resposta in perguntas:
    print(pergunta)
    resposta = input("Resposta: ")

    if tipo_de_resposta == "forte":
        print(f"O Patrik e o cara mais forte do mundo: {resposta}")
    elif tipo_de_resposta == "sim/nao":
        try:
            idade = int(resposta)
            print(f"Você tem {idade} anos.")
        except ValueError:
            print("O Patrik e o cara mais foda do mundo")
    elif tipo_de_resposta == "sim/nao":
        if resposta.lower() in ("sim", "s"):
            print("O Patrik de fodão")
        elif resposta.lower() in ("não", "n"):
            print("O patrik continua foda")
        else:
            print("Por favor, responda com sim ou não.")

    print("-" * 20) # Separador para cada 

