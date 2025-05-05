import pygame
import random
import time
import sys

pygame.init()

LARGURA, ALTURA = 600, 500
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Memória Simples")

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (50, 50, 200)
VERDE = (50, 200, 50)
VERMELHO = (200, 50, 50)
CINZA = (180, 180, 180)

LINHAS, COLUNAS = 4, 4
TAMANHO_CARTA = 80
ESPACO = 10
MARGEM_SUPERIOR = 80

fonte = pygame.font.SysFont(None, 48)
fonte_pequena = pygame.font.SysFont(None, 32)
fonte_instrucao = pygame.font.SysFont(None, 28)

def desenhar_texto(texto, fonte, cor, centro):
    img = fonte.render(texto, True, cor)
    rect = img.get_rect(center=centro)
    TELA.blit(img, rect)

def menu_inicial():
    while True:
        TELA.fill(BRANCO)
        desenhar_texto("Jogo da Memória", fonte, AZUL, (LARGURA//2, 120))
        pygame.draw.rect(TELA, AZUL, (200, 200, 200, 60))
        pygame.draw.rect(TELA, VERMELHO, (200, 280, 200, 60))
        desenhar_texto("Jogar", fonte, BRANCO, (300, 230))
        desenhar_texto("Sair", fonte, BRANCO, (300, 310))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 200 <= mx <= 400 and 200 <= my <= 260:
                    return True
                elif 200 <= mx <= 400 and 280 <= my <= 340:
                    pygame.quit()
                    sys.exit()

def tela_instrucoes():
    instrucoes = [
        "Instruções:",
        "",
        "- O objetivo é encontrar todos os pares de cartas iguais.",
        "- Clique em duas cartas para revelá-las.",
        "- Se forem iguais, permanecem viradas.",
        "- Se forem diferentes, elas serão ocultadas novamente.",
        "- Você tem 1 minuto para completar o jogo.",
        ">> Clique em 'Começar' para iniciar! <<"
    ]
    while True:
        TELA.fill(BRANCO)
        desenhar_texto("Como Jogar", fonte, AZUL, (LARGURA//2, 70))
        y = 120
        for linha in instrucoes:
            desenhar_texto(linha, fonte_instrucao, PRETO, (LARGURA//2, y))
            y += 35
        pygame.draw.rect(TELA, VERDE, (200, 400, 200, 50))
        desenhar_texto("Começar", fonte_pequena, BRANCO, (300, 425))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 200 <= mx <= 400 and 400 <= my <= 450:
                    return

def gerar_tabuleiro():
    cartas = list(range(1, (LINHAS*COLUNAS)//2 + 1)) * 2
    random.shuffle(cartas)
    tabuleiro = [cartas[i*COLUNAS:(i+1)*COLUNAS] for i in range(LINHAS)]
    reveladas = [[False]*COLUNAS for _ in range(LINHAS)]
    return tabuleiro, reveladas

def desenhar_tabuleiro(tabuleiro, reveladas, tempo_restante):
    TELA.fill(BRANCO)
    for i in range(LINHAS):
        for j in range(COLUNAS):
            x = j * (TAMANHO_CARTA + ESPACO) + ESPACO
            y = i * (TAMANHO_CARTA + ESPACO) + MARGEM_SUPERIOR
            if reveladas[i][j]:
                pygame.draw.rect(TELA, VERDE, (x, y, TAMANHO_CARTA, TAMANHO_CARTA))
                texto = fonte.render(str(tabuleiro[i][j]), True, PRETO)
                TELA.blit(texto, (x + 25, y + 15))
            else:
                pygame.draw.rect(TELA, AZUL, (x, y, TAMANHO_CARTA, TAMANHO_CARTA))
    # Desenha o timer
    desenhar_texto(f"Tempo: {tempo_restante}s", fonte_pequena, PRETO, (LARGURA//2, 40))
    pygame.display.flip()

def posicao_cartao(mx, my):
    for i in range(LINHAS):
        for j in range(COLUNAS):
            x = j * (TAMANHO_CARTA + ESPACO) + ESPACO
            y = i * (TAMANHO_CARTA + ESPACO) + MARGEM_SUPERIOR
            if x <= mx <= x + TAMANHO_CARTA and y <= my <= y + TAMANHO_CARTA:
                return i, j
    return None, None

def mostrar_tela_final(venceu, tempo_gasto):
    while True:
        TELA.fill(BRANCO)
        if venceu:
            desenhar_texto("Parabéns! Você venceu!", fonte, VERDE, (LARGURA//2, 160))
            desenhar_texto(f"Tempo gasto: {tempo_gasto:.1f} segundos", fonte_pequena, PRETO, (LARGURA//2, 220))
        else:
            desenhar_texto("Tempo esgotado!", fonte, VERMELHO, (LARGURA//2, 160))
            desenhar_texto("Tente novamente!", fonte_pequena, PRETO, (LARGURA//2, 220))
        pygame.draw.rect(TELA, AZUL, (200, 300, 200, 60))
        desenhar_texto("Menu", fonte, BRANCO, (300, 330))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 200 <= mx <= 400 and 300 <= my <= 360:
                    return

def jogo():
    tabuleiro, reveladas = gerar_tabuleiro()
    primeira = None
    segunda = None
    aguardando = False
    tempo_espera = 0
    total_reveladas = 0
    tempo_limite = 60  # segundos
    tempo_inicio = time.time()
    tempo_gasto = 0

    rodando = True
    venceu = False

    while rodando:
        tempo_atual = time.time()
        tempo_gasto = tempo_atual - tempo_inicio
        tempo_restante = max(0, int(tempo_limite - tempo_gasto))

        desenhar_tabuleiro(tabuleiro, reveladas, tempo_restante)

        if tempo_restante == 0:
            break

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN and not aguardando:
                mx, my = pygame.mouse.get_pos()
                i, j = posicao_cartao(mx, my)
                if i is not None and not reveladas[i][j]:
                    if primeira is None:
                        primeira = (i, j)
                        reveladas[i][j] = True
                        total_reveladas += 1
                    elif segunda is None and (i, j) != primeira:
                        segunda = (i, j)
                        reveladas[i][j] = True
                        total_reveladas += 1
                        aguardando = True
                        tempo_espera = time.time()

        if aguardando and time.time() - tempo_espera > 1:
            i1, j1 = primeira
            i2, j2 = segunda
            if tabuleiro[i1][j1] != tabuleiro[i2][j2]:
                reveladas[i1][j1] = False
                reveladas[i2][j2] = False
                total_reveladas -= 2
            primeira = None
            segunda = None
            aguardando = False

        # Verifica se o jogador venceu
        if total_reveladas == LINHAS * COLUNAS:
            venceu = True
            break

    mostrar_tela_final(venceu, tempo_gasto)

def main():
    while True:
        menu_inicial()
        tela_instrucoes()
        jogo()

if __name__ == "__main__":
    main()
