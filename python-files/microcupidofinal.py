import os
import json

DATA_FILE = "microcupido_dados.txt"

perguntas_etapa1 = [
    "Você gosta de cinema?",
    "Você gosta de esportes?",
    "Prefere praia a montanha?",
    "Você gosta de animais?",
    "Você é uma pessoa extrovertida?",
    "Você gosta de ler livros?",
    "Você gosta de dançar?",
    "Você gosta de videogames?",
    "Você prefere café a chá?",
    "Você gosta de música clássica?"
]

perguntas_etapa2 = [
    "Você costuma tomar decisões com base na razão, mesmo em situações emocionais?",
    "Você prefere planejar com antecedência do que agir por impulso?",
    "Você costuma ser honesto consigo mesmo(a), mesmo quando a verdade é difícil de encarar?",
    "Você lida bem com críticas construtivas?",
    "Você tende a evitar confrontos mesmo quando está certo(a)?",
    "Você considera importante manter a rotina e organização no dia a dia?",
    "Você costuma compartilhar seus sentimentos com facilidade?",
    "Você se sente confortável em ambientes sociais com muitas pessoas?",
    "Você valoriza mais estabilidade do que aventura em um relacionamento?",
    "Você acredita que o amor precisa de tempo para se desenvolver, e não acontece à primeira vista?"
]

# Novas perguntas de perfil político/ideológico/filosófico
perguntas_etapa3 = [
    "Você acredita que o governo deve ser mais centralizado ou descentralizado?",
    "Você considera a liberdade de expressão mais importante do que a manutenção da ordem pública?",
    "Você acredita que as leis devem refletir os valores tradicionais ou evoluir conforme a sociedade?",
    "Você apoia a ideia de que a justiça social deve prevalecer sobre o direito individual?",
    "Você acha que os governos devem intervir mais na economia para garantir igualdade?",
    "Você acredita que a religião deve influenciar as decisões políticas?",
    "Você considera que a democracia é o melhor sistema de governo em qualquer contexto?",
    "Você acredita que a igualdade de oportunidades é mais importante que a igualdade de resultados?",
    "Você defende que os direitos humanos são universais ou devem ser adaptados a cada cultura?",
    "Você acredita que o ambientalismo deve ser priorizado sobre o crescimento econômico?"
]

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return [json.loads(linha) for linha in f.readlines()]

def salvar_dados(dados):
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(dados) + "\n")

def obter_respostas(perguntas, opcoes):
    respostas = []
    for pergunta in perguntas:
        while True:
            resposta = input(pergunta + f" ({'/'.join(opcoes)}): ").strip().lower()
            if resposta in opcoes:
                respostas.append(resposta)
                break
            else:
                print("Resposta inválida.")
    return respostas

def obter_resposta_aberta(pergunta):
    while True:
        resposta = input(pergunta + ": ").strip().lower()
        if resposta:  # Verifica se a resposta não está vazia
            return resposta
        print("Resposta inválida. Por favor, responda com uma palavra.")

def calcular_compatibilidade(resp1, resp2):
    total = len(resp1)
    pontos = 0
    for r1, r2 in zip(resp1, resp2):
        if r1 == r2:
            pontos += 1
        elif 'talvez' in (r1, r2):
            pontos += 0.5
    return int((pontos / total) * 100)

def comparar_resposta_aberta(r1, r2):
    # Compara se as respostas abertas são iguais
    return 1 if r1 == r2 else 0

def main():
    print("Bem-vindo ao Microcupido!")
    nome = input("Digite seu nome: ").strip()
    sexo = input("Digite seu sexo (masculino/feminino): ").strip().lower()

    print("\nResponda às seguintes perguntas com 'sim' ou 'não':")
    respostas1 = obter_respostas(perguntas_etapa1, ["sim", "não"])

    print("\nAgora vamos para a segunda etapa")
    print("Responda com 'sim', 'não' ou 'talvez':")
    respostas2 = obter_respostas(perguntas_etapa2, ["sim", "não", "talvez"])

    print("\nAgora, as 10 perguntas de perfil político/ideológico/filosófico:")
    respostas3 = obter_respostas(perguntas_etapa3, ["sim", "não", "talvez"])

    print("\nResponda com uma palavra: Que tipo de pessoa você se considera?")
    resposta_aberta = obter_resposta_aberta("Qual a palavra que define você?")

    dados_usuario = {
        "nome": nome,
        "sexo": sexo,
        "etapa1": respostas1,
        "etapa2": respostas2,
        "etapa3": respostas3,
        "resposta_aberta": resposta_aberta
    }

    todos_dados = carregar_dados()
    salvar_dados(dados_usuario)

    print("\nCalculando compatibilidades...")

    melhor_match = None
    melhor_porcentagem = -1

    for outro in todos_dados:
        if outro["sexo"] == sexo:
            continue  # compatível apenas com sexo oposto
        comp1 = calcular_compatibilidade(respostas1, outro["etapa1"])
        comp2 = calcular_compatibilidade(respostas2, outro["etapa2"])
        comp3 = calcular_compatibilidade(respostas3, outro["etapa3"])
        comp_aberta = comparar_resposta_aberta(resposta_aberta, outro["resposta_aberta"])
        media = (comp1 + comp2 + comp3 + comp_aberta) // 4

        if media > melhor_porcentagem:
            melhor_porcentagem = media
            melhor_match = outro["nome"]

    if melhor_match:
        print(f"\nVocê é mais compatível com {melhor_match} ({melhor_porcentagem}% de compatibilidade).")
    else:
        print("\nNenhuma compatibilidade encontrada ainda. Aguarde mais pessoas responderem.")

    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
