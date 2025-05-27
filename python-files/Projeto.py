# Projeto: Alberson - P.O.O.I
# Verificação de CPF 1.0
# Autoras: Ana Clara dos Santos Moreira, Isabela Rangel, Isabelli Arantes Galvão - 2J

import time
print(44 * "-")
print(f"{'Verificação de CPF':^44}")
print(44 * "-")

# Lista de dicionários que guardará os CPFs e suas validações
lista_cpfs = []

while True:
    cpf = input("Digite o CPF (ou pressione Enter para sair): ").strip()

    if cpf == "":
        print("Saindo do programa...")
        time.sleep(1)
        print("Obrigado por usar o verificador de CPF!")
        print(44 * "-")
        break     

    # Verifica se é negativo (sem usar startswith)
    if len(cpf) > 0 and cpf[0] == "-":
        print("CPF inválido. Não pode ser negativo.")
        continue

    # Verifica se há letras ou símbolos (permitimos apenas dígitos, pontos e traços)
    invalido = False
    for c in cpf:
        if not c.isdigit() and c not in ['.', '-', ' ']:
            invalido = True
            break

    if invalido:
        print("CPF inválido. Não pode conter letras ou símbolos.")
        continue

    # Remove caracteres não numéricos
    cpf_limpo = ""
    for c in cpf:
        if c.isdigit():
            cpf_limpo += c

    # Valida entrada
    if len(cpf_limpo) != 11:
        print("CPF inválido. Deve conter exatamente 11 dígitos numéricos.")
        continue

    # Verifica se todos os dígitos são iguais
    todos_iguais = True
    for i in range(1, len(cpf_limpo)):
        if cpf_limpo[i] != cpf_limpo[0]:
            todos_iguais = False
            break
    if todos_iguais:
        print("CPF inválido. Todos os dígitos são iguais.")
        continue

    # Transforma em lista de inteiros
    digitos = []
    for c in cpf_limpo:
        digitos.append(int(c))

    # Verifica se CPF já foi testado
    cpf_ja_testado = False
    for item in lista_cpfs:
        if item['CPF'] == digitos:
            cpf_ja_testado = True
            break

    if cpf_ja_testado:
        print("Este CPF já foi testado anteriormente.")
        continue

    # Cálculo do 1º dígito verificador
    soma1 = 0
    multiplicador = 10
    for i in range(9):
        soma1 += digitos[i] * multiplicador
        multiplicador -= 1

    resto1 = soma1 % 11
    if resto1 < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto1

    # Cálculo do 2º dígito verificador
    soma2 = 0
    multiplicador = 11
    for i in range(9):
        soma2 += digitos[i] * multiplicador
        multiplicador -= 1
    soma2 += digito1 * 2

    resto2 = soma2 % 11
    if resto2 < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto2

    # Verificação final
    if digito1 == digitos[9] and digito2 == digitos[10]:
        validacao = "VÁLIDO"
    else:
        validacao = "INVÁLIDO"

    # Adiciona dicionário na lista
    lista_cpfs.append({
        "CPF": digitos,
        "VALIDACAO": validacao
    })

    # Pergunta ao usuário se deseja continuar
    while True:
        resp = input("Deseja testar outro CPF? (s/n): ").strip().lower()
        if resp == 's':
            break  # continua no laço principal
        elif resp == 'n':
            time.sleep(1)
            # Mostra os resultados antes de sair
            print("\nResultado dos testes:")
            qtd_validos = 0
            qtd_invalidos = 0

            for item in lista_cpfs:
                cpf_str = ''
                for d in item['CPF']:
                    cpf_str += str(d)
                print(f"CPF: {cpf_str} - {item['VALIDACAO']}")
                if item['VALIDACAO'] == 'VÁLIDO':
                    qtd_validos += 1
                else:
                    qtd_invalidos += 1

            total = len(lista_cpfs)
            if total > 0:
                print(f"\nTotal de CPFs testados: {total}")
                print(f"CPFs VÁLIDOS: {qtd_validos}")
                print(f"CPFs INVÁLIDOS: {qtd_invalidos}")
                print(f"Porcentagem de CPFs válidos: {(qtd_validos / total) * 100:.2f}%")
                print(f"Porcentagem de CPFs inválidos: {(qtd_invalidos / total) * 100:.2f}%\n")
                print("Obrigada por usar o verificador de CPF! :D")
            else:
                print("Nenhum CPF foi testado.")
            exit()
        else:
            print("Opção inválida. Digite 's' para sim ou 'n' para não.")
