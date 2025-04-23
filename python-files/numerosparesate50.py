#PROGRAMA QUE MOSTRA OS NÚMEROS PARES ENTRE 1 E 50
print('PROGRAMA QUE MOSTRA OS NÚMEROS PARES ENTRE 1 E 50')
for num in range(1,50):
        if num%2==0:
                print(num)

print('\n')

#PROGRAMA QUE CALCULA OS NÚMEROS ENTRE 1 E 500 MÚLTIPLOS DE 3 ÍMPARES
print('PROGRAMA QUE CALCULA OS NÚMEROS ENTRE 1 E 500 MÚLTIPLOS DE 3 ÍMPARES')
for num in range(1,500):
           if num%2!=0 and num%3==0:
                print(num)

#PROGRAMA QUE CALCULA A SOMA DOS NÚMEROS ENTRE 1 E 500 MÚLTIPLOS DE 3 ÍMPARES
print('PROGRAMA QUE CALCULA OS NÚMEROS ENTRE 1 E 30 MÚLTIPLOS DE 3 ÍMPARES')
soma = 0
for num in range(1,30):
           if num%2!=0 and num%3==0:
                print(num)
                soma = soma+num
                print(soma)