import pygame
import sys
import random
import os

# Inicialização
pygame.init()
pygame.mixer.init()

# Configurações
LARGURA, ALTURA = 1000, 650
GRID_TAMANHO = 10
TAMANHO_CELULA = 45
ESPACO_TABULEIROS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL_CLARO = (173, 216, 230, 150)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
CINZA = (100, 100, 100)
AMARELO = (255, 255, 0)

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Batalha Naval")

fonte_historia = pygame.font.SysFont("timesnewroman", 28)
fonte_menu = pygame.font.SysFont("arial", 36)
fonte_titulo = pygame.font.SysFont("arial", 90, bold=True)
fonte_mensagem = pygame.font.Font(None, 36)
fonte_info = pygame.font.Font(None, 32)

def mostrar_mensagem(texto, cor=BRANCO, tempo=0):
    mensagem = fonte_mensagem.render(texto, True, cor)
    rect = mensagem.get_rect(center=(LARGURA//2, 40))
    pygame.draw.rect(TELA, PRETO, rect.inflate(20, 10))
    TELA.blit(mensagem, rect)
    pygame.display.flip()
    if tempo > 0:
        pygame.time.delay(tempo)

def carregar_imagem(nome, tamanho=None, alpha=True):
    try:
        caminho = os.path.join("assets", nome)
        img = pygame.image.load(caminho)
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        if tamanho:
            img = pygame.transform.scale(img, tamanho)
        return img
    except Exception:
        surf = pygame.Surface((tamanho if tamanho else (50, 50)), pygame.SRCALPHA if alpha else 0)
        surf.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200), 150))
        return surf

img_titulo = carregar_imagem("titulo.png", (400, 180))
img_fundo_menu = carregar_imagem("fundo_menu.png", (LARGURA, ALTURA), False)
img_fase1 = carregar_imagem("fundo_fase1.png", (LARGURA, ALTURA), False)
img_fase2 = carregar_imagem("fundo_fase2.png", (LARGURA, ALTURA), False)
img_fase3 = carregar_imagem("fundo_fase3.png", (LARGURA, ALTURA), False)

img_navios = [
    carregar_imagem("navio1.png", (TAMANHO_CELULA*3, TAMANHO_CELULA)),
    carregar_imagem("navio2.png", (TAMANHO_CELULA*2, TAMANHO_CELULA)),
    carregar_imagem("navio3.png", (TAMANHO_CELULA, TAMANHO_CELULA))
]

img_explosao = carregar_imagem("explosao.png", (TAMANHO_CELULA, TAMANHO_CELULA))
img_splash = carregar_imagem("splash.png", (TAMANHO_CELULA, TAMANHO_CELULA))

try:
    pygame.mixer.music.load(os.path.join("assets", "marinha.mp3"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    som_explosao = pygame.mixer.Sound(os.path.join("assets", "explosao.mp3")) if os.path.exists(os.path.join("assets", "explosao.mp3")) else None
    som_splash = pygame.mixer.Sound(os.path.join("assets", "splash.mp3"))
    if som_explosao is None:
        som_explosao = som_splash
except Exception:
    class DummySound:
        def play(self): pass
    som_explosao = som_splash = DummySound()

class Navio:
    def __init__(self, tamanho, imagem):
        self.tamanho = tamanho
        self.imagem_original = imagem
        self.horizontal = True
        self.posicionado = False
        self.offset = (0, 0)
        self.arrastando = False
        self.reset_imagem()

    def reset_imagem(self):
        if self.horizontal:
            self.imagem = pygame.transform.scale(
                self.imagem_original,
                (self.tamanho*TAMANHO_CELULA, TAMANHO_CELULA)
            )
        else:
            self.imagem = pygame.transform.scale(
                pygame.transform.rotate(self.imagem_original, 90),
                (TAMANHO_CELULA, self.tamanho*TAMANHO_CELULA)
            )
        self.rect = self.imagem.get_rect()

    def desenhar(self):
        TELA.blit(self.imagem, self.rect)

    def girar(self):
        self.horizontal = not self.horizontal
        self.reset_imagem()

def criar_tabuleiro():
    return [[' ' for _ in range(GRID_TAMANHO)] for _ in range(GRID_TAMANHO)]

def desenhar_tabuleiro(x, y, tabuleiro, revelar=False, debug=False):
    for linha in range(GRID_TAMANHO):
        for coluna in range(GRID_TAMANHO):
            rect = pygame.Rect(x + coluna*TAMANHO_CELULA, y + linha*TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
            celula = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            pygame.draw.rect(celula, AZUL_CLARO, (0, 0, TAMANHO_CELULA, TAMANHO_CELULA))
            pygame.draw.rect(celula, PRETO, (0, 0, TAMANHO_CELULA, TAMANHO_CELULA), 1)
            TELA.blit(celula, rect.topleft)
            if tabuleiro[linha][coluna] == 'X':
                TELA.blit(img_explosao, rect)
            elif tabuleiro[linha][coluna] == 'O':
                TELA.blit(img_splash, rect)
            elif (debug or revelar) and tabuleiro[linha][coluna] == 'N':
                pygame.draw.rect(TELA, (50, 200, 50, 150), rect)

def posicionar_navios_ia(tabuleiro, fase):
    if fase == 1:
        tamanhos = [3, 2, 2, 1, 1]
    elif fase == 2:
        tamanhos = [3, 2, 1, 1]
    else:
        tamanhos = [3, 2, 1]
    for tam in tamanhos:
        while True:
            horizontal = random.choice([True, False])
            if horizontal:
                lin = random.randint(0, GRID_TAMANHO-1)
                col = random.randint(0, GRID_TAMANHO-tam)
            else:
                lin = random.randint(0, GRID_TAMANHO-tam)
                col = random.randint(0, GRID_TAMANHO-1)
            valido = True
            for i in range(tam):
                if horizontal:
                    linha, coluna = lin, col+i
                else:
                    linha, coluna = lin+i, col
                if tabuleiro[linha][coluna] != ' ':
                    valido = False
                    break
            if valido:
                for i in range(tam):
                    if horizontal:
                        tabuleiro[lin][col+i] = 'N'
                    else:
                        tabuleiro[lin+i][col] = 'N'
                break

def contar_celulas_com_navios(tabuleiro):
    return sum(linha.count('N') for linha in tabuleiro)

def mostrar_texto_animado(linhas, cor=BRANCO, tempo=30, fonte=None):
    if fonte is None:
        fonte = fonte_historia
    espacamento = 40
    altura_total = len(linhas) * espacamento
    y_inicial = ALTURA
    clock = pygame.time.Clock()
    mostrando = True
    while mostrando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                mostrando = False
        TELA.fill(PRETO)
        y_inicial -= 1
        for i, linha in enumerate(linhas):
            texto = fonte.render(linha, True, cor)
            x = (LARGURA - texto.get_width()) // 2
            y = y_inicial + i * espacamento
            if -50 < y < ALTURA + 50:
                TELA.blit(texto, (x, y))
        if y_inicial + altura_total < 0:
            mostrando = False
        pygame.display.flip()
        clock.tick(tempo)

def menu():
    while True:
        TELA.blit(img_fundo_menu, (0, 0))
        if img_titulo:
            titulo_rect = img_titulo.get_rect(center=(LARGURA//2, ALTURA//4))
            TELA.blit(img_titulo, titulo_rect)
        else:
            texto_titulo = fonte_titulo.render("BATALHA NAVAL", True, AMARELO)
            TELA.blit(texto_titulo, (LARGURA//2 - texto_titulo.get_width()//2, ALTURA//4 - texto_titulo.get_height()//2))
        botao = pygame.Rect(LARGURA//2 - 100, ALTURA//2, 200, 50)
        pygame.draw.rect(TELA, (70, 70, 70), botao, border_radius=8)
        pygame.draw.rect(TELA, AMARELO, botao, 3, border_radius=8)
        texto = fonte_mensagem.render("Jogar", True, AMARELO)
        TELA.blit(texto, (botao.centerx - texto.get_width()//2, botao.centery - texto.get_height()//2))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao.collidepoint(evento.pos):
                    return True

def mostrar_historia():
    historia = [
        "Em 1942, durante a Segunda Guerra Mundial,",
        "a costa portuguesa foi alvo de ameaças inimigas.",
        "",
        "A Marinha Portuguesa organizou uma frota para proteger",
        "os portos estratégicos, incluindo Viana do Castelo.",
        "",
        "Agora, cabe a ti comandar uma dessas frotas,",
        "colocar os navios com sabedoria e derrotar o inimigo.",
        "",
        "Boa sorte, comandante. Talant de Bien Faire!"
    ]
    mostrar_texto_animado(historia, BRANCO, 60, fonte_historia)

def tela_transicao_fase(fase, fundo):
    escurecedor = pygame.Surface((LARGURA, ALTURA))
    escurecedor.fill(PRETO)
    escurecedor.set_alpha(180)
    TELA.blit(fundo, (0, 0))
    TELA.blit(escurecedor, (0, 0))
    if fase == 2:
        dia_texto = "Dia 3"
    elif fase == 3:
        dia_texto = "Dia 7"
    else:
        dia_texto = ""
    if dia_texto:
        fonte_grande = pygame.font.SysFont("Arial", 80, bold=True)
        texto_grande = fonte_grande.render(dia_texto, True, BRANCO)
        TELA.blit(texto_grande, (LARGURA//2 - texto_grande.get_width()//2, ALTURA//2 - 100))
    texto = fonte_mensagem.render(f"Fase {fase-1} concluída! Preparar próxima...", True, BRANCO)
    TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 + 50))
    pygame.display.flip()
    pygame.time.delay(3500)

def mostrar_fim_jogo():
    historia_vitoria = [
        "Após três dias de intensos combates,",
        "a frota portuguesa conseguiu repelir",
        "as forças inimigas e proteger os portos.",
        "",
        "Portugal manteve a sua neutralidade",
        "e honrou a sua tradição marítima!",
        "",
        "Cumpriste a tua missão com honra, comandante!"
        "A Pátria honrae que a Pátria vos contempla!"
    ]
    mostrar_texto_animado(historia_vitoria, VERDE, 60, fonte_historia)

def tela_fim_de_jogo(venceu, fundo_atual):
    escurecedor = pygame.Surface((LARGURA, ALTURA))
    escurecedor.fill(PRETO)
    escurecedor.set_alpha(180)
    rodando = True
    clock = pygame.time.Clock()
    while rodando:
        TELA.blit(fundo_atual, (0, 0))
        TELA.blit(escurecedor, (0, 0))
        msg = "Vitória nesta fase!" if venceu else "Foste derrotado!"
        cor = VERDE if venceu else VERMELHO
        texto = fonte_mensagem.render(msg, True, cor)
        TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - 100))
        botao_menu = pygame.Rect(LARGURA//2 - 170, ALTURA//2, 150, 60)
        pygame.draw.rect(TELA, CINZA, botao_menu, border_radius=8)
        pygame.draw.rect(TELA, BRANCO, botao_menu, 2, border_radius=8)
        texto_menu = fonte_mensagem.render("Menu", True, BRANCO)
        TELA.blit(texto_menu, (botao_menu.centerx - texto_menu.get_width()//2, botao_menu.centery - texto_menu.get_height()//2))
        botao_recomecar = pygame.Rect(LARGURA//2 + 20, ALTURA//2, 170, 60)
        pygame.draw.rect(TELA, CINZA, botao_recomecar, border_radius=8)
        pygame.draw.rect(TELA, BRANCO, botao_recomecar, 2, border_radius=8)
        texto_recomecar = fonte_mensagem.render("Recomeçar", True, BRANCO)
        TELA.blit(texto_recomecar, (botao_recomecar.centerx - texto_recomecar.get_width()//2, botao_recomecar.centery - texto_recomecar.get_height()//2))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_menu.collidepoint(evento.pos):
                    return "menu"
                if botao_recomecar.collidepoint(evento.pos):
                    return "recomecar"
        clock.tick(60)

def ataque_ia(tab_jogador, fase, memoria_ia):
    GRID = GRID_TAMANHO
    if fase == 1:
        while True:
            lin, col = random.randint(0, GRID-1), random.randint(0, GRID-1)
            if tab_jogador[lin][col] not in ('X', 'O'):
                return lin, col
    else:
        alvos = []
        for l in range(GRID):
            for c in range(GRID):
                if tab_jogador[l][c] == 'X':
                    for dl, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nl, nc = l+dl, c+dc
                        if 0<=nl<GRID and 0<=nc<GRID and tab_jogador[nl][nc] not in ('X','O'):
                            alvos.append((nl,nc))
        if alvos:
            return random.choice(alvos)
        else:
            return ataque_ia(tab_jogador, 1, memoria_ia)

def jogo(fase, fundo, debug=False):
    tab_jogador = criar_tabuleiro()
    tab_ia = criar_tabuleiro()
    revelado_ia = criar_tabuleiro()
    navios = [
        Navio(3, img_navios[0]),
        Navio(2, img_navios[1]),
        Navio(2, img_navios[1]),
        Navio(1, img_navios[2]),
        Navio(1, img_navios[2])
    ]
    area_total = GRID_TAMANHO*TAMANHO_CELULA*2 + ESPACO_TABULEIROS
    x_jogador = (LARGURA - area_total) // 2
    y_tab = (ALTURA - GRID_TAMANHO*TAMANHO_CELULA) // 2
    x_ia = x_jogador + GRID_TAMANHO*TAMANHO_CELULA + ESPACO_TABULEIROS
    espaco_entre_navios = 10
    area_navios = TAMANHO_CELULA * 3 * 5 + espaco_entre_navios * 4
    inicio_x = x_jogador + (GRID_TAMANHO*TAMANHO_CELULA - area_navios) // 2
    inicio_x = max(inicio_x, 0)
    inicio_x = min(inicio_x, LARGURA - area_navios)
    for i, navio in enumerate(navios):
        navio.rect.topleft = (inicio_x + i*(TAMANHO_CELULA*3 + espaco_entre_navios), y_tab + GRID_TAMANHO*TAMANHO_CELULA + 30)
    posicionar_navios_ia(tab_ia, fase)
    total_celulas_navios_ia = contar_celulas_com_navios(tab_ia)
    selecionado = None
    posicionando = True
    rodando = True
    clock = pygame.time.Clock()
    mensagem_tempo = 0
    mensagem_texto = ""
    turno_jogador = True
    memoria_ia = {}
    total_acertos_ia = 0
    while rodando:
        TELA.blit(fundo, (0, 0))
        desenhar_tabuleiro(x_jogador, y_tab, tab_jogador)
        # --- CORRIGIDO AQUI ---
        if debug:
            desenhar_tabuleiro(x_ia, y_tab, tab_ia, True, True)
        else:
            desenhar_tabuleiro(x_ia, y_tab, revelado_ia)
        # --- FIM DA CORREÇÃO ---
        if debug:
            fonte_debug = pygame.font.Font(None, 24)
            texto_debug = fonte_debug.render("MODO DEBUG: Navios da IA visíveis", True, VERMELHO)
            TELA.blit(texto_debug, (10, 10))
        for navio in navios:
            navio.desenhar()
        if posicionando:
            texto = fonte_mensagem.render("Arrasta os navios para o teu tabuleiro (à esquerda).", True, AMARELO)
            rect = texto.get_rect(center=(LARGURA//2, 40))
            pygame.draw.rect(TELA, PRETO, rect.inflate(20, 10))
            TELA.blit(texto, rect)
        elif pygame.time.get_ticks() < mensagem_tempo:
            mostrar_mensagem(mensagem_texto, AMARELO, 0)
        elif not posicionando:
            if turno_jogador:
                mostrar_mensagem("A tua vez - clica no tabuleiro inimigo.", VERDE)
            else:
                mostrar_mensagem("Vez da IA a pensar...", VERMELHO)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F3:
                    debug = not debug
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if posicionando:
                    for navio in navios:
                        if navio.rect.collidepoint(evento.pos) and not navio.posicionado:
                            selecionado = navio
                            navio.arrastando = True
                            navio.offset = (evento.pos[0] - navio.rect.x, evento.pos[1] - navio.rect.y)
                            break
                elif turno_jogador:
                    mx, my = evento.pos
                    if x_ia <= mx < x_ia + GRID_TAMANHO*TAMANHO_CELULA and y_tab <= my < y_tab + GRID_TAMANHO*TAMANHO_CELULA:
                        gx = (mx - x_ia) // TAMANHO_CELULA
                        gy = (my - y_tab) // TAMANHO_CELULA
                        if revelado_ia[gy][gx] == ' ':
                            if tab_ia[gy][gx] == 'N':
                                revelado_ia[gy][gx] = 'X'
                                tab_ia[gy][gx] = 'X'
                                som_explosao.play()
                                total_acertos_ia += 1
                            else:
                                revelado_ia[gy][gx] = 'O'
                                som_splash.play()
                            turno_jogador = False
                            mensagem_texto = "IA a jogar..."
                            mensagem_tempo = pygame.time.get_ticks() + 1500
            elif evento.type == pygame.MOUSEBUTTONUP and selecionado:
                selecionado.arrastando = False
                mx, my = evento.pos
                gx = (mx - x_jogador) // TAMANHO_CELULA
                gy = (my - y_tab) // TAMANHO_CELULA
                if 0 <= gx < GRID_TAMANHO and 0 <= gy < GRID_TAMANHO:
                    valido = True
                    for i in range(selecionado.tamanho):
                        lin = gy + (i if not selecionado.horizontal else 0)
                        col = gx + (i if selecionado.horizontal else 0)
                        if lin >= GRID_TAMANHO or col >= GRID_TAMANHO or tab_jogador[lin][col] != ' ':
                            valido = False
                            break
                    if valido:
                        for i in range(selecionado.tamanho):
                            lin = gy + (i if not selecionado.horizontal else 0)
                            col = gx + (i if selecionado.horizontal else 0)
                            tab_jogador[lin][col] = 'N'
                        selecionado.posicionado = True
                        selecionado.rect.topleft = (x_jogador + gx*TAMANHO_CELULA, y_tab + gy*TAMANHO_CELULA)
                        if all(navio.posicionado for navio in navios):
                            mensagem_texto = "Começa o jogo!"
                            mensagem_tempo = pygame.time.get_ticks() + 2000
                            posicionando = False
                selecionado = None
            elif evento.type == pygame.MOUSEMOTION and selecionado and selecionado.arrastando:
                selecionado.rect.x = evento.pos[0] - selecionado.offset[0]
                selecionado.rect.y = evento.pos[1] - selecionado.offset[1]
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_r and selecionado:
                selecionado.girar()
        # Turno da IA
        if not posicionando and not turno_jogador and pygame.time.get_ticks() > mensagem_tempo:
            lin, col = ataque_ia(tab_jogador, fase, memoria_ia)
            if tab_jogador[lin][col] == 'N':
                tab_jogador[lin][col] = 'X'
                som_explosao.play()
            else:
                tab_jogador[lin][col] = 'O'
                som_splash.play()
            turno_jogador = True
        # Verifica vitória/derrota
        if not posicionando:
            if total_acertos_ia >= total_celulas_navios_ia:
                return True
            navios_jogador_restantes = False
            for linha in tab_jogador:
                if 'N' in linha:
                    navios_jogador_restantes = True
                    break
            if not navios_jogador_restantes:
                return False
        pygame.display.flip()
        clock.tick(60)

def main():
    debug = False
    clock = pygame.time.Clock()
    while True:
        if not menu():
            break
        mostrar_historia()
        fase = 1
        fundos = [img_fase1, img_fase2, img_fase3]
        while fase <= 3:
            resultado = jogo(fase, fundos[fase-1], debug)
            if resultado:
                if fase < 3:
                    tela_transicao_fase(fase+1, fundos[fase])
                    fase += 1
                else:
                    mostrar_fim_jogo()
                    break
            else:
                acao = tela_fim_de_jogo(False, fundos[fase-1])
                if acao == "menu":
                    break
                elif acao == "recomecar":
                    continue
                else:
                    break
        if fase > 3:
            mostrar_fim_jogo()

if __name__ == "__main__":
    main()
