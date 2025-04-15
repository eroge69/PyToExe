def e_primo(num):
    if num <= 1:
      return False
    for i in range(2,int(num**0.5) + 1 ):
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

#solicitar ao usuario o numero do primo que deseja encontrar
n = int(input("Digite a posição do número do primo que vc deseja encontrar:  "))
if n <= 0:
  print("por favor insira um numero maior que zero. ")
else:
  numero_primo = acha_num_primo(n)
  print(f"o {n}° numero primo é: {numero_primo}")  