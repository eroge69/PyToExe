import pygame
import numpy as np
import sounddevice as sd

# === Nastavení okna ===
WIDTH = 1200
HEIGHT = 700
FPS = 60
NUM_BARS = 96

# === Inicializace Pygame ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spektrální Analyzer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 14)

# === Nastavení mikrofonu ===
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024

# === Funkce pro příjem zvuku ===
audio_data = np.zeros(BUFFER_SIZE)

def audio_callback(indata, frames, time, status):
    global audio_data
    audio_data = np.copy(indata[:, 0])

# === Spuštění streamu mikrofonu ===
stream = sd.InputStream(
    channels=1,
    samplerate=SAMPLE_RATE,
    blocksize=BUFFER_SIZE,
    callback=audio_callback
)
stream.start()

# === Paměť pro výšky sloupců (pro vyhlazování) ===
bars = np.zeros(NUM_BARS)
peaks = np.zeros(NUM_BARS)  # Paměť pro peaks (maximální hodnoty)

# === Funkce pro logaritmické rozmístění frekvencí ===
def get_log_frequency_bins(num_bins, min_freq, max_freq, sample_rate):
    freqs = np.logspace(np.log10(min_freq), np.log10(max_freq), num_bins)
    freqs = np.clip(freqs, 0, sample_rate // 2)
    return freqs

# === Funkce pro formátování popisků (kHz pro > 1000Hz) ===
def format_frequency_label(freq):
    if freq >= 1000:
        return f"{freq / 1000:.1f} kHz"
    else:
        return f"{int(freq)} Hz"

# === Hlavní smyčka programu ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Vymazání obrazovky
    screen.fill((0, 0, 0))

    # Zpracování FFT
    fft_data = np.abs(np.fft.rfft(audio_data))
    fft_data = fft_data[:NUM_BARS]
    fft_data = np.log(fft_data + 1)

    # Normalizace
    max_value = np.max(fft_data)
    if max_value > 0:
        fft_data = fft_data / max_value

    # Vykreslení sloupců
    bar_width = WIDTH / NUM_BARS
    for i in range(NUM_BARS):
        target_height = fft_data[i] * (HEIGHT - 100)  # necháme místo dole na stupnici
        bars[i] = 0.8 * bars[i] + 0.2 * target_height  # vyhlazování sloupců

        # Sledování maxima pro peak
        peaks[i] = max(peaks[i], bars[i])  # uložíme maximální hodnotu pro peak

        # Pomalu snižujeme peak (fading efekt)
        peaks[i] *= 0.99  # Zpomalení poklesu peak hodnoty

        x = i * bar_width

        # Hlavní sloupec (bílý)
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (int(x), int(HEIGHT - 100 - bars[i]), int(bar_width - 2), int(bars[i]))
        )

        # Slabá šedá čárka nad každým sloupcem (peak) - s fading efektem
        peak_height = peaks[i] * 0.05  # 5% z výšky sloupce pro šedou čárku
        pygame.draw.line(
            screen,
            (169, 169, 169),  # Šedá barva (Light Gray)
            (int(x + bar_width / 4), int(HEIGHT - 100 - peaks[i] - peak_height)),  # Začátek čáry
            (int(x + 3 * bar_width / 4), int(HEIGHT - 100 - peaks[i] - peak_height)),  # Konec čáry
            2  # Šířka čáry
        )

    # === Nakreslení stupnice ===
    # Vodorovná čára
    pygame.draw.line(screen, (200, 200, 200), (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)

    # Získání frekvenčních binů
    freqs = get_log_frequency_bins(NUM_BARS, 20, 20000, SAMPLE_RATE)

    # Číselné popisky
    step = 5  # Každých 5 sloupců zobrazíme frekvenci
    for i in range(0, NUM_BARS, step):
        freq_label = format_frequency_label(freqs[i])
        label_surface = font.render(freq_label, True, (200, 200, 200))
        label_rect = label_surface.get_rect(center=(int(i * bar_width), HEIGHT - 80))
        screen.blit(label_surface, label_rect)

    # Aktualizace obrazovky
    pygame.display.flip()
    clock.tick(FPS)

# === Ukončení ===
stream.stop()
stream.close()
pygame.quit()
