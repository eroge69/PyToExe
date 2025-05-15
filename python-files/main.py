amorDaMinhaVida = "Princesinha"
individo = "Halley :D"

print(f"Eieiei {amorDaMinhaVida}, você gosta deste indivíduo: {individo}")

gostar = str(input("Responda: "))

print("Únicas respostas: Sim ou Não.")
if gostar >= "Sim":
    print("Hmm, interessante!")
else:
    print("Poh, tenta denovo, pensa mais um pouquinho :)")


notas = [
    "0",
    "50",
    "100"
]

print("Dê uma nota para ele, pois ele irá ver! :D")
print(f"Você tem a seguinte tabela de notas: {notas}")
escolha = int(input("Dê a nota: "))

if escolha >= 100:
    print("CARAMBA, SE AMA ELE MESMO VIU!")
elif escolha >= 50:
    print("Carambolas, somente metade? porque não mais um pouquinho?")
elif escolha <= 0:
    print("Nossa, você odeia ele? 😥")