import pygame
import sys

# Inizializza Pygame
pygame.init()

# Impostazioni della finestra
larghezza_finestra = 800
altezza_finestra = 600
finestra = pygame.display.set_mode((larghezza_finestra, altezza_finestra))
pygame.display.set_caption("Pong 1v1")

# Colori
NERO = (0, 0, 0)
BIANCO = (255, 255, 255)

# Impostazioni barre
larghezza_barra = 15
altezza_barra = 100
velocita_barra = 10

# Impostazioni palla
raggio_palla = 10
velocita_palla_x = 5
velocita_palla_y = 5

# Font per il punteggio
font = pygame.font.SysFont("Arial", 30)

# Funzione per disegnare la palla
def disegna_palla(x, y):
    pygame.draw.circle(finestra, BIANCO, (x, y), raggio_palla)

# Funzione per disegnare una barra
def disegna_barra(x, y):
    pygame.draw.rect(finestra, BIANCO, (x, y, larghezza_barra, altezza_barra))

# Funzione per disegnare il punteggio
def disegna_punteggio(punteggio_giocatore1, punteggio_giocatore2):
    punteggio_text = font.render(f"{punteggio_giocatore1} - {punteggio_giocatore2}", True, BIANCO)
    finestra.blit(punteggio_text, (larghezza_finestra // 2 - punteggio_text.get_width() // 2, 20))

# Ciclo principale del gioco
def gioco():
    x_palla = larghezza_finestra // 2
    y_palla = altezza_finestra // 2
    velocita_palla_x = 5
    velocita_palla_y = 5

    y_barra_giocatore1 = altezza_finestra // 2 - altezza_barra // 2
    y_barra_giocatore2 = altezza_finestra // 2 - altezza_barra // 2

    punteggio_giocatore1 = 0
    punteggio_giocatore2 = 0

    orario = pygame.time.Clock()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Controllo delle barre
        tasti = pygame.key.get_pressed()
        if tasti[pygame.K_w] and y_barra_giocatore1 > 0:
            y_barra_giocatore1 -= velocita_barra
        if tasti[pygame.K_s] and y_barra_giocatore1 < altezza_finestra - altezza_barra:
            y_barra_giocatore1 += velocita_barra
        if tasti[pygame.K_UP] and y_barra_giocatore2 > 0:
            y_barra_giocatore2 -= velocita_barra
        if tasti[pygame.K_DOWN] and y_barra_giocatore2 < altezza_finestra - altezza_barra:
            y_barra_giocatore2 += velocita_barra

        # Movimento della palla
        x_palla += velocita_palla_x
        y_palla += velocita_palla_y

        # Collisione con il bordo superiore e inferiore
        if y_palla <= 0 or y_palla >= altezza_finestra:
            velocita_palla_y = -velocita_palla_y

        # Collisione con le barre
        if (x_palla <= larghezza_barra and y_barra_giocatore1 < y_palla < y_barra_giocatore1 + altezza_barra) or (x_palla >= larghezza_finestra - larghezza_barra and y_barra_giocatore2 < y_palla < y_barra_giocatore2 + altezza_barra):
            velocita_palla_x = -velocita_palla_x

        # Punti segnati
        if x_palla <= 0:
            punteggio_giocatore2 += 1
            x_palla = larghezza_finestra // 2
            y_palla = altezza_finestra // 2
            velocita_palla_x = -velocita_palla_x

        if x_palla >= larghezza_finestra:
            punteggio_giocatore1 += 1
            x_palla = larghezza_finestra // 2
            y_palla = altezza_finestra // 2
            velocita_palla_x = -velocita_palla_x

        # Riempie lo schermo di nero
        finestra.fill(NERO)

        # Disegna la palla, le barre e il punteggio
        disegna_palla(x_palla, y_palla)
        disegna_barra(30, y_barra_giocatore1)
        disegna_barra(larghezza_finestra - 30 - larghezza_barra, y_barra_giocatore2)
        disegna_punteggio(punteggio_giocatore1, punteggio_giocatore2)

        pygame.display.update()
        orario.tick(60)

# Avvia il gioco
if __name__ == "__main__":
    gioco()
