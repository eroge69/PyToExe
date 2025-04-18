def calculadora():
    while True:
        print("\n=== CALCULADORA ===")
        print("1 - Adição")
        print("2 - Subtração")
        print("3 - Multiplicação")
        print("4 - Divisão")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "0":
            break

        a = float(input("Digite o primeiro número: "))
        b = float(input("Digite o segundo número: "))

        if opcao == "1":
            print("Resultado:", a + b)
        elif opcao == "2":
            print("Resultado:", a - b)
        elif opcao == "3":
            print("Resultado:", a * b)
        elif opcao == "4":
            if b == 0:
                print("Erro: divisão por zero.")
            else:
                print("Resultado:", a / b)
        else:
            print("Opção inválida.")

calculadora()
