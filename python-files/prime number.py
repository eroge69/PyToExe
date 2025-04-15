def e_primo(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def acha_num_primo(n):
    count = 0
    num = 2
    while True:
        if e_primo(num):
            count += 1
            if count == n:
                return num
        num += 1

while True:
    try:
        n_str = input("Digite a posição do número primo que você deseja encontrar (ou pressione Enter para sair): ")
        if n_str == "":
            break
        n = int(n_str)
        if n <= 0:
            print("Por favor, insira um número maior que zero.")
        else:
            numero_primo = acha_num_primo(n)
            print(f"O {n}° número primo é: {numero_primo}")
    except ValueError:
        print("Entrada inválida. Por favor, digite um número inteiro ou pressione Enter.")