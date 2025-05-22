def main():
    try:
        # Solicita os valores do usuário
        horas_ponto = float(input("Horas do ponto: "))
        horas_trabalhadas = float(input("Horas trabalhadas: "))

        # Evita divisão por zero
        if horas_ponto == 0:
            print("Erro: Horas do ponto não pode ser zero.")
        else:
            # Calcula a taxa
            taxa = (horas_trabalhadas / horas_ponto) * 100

            # Exibe os valores e resultado
            print("\n--- Resultado ---")
            print(f"Horas do ponto: {horas_ponto}")
            print(f"Horas trabalhadas: {horas_trabalhadas}")
            print(f"Taxa: {taxa:.2f}%")
    
    except ValueError:
        print("Erro: Insira apenas números válidos.")
    
    # Aguarda o usuário pressionar Enter
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
