import os
import csv

def criar_tabela_imc():
    with open("tabela_imc.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id_registro", "Faixa_IMC", "Classificacao", "Atividades", "Alimentacao"])
        writer.writerow([1, "Abaixo de 18,5 kg/m²", "Abaixo do peso",
                         "Aumentar a ingestão calórica, atividades de fortalecimento muscular, acompanhamento nutricional.",
                         "Priorizar alimentos ricos em proteínas, carboidratos complexos e gorduras saudáveis."])
        writer.writerow([2, "18,5 - 24,9 kg/m²", "Peso normal",
                         "Manter uma dieta equilibrada e praticar atividades físicas regulares.",
                         "Variedade de alimentos, priorizando frutas, legumes, grãos integrais, carnes magras e laticínios desnatados."])
        writer.writerow([3, "25 - 29,9 kg/m²", "Sobrepeso",
                         "Aumentar a prática de atividades físicas aeróbicas e de força, reduzir o consumo de alimentos processados e bebidas açucaradas, buscar orientação nutricional.",
                         "Priorizar alimentos ricos em fibras, reduzir o consumo de alimentos ultraprocessados e aumentar o consumo de frutas, legumes e verduras."])
        writer.writerow([4, "30 kg/m² ou mais", "Obesidade",
                         "Buscar acompanhamento médico e nutricional, praticar atividades físicas regulares, adotar hábitos alimentares saudáveis de forma gradual.",
                         "Reduzir o consumo de alimentos ricos em gordura saturada e açúcar, aumentar o consumo de frutas, legumes, grãos integrais e água."])

def criar_instrucoes():
    texto = """5 hábitos saudáveis para abaixar o IMC de obesidade
Abaixar o IMC de obesidade requer uma abordagem holística, que envolve mudanças no 
estilo de vida, incluindo escolhas alimentares saudáveis e a prática de exercícios físicos 
regulares.
1. Alimentação balanceada: dê preferência a uma dieta equilibrada, incluindo em seu 
cardápio vegetais, frutas, grãos integrais, proteínas magras e gorduras “boas” e 
evitando alimentos processados, ricos em açúcares e gorduras saturadas.
2. Controle das porções: com a orientação de um nutricionista, diminua as porções para 
controlar a ingestão calórica e promover a perda de peso, com refeições menores - 
porém mais frequentes - ao longo do dia.
3. Atividade física regular: incorpore exercícios físicos moderados na sua rotina para 
aumentar o déficit calórico, como musculação, corrida, caminhada, natação, entre 
outros.
4. Hidratação adequada: mantenha-se hidratado durante o dia, pois isso pode ajudar a 
controlar o apetite e a manter metabolismo funcionando adequadamente.
5. Sono adequado: tente dormir de 7 a 8 horas por noite, pois repousar pouco pode 
desajustar os hormônios responsáveis por regular o apetite e o metabolismo."""
    with open("instrucoes.txt", mode="w", encoding="utf-8") as file:
        file.write(texto)

def criar_arquivo_usuarios():
    if not os.path.exists("usuarios.csv"):
        with open("usuarios.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Nome", "Peso", "Altura", "IMC", "id_registro"])

def carregar_tabela_imc():
    tabela = {}
    with open("tabela_imc.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            tabela[int(row["id_registro"])] = row
    return tabela

def obter_faixa_imc(imc):
    if imc < 18.5:
        return 1
    elif 18.5 <= imc <= 24.9:
        return 2
    elif 25 <= imc <= 29.9:
        return 3
    else:
        return 4

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    criar_tabela_imc()
    criar_instrucoes()
    criar_arquivo_usuarios()
    tabela = carregar_tabela_imc()

    while True:
        nome = input("Digite seu nome: ").strip()
        try:
            altura = float(input("Digite sua altura (em metros): "))
            peso = float(input("Digite seu peso (em kg): "))
            if altura <= 0 or peso <= 0:
                print("Dados inválidos.")
                op = input("Deseja continuar? (C para continuar / S para sair): ").upper()
                if op == 'S':
                    break
                else:
                    continue
        except ValueError:
            print("Entrada inválida.")
            continue

        imc = round(peso / (altura ** 2), 2)
        id_registro = obter_faixa_imc(imc)

        with open("usuarios.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([nome, peso, altura, imc, id_registro])

        limpar_tela()
        print(f"✓ Nome: {nome}")
        print(f"✓ Peso: {peso} kg  Altura: {altura} m  IMC: {imc}")
        info = tabela[id_registro]
        print(f"FaixadeIMC: {info['Faixa_IMC']}")
        print(f"Classificação: {info['Classificacao']}")
        print(f"Sugestões de Atividades Físicas: {info['Atividades']}")
        print(f"Sugestões Alimentares: {info['Alimentacao']}")

        print("Instruções:")
        with open("instrucoes.txt", encoding="utf-8") as file:
            print(file.read())

        print()
        continuar = input("Digite C para continuar ou qualquer outra tecla para sair: ").upper()
        if continuar != 'C':
            break

if __name__ == "__main__":
    main()
