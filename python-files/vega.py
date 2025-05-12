
import random

saldo = 50  # Saldo inicial do jogador

print("🎰 Bem-vindo ao VEGA's Casino!")
print("Você começa com $50.")

while saldo > 0:
    print(f"\nSeu saldo atual: ${saldo}")
    
    try:
        aposta = float(input("Quanto deseja apostar? (Digite 0 para sair): "))
        if aposta == 0:
            break
        if aposta > saldo or aposta < 0:
            print("Aposta inválida.")
            continue
    
       


        numero = int(input("Escolha um número de 1 a 5: "))
        if numero < 1 or numero > 5:
            print("Número fora do intervalo.")
            continue

        sorteio = random.randint(1, 5)
        print(f"Número sorteado: {sorteio}")

        if numero == sorteio:
            ganho = aposta * 3
            saldo += ganho
            print(f"🎉 Parabéns! Você ganhou ${ganho}!")
        else:
            saldo -= aposta * 1.5
            print("💔 Que pena, você perdeu.")

    except ValueError:
        print("Por favor, digite apenas números inteiros.")
    
    if saldo > 200:
        print("ACABOU DE ATINGIR O DOBRO DO SEU DINHEIRO INICIAL!!")
    if saldo == 1000:
        print("ACABOU DE ATINGIR $1000")
    

print(f"\nJogo terminado. Seu saldo final: ${saldo}")
print("Obrigado por jogar! 🍀")
