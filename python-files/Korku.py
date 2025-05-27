import pygame
import os
import time
import math

# Pygame'ı başlat
pygame.init()

# Ekran boyutları
# Tam ekran modunda bu değerler otomatik olarak ekran çözünürlüğünüzden alınacaktır.
# Ancak yine de pencere modunda kullanmak isterseniz bir başlangıç boyutu belirlemek iyi olur.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Ekranı tam ekran olarak ayarla
# pygame.FULLSCREEN bayrağını ekliyoruz
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# Pencere başlığı (tam ekranda görünmeyebilir ama yine de tanımlı olsun)
pygame.display.set_caption("Korku Oyunu")

# Renkler (RGB formatında)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0) # Anahtar için sarı renk
BLUE = (0, 0, 255) # Placeholder, kullanılmayacak ama kalsın
GRAY = (150, 150, 150) # Menü butonları için

# Dosya yolları
# Çalıştırılan dosyanın dizinini alır
current_dir = os.path.dirname(__file__)
# 'assets' klasörünün yolunu oluşturur
assets_dir = os.path.join(current_dir, "assets")
# 'images' klasörünün yolunu oluşturur
images_dir = os.path.join(assets_dir, "images")
# 'sounds' klasörünün yolunu oluşturur
sounds_dir = os.path.join(assets_dir, "sounds")

# Font yükleme (mesajlar ve Game Over için)
font = pygame.font.Font(None, 36) # Genel mesajlar için
menu_font = pygame.font.Font(None, 64) # Menü başlığı ve butonları için
game_over_font = pygame.font.Font(None, 74) # Game Over için daha büyük font
timer_font = pygame.font.Font(None, 48) # Sayaç için font

# --- Oyuncu Sınıfı ---
# Oyuncunun özelliklerini (görsel, konum, hız, anahtar durumu) ve hareketini yönetir.
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            # Oyuncu görselini yükle ve boyutlandır
            self.image = pygame.image.load(os.path.join(images_dir, "player.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except pygame.error as e:
            # Görsel yüklenemezse varsayılan yeşil bir kare kullan
            print(f"Oyuncu görseli yüklenirken hata oluştu: {e}")
            self.image = pygame.Surface((50, 50))
            self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2 # Oyuncu hızı
        self.has_key = False # Oyuncunun anahtarı olup olmadığını tutar

    def update(self):
        # Klavye girdilerini al ve oyuncuyu hareket ettir
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Oyuncunun ekran sınırları içinde kalmasını sağla
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

# --- Canavar Sınıfı ---
# Canavarın özelliklerini (görsel, konum, hız) ve oyuncuyu takip etme mantığını yönetir.
class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            # Canavar görselini yükle ve boyutlandır
            self.image = pygame.image.load(os.path.join(images_dir, "monster.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 80))
        except pygame.error as e:
            # Görsel yüklenemezse varsayılan kırmızı bir kare kullan
            print(f"Canavar görseli yüklenirken hata oluştu: {e}")
            self.image = pygame.Surface((80, 80))
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1.5 # Canavar hızı

    def update(self, player_rect):
        # Canavarın oyuncuyu takip etme mantığı (basit takip)
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery

        distance = math.sqrt(dx**2 + dy**2)
        if distance > self.speed:
            self.rect.x += self.speed * (dx / distance)
            self.rect.y += self.speed * (dy / distance)
        else:
            self.rect.center = player_rect.center # Oyuncuya çok yakınsa direkt üzerine gelsin

        # Canavarın ekran sınırları içinde kalmasını sağla
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

# --- Anahtar Sınıfı ---
# Anahtarın görselini ve konumunu yönetir.
class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            # Anahtar görselini yükle ve boyutlandır
            self.image = pygame.image.load(os.path.join(images_dir, "key.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except pygame.error as e:
            # Görsel yüklenemezse varsayılan sarı bir kare kullan
            print(f"Anahtar görseli yüklenirken hata oluştu: {e}")
            self.image = pygame.Surface((50, 50))
            self.image.fill(YELLOW)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# --- Görsel Yükleme ---
game_images = {}
try:
    # Arka plan görsellerini yükle ve ekran boyutuna göre ölçeklendir
    game_images["room1_background"] = pygame.image.load(os.path.join(images_dir, "room1_background.png")).convert_alpha()
    game_images["room2_background"] = pygame.image.load(os.path.join(images_dir, "room2.png")).convert_alpha()
    game_images["room3_background"] = pygame.image.load(os.path.join(images_dir, "room3.png")).convert_alpha()
    game_images["room4_background"] = pygame.image.load(os.path.join(images_dir, "room4.png")).convert_alpha()
    game_images["small_door"] = pygame.image.load(os.path.join(images_dir, "small_door.png")).convert_alpha()
    game_images["jump_scare"] = pygame.image.load(os.path.join(images_dir, "jump_scare.png")).convert_alpha()
    # Kilitli kapı görseli yoksa varsayılan küçük kapı görselini kullan
    game_images["locked_door"] = pygame.image.load(os.path.join(images_dir, "locked_door.png")).convert_alpha() if os.path.exists(os.path.join(images_dir, "locked_door.png")) else game_images["small_door"]
    # Anahtar görseli yoksa varsayılan bir yüzey oluştur
    game_images["key"] = pygame.image.load(os.path.join(images_dir, "key.png")).convert_alpha() if os.path.exists(os.path.join(images_dir, "key.png")) else pygame.Surface((50,50))
    # Room3'ten Room4'e giden kilitli kapı için ayrı bir görsel (yoksa küçük kapı)
    game_images["locked_door_for_room3_to_room4"] = pygame.image.load(os.path.join(images_dir, "locked_door.png")).convert_alpha() if os.path.exists(os.path.join(images_dir, "locked_door.png")) else game_images["small_door"]

    # Basınç plakası görselleri ve boyutlandırma
    pressure_plate_size = (150, 150)
    game_images["pressure_plate_up"] = pygame.image.load(os.path.join(images_dir, "pressure_plate_up.png")).convert_alpha()
    game_images["pressure_plate_up"] = pygame.transform.scale(game_images["pressure_plate_up"], pressure_plate_size)
    game_images["pressure_plate_down"] = pygame.image.load(os.path.join(images_dir, "pressure_plate_down.png")).convert_alpha()
    game_images["pressure_plate_down"] = pygame.transform.scale(game_images["pressure_plate_down"], pressure_plate_size)
    # Menü arkaplan görseli (isteğe bağlı)
    game_images["menu_background"] = pygame.image.load(os.path.join(images_dir, "menu_background.png")).convert() if os.path.exists(os.path.join(images_dir, "menu_background.png")) else None

    # Arka planları ekran boyutuna ölçeklendir
    # Tam ekran modunda ekran boyutu otomatik olarak ayarlanacağı için,
    # bu ölçeklendirmelerden önce ekranın gerçek boyutlarını almak daha iyidir.
    # Bu nedenle, screen.get_size() kullanarak mevcut ekran boyutunu alıyoruz.
    current_screen_width, current_screen_height = screen.get_size()
    game_images["room1_background"] = pygame.transform.scale(game_images["room1_background"], (current_screen_width, current_screen_height))
    game_images["room2_background"] = pygame.transform.scale(game_images["room2_background"], (current_screen_width, current_screen_height))
    game_images["room3_background"] = pygame.transform.scale(game_images["room3_background"], (current_screen_width, current_screen_height))
    game_images["room4_background"] = pygame.transform.scale(game_images["room4_background"], (current_screen_width, current_screen_height))
    game_images["jump_scare"] = pygame.transform.scale(game_images["jump_scare"], (current_screen_width, current_screen_height))
    if game_images["menu_background"]:
        game_images["menu_background"] = pygame.transform.scale(game_images["menu_background"], (current_screen_width, current_screen_height))

except pygame.error as e:
    # Görsel yükleme hatası durumunda oyunu kapat
    print(f"Görsel yüklenirken hata oluştu: {e}")
    pygame.quit()
    exit()

# Ses Yükleme
game_sounds = {}
try:
    # Ses dosyalarını yükle
    game_sounds["background_ambience"] = pygame.mixer.Sound(os.path.join(sounds_dir, "background_ambience.wav"))
    game_sounds["door_creak"] = pygame.mixer.Sound(os.path.join(sounds_dir, "door_creak.wav"))
    game_sounds["jump_scare_scream"] = pygame.mixer.Sound(os.path.join(sounds_dir, "jump_scare_scream.wav"))
    game_sounds["monster_chase"] = pygame.mixer.Sound(os.path.join(sounds_dir, "monster_chase.wav"))
    game_sounds["key_pickup"] = pygame.mixer.Sound(os.path.join(sounds_dir, "key_pickup.wav"))
    game_sounds["locked_door"] = pygame.mixer.Sound(os.path.join(sounds_dir, "locked_door.wav"))
    # Bulmaca çözme ve plaka basma sesleri için varsayılan sesler (yoksa anahtar alma sesi)
    game_sounds["puzzle_solve"] = pygame.mixer.Sound(os.path.join(sounds_dir, "puzzle_solve.wav")) if os.path.exists(os.path.join(sounds_dir, "puzzle_solve.wav")) else game_sounds["key_pickup"]
    game_sounds["plate_press_sound"] = pygame.mixer.Sound(os.path.join(sounds_dir, "plate_press.wav")) if os.path.exists(os.path.join(sounds_dir, "plate_press.wav")) else game_sounds["key_pickup"]
    game_sounds["menu_music"] = pygame.mixer.Sound(os.path.join(sounds_dir, "menu_music.wav")) if os.path.exists(os.path.join(sounds_dir, "menu_music.wav")) else None # Menü müziği

except pygame.error as e:
    # Ses yükleme veya oynatma hatası durumunda devam et (oyunu kapatma)
    print(f"Ses yüklenirken veya oynatılırken hata oluştu: {e}")
    pass
start_text = menu_font.render("oyuna Başla", True, WHITE)
exit_text = menu_font.render("Çıkış", True, WHITE)

# --- Oyun Durumları ---
# Oyunun hangi aşamada olduğunu belirleyen sabitler
MAIN_MENU = -1 # Yeni eklenen menü durumu
MAIN_GAME = 0 # Normal oyun
JUMP_SCARE_ACTIVE = 1 # Jump scare aktif
MONSTER_CHASE = 2 # Canavar kovalıyor
CATCH_JUMP_SCARE_ACTIVE = 3 # Canavar yakaladıktan sonraki jump scare
GAME_OVER = 4 # Oyun bitti (kaybedildi)
GAME_WON = 5 # Oyun bitti (kazanıldı)
TIMER_MONSTER_CHASE = 6 # Süre bitince canavar kovalaması (Room 3 için)

# --- Oda Durumları ---
# Oyuncunun hangi odada olduğunu belirleyen sabitler
ROOM1 = 0
ROOM2 = 1
ROOM3 = 2
ROOM4 = 3

# Oyun döngüsü için değişkenler
running = True # Oyun çalışıyor mu?
# current_game_state'i başlangıçta MAIN_MENU olarak ayarla
current_game_state = MAIN_MENU
current_room = ROOM1 # Oyuncunun mevcut odası (oyun başladığında MAIN_GAME'e geçince ROOM1'e gidecek)

jump_scare_start_time = 0 # Jump scare'in başladığı zaman
JUMP_SCARE_DURATION = 1.5 # Jump scare süresi (saniye)

monster_active = False # Canavar aktif mi?
jump_scare_triggered_once = False # Room2'deki jump scare bir kere tetiklendi mi?

catch_jump_scare_start_time = 0 # Yakalandıktan sonraki jump scare'in başladığı zaman

# Room3 Sayaç Değişkenleri
room3_timer_active = False # Room 3 sayacı aktif mi?
room3_start_time = 0 # Sayacın başladığı zaman
room3_time_limit = 30 # Saniye cinsinden süre sınırı (örneğin 30 saniye)
monster_spawned_room3 = False # Room3'te canavarın ortaya çıkıp çıkmadığını kontrol eder

# Room4 Bulmaca Değişkenleri
room4_puzzle_active = False # Room 4 bulmacası aktif mi?
room4_password_sequence = [pygame.K_k, pygame.K_a, pygame.K_p, pygame.K_i] # Doğru şifre tuşları (KAPI)
player_password_input = [] # Oyuncunun girdiği tuşları tutacak
room4_door_open = False # Room 4'teki son kapı açık mı?


# --- Oyuncu Nesnesi Oluşturma ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75)

# --- Canavar Nesnesi Oluşturma ---
monster = Monster(-100, -100) # Başlangıçta ekran dışında (görünmez)

# --- Anahtar Nesnesi Oluşturma ---
key = Key(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50) # Anahtarın konumu
key_visible = True # Anahtar görünür mü?

# --- Kapı ve Etkileşim Alanları ---
door_width = 100
door_height = 150

# Tam ekran modunda koordinatları güncelleyeceğiz
# Ekranın gerçek boyutlarını al
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# Room1'den Room2'ye geçen kapı
door_rect_room1_to_room2 = pygame.Rect(50, 50, door_width, door_height)
# Kapının etkileşim alanı (kapının biraz daha etrafını kapsar)
door_trigger_zone_room1_to_room2 = pygame.Rect(door_rect_room1_to_room2.x, door_rect_room1_to_room2.y - 20, door_width, door_height + 20)

# Room2'den Room1'e geçen kapı
door_rect_room2_to_room1 = pygame.Rect(50, SCREEN_HEIGHT // 2 - 75, door_width, door_height)
door_trigger_zone_room2_to_room1 = pygame.Rect(door_rect_room2_to_room1.x, door_rect_room2_to_room1.y, door_width + 20, door_height)

# Room1'deki kilitli kapı (Room3'e geçiş)
locked_door_rect_room1 = pygame.Rect(SCREEN_WIDTH // 2 - (door_width // 2), SCREEN_HEIGHT // 2 - 100, door_width, door_height)
locked_door_trigger_zone_room1 = pygame.Rect(locked_door_rect_room1.x, locked_door_rect_room1.y, door_width, door_height + 20)
locked_door_open = False # Bu kapı açık mı?

# Room3'ten Room4'e geçen kilitli kapı
door_rect_room3_to_room4 = pygame.Rect(SCREEN_WIDTH - door_width - 50, SCREEN_HEIGHT // 2 - 75, door_width, door_height)
door_trigger_zone_room3_to_room4 = pygame.Rect(door_rect_room3_to_room4.x, door_rect_room3_to_room4.y, door_width, door_height + 20)
door_room3_to_room4_locked = True # Başlangıçta kilitli

# Room4'ten Room3'e geçen kapı
door_rect_room4_to_room3 = pygame.Rect(50, SCREEN_HEIGHT // 2 - 75, door_width, door_height)
door_trigger_zone_room4_to_room3 = pygame.Rect(door_rect_room4_to_room3.x, door_rect_room4_to_room3.y, door_width + 20, door_height)

# Room2'deki canavar kovalamasını tetikleyen bölge (jump scare bölgesi)
jump_scare_trigger_zone_room2 = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 75, 150, 150)

# --- Room3 Basınç Plakaları Bulmacası ---
plate_size = pressure_plate_size[0] # 150x150 idi
# Plakaları ekranın üstünde 3 ve altında 3 adet olacak şekilde düzenleme
# x_offset plakaların yatayda eşit aralıklarla dağılması için
x_offset = (SCREEN_WIDTH - 3 * plate_size) // 4 # 3 plaka ve 4 boşluk (kenarlar da dahil)

pressure_plates_data = [
    # Üst sıradaki 3 plaka
    {"id": 0, "rect": pygame.Rect(x_offset, 50, plate_size, plate_size), "is_pressed": False, "last_pressed_time": 0},
    {"id": 1, "rect": pygame.Rect(2 * x_offset + plate_size, 50, plate_size, plate_size), "is_pressed": False, "last_pressed_time": 0},
    {"id": 2, "rect": pygame.Rect(3 * x_offset + 2 * plate_size, 50, plate_size, plate_size), "is_pressed": False, "last_pressed_time": 0},
    # Alt sıradaki 3 plaka
    {"id": 3, "rect": pygame.Rect(x_offset, SCREEN_HEIGHT - 50 - plate_size, plate_size, plate_size), "is_pressed": False, "last_pressed_time": 0},
    {"id": 4, "rect": pygame.Rect(2 * x_offset + plate_size, SCREEN_HEIGHT - 50 - plate_size, plate_size, plate_size), "is_pressed": False, "last_pressed_time": 0},
    {"id": 5, "rect": pygame.Rect(3 * x_offset + 2 * plate_size, SCREEN_HEIGHT - 50 - plate_size, plate_size, plate_size), "is_pressed": False, "last_pressed_time": 0},
]

# Doğru plaka basma sırası (örneğin 0, 4, 1, 3, 5, 2)
puzzle_sequence = [0, 4, 1, 3, 5, 2] # Yeni 6 plakalı örnek sıra. Bunu değiştirebilirsin!
player_sequence = [] # Oyuncunun bastığı sırayı tutacak
puzzle_solved = False # Bulmaca çözüldü mü?
PLATE_PRESS_COOLDOWN = 0.5 # Yanlış basıldığında sıfırlanma süresi veya basılı kalma süresi

# Mesaj göstermek için değişkenler
display_message = False
message_text = ""
message_start_time = 0
MESSAGE_DURATION = 2 # Mesajın ekranda kalma süresi (saniye)

def show_message(text):
    # Ekranda kısa süreli mesaj göstermek için fonksiyon
    global display_message, message_text, message_start_time
    message_text = text
    display_message = True
    message_start_time = time.time()

# --- Oyunu Başlangıç Durumuna Getiren Fonksiyon ---
# Yeni oyun başladığında tüm değişkenleri sıfırlar.
def reset_game():
    global player, monster, key, key_visible, locked_door_open, \
           door_room3_to_room4_locked, puzzle_solved, player_sequence, \
           room3_timer_active, room3_start_time, monster_spawned_room3, \
           jump_scare_triggered_once, monster_active, current_room, \
           current_game_state, room4_puzzle_active, room4_door_open, player_password_input, \
           pressure_plates_data

    # Oyuncunun ve diğer nesnelerin konumlarını tam ekran boyutlarına göre güncelleyin
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75)
    monster = Monster(-100, -100)
    key = Key(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
    key_visible = True
    locked_door_open = False
    door_room3_to_room4_locked = True
    puzzle_solved = False
    player_sequence = []
    room3_timer_active = False
    room3_start_time = 0
    monster_spawned_room3 = False
    jump_scare_triggered_once = False
    monster_active = False
    current_room = ROOM1
    current_game_state = MAIN_GAME # Oyun başlangıç durumu
    room4_puzzle_active = False
    room4_door_open = False
    player_password_input = []

    # Basınç plakalarının durumunu sıfırla
    for p in pressure_plates_data:
        p["is_pressed"] = False
        p["last_pressed_time"] = 0

    # Sesleri durdur ve arka plan ambiyansını başlat
    pygame.mixer.stop()
    if game_sounds["background_ambience"]:
        game_sounds["background_ambience"].play(-1)
        game_sounds["background_ambience"].set_volume(0.5)

# --- Oyun Döngüsü ---
clock = pygame.time.Clock()
FPS = 60 # Saniyedeki kare sayısı

# Menü müziğini başlat (Oyun başlar başlamaz menüde olacağımız için burada başlatırız)
if game_sounds["menu_music"]:
    pygame.mixer.stop() # Diğer sesleri durdur (varsa)
    game_sounds["menu_music"].play(-1) # Sürekli çal
    game_sounds["menu_music"].set_volume(0.4)

while running:
    dt = clock.tick(FPS) / 1000.0 # Delta time (saniye cinsinden), frame süresi

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Oyunu kapatma isteği
        
        # Tam ekrandan çıkmak için Esc tuşu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False # Oyunu kapat

        # Menü durumunda klavye veya fare olayları
        if current_game_state == MAIN_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # "Oyuna Başla" butonu
                start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
                if start_button_rect.collidepoint(mouse_pos):
                    reset_game() # Oyunu sıfırla ve başlat
                    print("Oyun Başladı!")
                    # Menü müziğini durdur
                    if game_sounds["menu_music"]:
                        game_sounds["menu_music"].stop()
                # "Çıkış" butonu
                exit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
                if exit_button_rect.collidepoint(mouse_pos):
                    running = False
            continue # Menüdeyken başka olayları kontrol etme

        # Oyun içi klavye tuş basımı olayları
        if event.type == pygame.KEYDOWN:
            # 'E' tuşu etkileşimleri
            if event.key == pygame.K_e:
                # Sadece belirli oyun durumlarındayken 'E' tuşu ile etkileşime izin ver
                if current_game_state == MAIN_GAME or current_game_state == MONSTER_CHASE or current_game_state == JUMP_SCARE_ACTIVE or current_game_state == TIMER_MONSTER_CHASE:
                    # Room1'den Room2'ye geçiş
                    if current_room == ROOM1 and player.rect.colliderect(door_trigger_zone_room1_to_room2):
                        current_room = ROOM2
                        player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75) # Oyuncuyu yeni odada uygun yere ışınla
                        if game_sounds["door_creak"]:
                            game_sounds["door_creak"].play()
                        show_message("Room 2'ye geçtin!")
                        print("Room 2'ye geçildi!")
                        # Canavar aktifse, kapıdan uzak bir noktaya ışınla
                        if monster_active:
                            monster.rect.center = (door_rect_room2_to_room1.centerx + 100, door_rect_room2_to_room1.centery)

                    # Room2'den Room1'e geçiş
                    elif current_room == ROOM2 and player.rect.colliderect(door_trigger_zone_room2_to_room1):
                        current_room = ROOM1
                        player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75)
                        if game_sounds["door_creak"]:
                            game_sounds["door_creak"].play()
                        show_message("Room 1'e geri döndün.")
                        print("Room 1'e geri dönüldü!")
                        # Canavar aktifse, kapıdan uzak bir noktaya ışınla
                        if monster_active:
                            monster.rect.center = (door_rect_room1_to_room2.centerx - 100, door_rect_room1_to_room2.centery)

                    # Room1'deki kilitli kapı (Room3'e geçiş)
                    elif current_room == ROOM1 and player.rect.colliderect(locked_door_trigger_zone_room1):
                        if player.has_key: # Oyuncunun anahtarı varsa
                            locked_door_open = True
                            show_message("Kapı açıldı! Yeni bir odaya geçiliyor...")
                            if game_sounds["door_creak"]:
                                game_sounds["door_creak"].play()
                            print("Kilitli kapı açıldı!")

                            current_room = ROOM3 # Room 3'e geçiş
                            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

                            # Room3'e girince sayacı başlat
                            room3_timer_active = True
                            room3_start_time = time.time()
                            show_message(f"Bu odada {room3_time_limit} saniyen var!")

                            # Room3'e girince canavarı pasifleştir ve sesini durdur
                            monster_active = False
                            monster.rect.center = (-100, -100) # Ekran dışına taşı
                            if "monster_chase" in game_sounds:
                                # Canavar kovalamaca sesi çalıyorsa durdur
                                if game_sounds["monster_chase"] in [pygame.mixer.Channel(i).get_sound() for i in range(pygame.mixer.get_num_channels())]:
                                    game_sounds["monster_chase"].stop()

                            show_message("Canavar sizi takip etmeyi bıraktı!")
                            current_game_state = MAIN_GAME # Oyun durumunu normale çevir
                            print("Room 3'e geçildi, canavar pasif. Sayaç başlatıldı.")
                        else:
                            # Anahtar yoksa kilitli kapı sesi çal ve mesaj göster
                            show_message("Bu kapı kilitli. Bir anahtara ihtiyacın var.")
                            if game_sounds["locked_door"]:
                                game_sounds["locked_door"].play()
                            print("Kilitli kapı. Anahtar gerekli.")

                    # Room3'ten Room4'e geçiş (kilitli kapı veya açık kapı)
                    elif current_room == ROOM3 and player.rect.colliderect(door_trigger_zone_room3_to_room4):
                        if door_room3_to_room4_locked: # Kapı kilitli ise
                            show_message("Bu kapı kilitli görünüyor. Bir şeyler yapmalısın!")
                            if game_sounds["locked_door"]:
                                game_sounds["locked_door"].play()
                        else: # Kapı açık
                            current_room = ROOM4
                            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75)
                            if game_sounds["door_creak"]:
                                game_sounds["door_creak"].play()
                            show_message("Daha da derine iniyorsun...")
                            print("Room 4'e geçildi!")
                            room3_timer_active = False # Room4'e geçince sayacı durdur
                            monster_spawned_room3 = False # Room4'e geçince canavarın durumunu sıfırla
                            # Canavar sesi çalıyorsa durdur
                            if "monster_chase" in game_sounds:
                                if game_sounds["monster_chase"] in [pygame.mixer.Channel(i).get_sound() for i in range(pygame.mixer.get_num_channels())]:
                                    game_sounds["monster_chase"].stop()
                            # Room 4'e girince bulmacayı başlat
                            room4_puzzle_active = True
                            player_password_input = [] # Şifre girişini sıfırla
                            show_message("Son kapı kilitli. 'KAPI' şifresini tuşla!")

                    # Room4'ten Room3'e geçiş
                    elif current_room == ROOM4 and player.rect.colliderect(door_trigger_zone_room4_to_room3):
                        current_room = ROOM3
                        player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) # Ortaya ışınla
                        if game_sounds["door_creak"]:
                            game_sounds["door_creak"].play()
                        show_message("Room 3'e geri döndün.")
                        print("Room 3'e geri dönüldü!")
                        # Eğer bulmaca çözülmediyse ve süre dolmamışsa sayacı tekrar başlat
                        if not puzzle_solved and not monster_spawned_room3:
                            room3_timer_active = True
                            # Geçen süreyi koruyarak yeni başlangıç zamanı ayarla
                            if room3_start_time != 0:
                                elapsed_at_exit = time.time() - room3_start_time
                                room3_start_time = time.time() - elapsed_at_exit
                            else:
                                room3_start_time = time.time()
                            show_message(f"Room 3'e geri döndün. Kalan süre: {int(room3_time_limit - (time.time() - room3_start_time))} saniye.")
                        elif monster_spawned_room3: # Canavar Room3'te aktifse
                            current_game_state = TIMER_MONSTER_CHASE # Geri dönüldüğünde kovalamaca devam etmeli
                            monster_active = True
                            monster.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4) # Canavarı tekrar görünür yap
                            if game_sounds["monster_chase"]:
                                game_sounds["monster_chase"].play(-1)
                                game_sounds["monster_chase"].set_volume(0.3)
                            print("Room 3'e geri dönüldü, canavar takibi devam ediyor.")

            # Room 4 Bulmacası Klavye Girdisi (Sadece Room 4'te ve bulmaca aktifken)
            if current_room == ROOM4 and room4_puzzle_active and not room4_door_open:
                # Sadece 'KAPI' harfleriyle ilgileniyoruz
                # Her tuşa basıldığında, o tuşun kodunu player_password_input listesine ekle
                if event.key in room4_password_sequence: # Sadece doğru tuşları dikkate al
                    player_password_input.append(event.key)
                    # Mesajı anında güncelle
                    entered_chars = [chr(k).upper() for k in player_password_input if k >= pygame.K_a and k <= pygame.K_z]
                    show_message("".join(entered_chars) + "...")

                    # Girilen şifreyi kontrol et
                    if player_password_input == room4_password_sequence:
                        room4_door_open = True
                        room4_puzzle_active = False # Bulmacayı devre dışı bırak
                        # current_game_state = GAME_WON # Eski kod
                        current_game_state = MAIN_MENU # Oyun kazanılınca menüye dön
                        show_message("Son kapı açıldı! Kazandın!")
                        if game_sounds["puzzle_solve"]: # Bulmaca çözme sesini kullan
                            game_sounds["puzzle_solve"].play()
                        # Arka plan müziğini durdur ve menü müziğini başlat
                        pygame.mixer.stop() # Tüm sesleri durdur
                        if game_sounds["menu_music"]:
                            game_sounds["menu_music"].play(-1)
                            game_sounds["menu_music"].set_volume(0.4)
                        print("Oyun Bitti: KAZANDIN! Menüye dönülüyor.")
                    elif len(player_password_input) > len(room4_password_sequence) or \
                         (len(player_password_input) > 0 and player_password_input[-1] != room4_password_sequence[len(player_password_input)-1]):
                        # Şifreden daha uzun bir giriş olursa veya yanlış tuşa basılırsa sıfırla
                        player_password_input = []
                        show_message("Yanlış sıra! Tekrar dene.")
                else: # Doğru tuşlar dışında bir tuşa basıldıysa sıfırla (eğer zaten bir şey girilmişse)
                    if len(player_password_input) > 0:
                        player_password_input = []
                        show_message("Yanlış tuş! Tekrar dene.")


        # Game Over veya Game Won sonrası tıklama ile çıkış (Bu kısım GAME_WON için değişti)
        if current_game_state == GAME_OVER and event.type == pygame.MOUSEBUTTONDOWN:
            print("Oyun bitti.")
            running = False # Oyun tamamen kapatılır

    # Oyun durumuna göre güncellemeler
    if current_game_state == MAIN_GAME:
        player.update()

        # Anahtar toplama kontrolü (sadece o odada ve anahtar görünürse)
        if current_room == ROOM2 and key_visible and player.rect.colliderect(key.rect):
            player.has_key = True
            key_visible = False
            show_message("Bir anahtar buldun!")
            if game_sounds["key_pickup"]:
                game_sounds["key_pickup"].play()
            print("Anahtar alındı!")

        # Room2'de canavar kovalamasını tetikleme mantığı (Jump Scare)
        if current_room == ROOM2 and player.rect.colliderect(jump_scare_trigger_zone_room2) and not jump_scare_triggered_once:
            current_game_state = JUMP_SCARE_ACTIVE # Jump scare durumuna geç
            jump_scare_start_time = time.time()
            if game_sounds["jump_scare_scream"]:
                game_sounds["jump_scare_scream"].play()
            jump_scare_triggered_once = True # Bir daha tetiklenmesin
            if "background_ambience" in game_sounds:
                game_sounds["background_ambience"].set_volume(0.1) # Ambiyans sesini kıs

            print("Canavar kovalaması tetiklendi (sadece çığlık sesi ile)!")

        # Room3 Basınç Plakaları Bulmacası Güncelleme
        if current_room == ROOM3 and not puzzle_solved:
            for plate_data in pressure_plates_data:
                # Plaka daha önce basılmadıysa, oyuncu şu an üzerinde duruyorsa ve bekleme süresi geçtiyse
                if not plate_data["is_pressed"] and player.rect.colliderect(plate_data["rect"]) and \
                   (time.time() - plate_data["last_pressed_time"] > PLATE_PRESS_COOLDOWN):

                    plate_data["is_pressed"] = True
                    plate_data["last_pressed_time"] = time.time()
                    player_sequence.append(plate_data["id"]) # Basılan plakanın ID'sini sıraya ekle
                    if game_sounds["plate_press_sound"]:
                        game_sounds["plate_press_sound"].play()

                    show_message(f"Plaka {plate_data['id']} basıldı!")
                    print(f"Player sequence: {player_sequence}")

                    # Sıra yanlış mı gidiyor?
                    if len(player_sequence) > 0 and player_sequence[-1] != puzzle_sequence[len(player_sequence)-1]:
                        show_message("Yanlış sıra! Tekrar dene.")
                        player_sequence = [] # Sıfırla
                        # Tüm plakaları tekrar yukarı çek (görseli sıfırla)
                        for p in pressure_plates_data:
                            p["is_pressed"] = False
                            p["last_pressed_time"] = time.time() # Kısa bir bekleme süresi
                    # Bulmaca çözüldü mü?
                    elif player_sequence == puzzle_sequence:
                        puzzle_solved = True
                        door_room3_to_room4_locked = False # Kapıyı aç!
                        show_message("Tebrikler! Kapı açıldı.")
                        if game_sounds["puzzle_solve"]:
                            game_sounds["puzzle_solve"].play()
                        print("Basınç plakaları bulmacası çözüldü!")
                        room3_timer_active = False # Bulmaca çözülünce sayacı durdur
                        monster_spawned_room3 = False # Canavar aktifse de pasifleştir
                        if "monster_chase" in game_sounds:
                            if game_sounds["monster_chase"] in [pygame.mixer.Channel(i).get_sound() for i in range(pygame.mixer.get_num_channels())]:
                                game_sounds["monster_chase"].stop()


        # Room3 zaman sayacı kontrolü
        # Eğer Room 3'teyseniz, sayaç aktifse ve bulmaca çözülmediyse
        if room3_timer_active and current_room == ROOM3 and not puzzle_solved:
            remaining_time_raw = room3_time_limit - (time.time() - room3_start_time)
            if remaining_time_raw <= 0:
                # Süre doldu!
                if not monster_spawned_room3: # Canavar henüz ortaya çıkmadıysa
                    current_game_state = TIMER_MONSTER_CHASE # Canavar kovalamaca durumuna geç
                    monster_active = True
                    monster_spawned_room3 = True # Canavarın ortaya çıktığını işaretle
                    monster.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4) # Canavarı ekranın üst orta kısmına yerleştir
                    show_message("Süre doldu! Canavar ortaya çıktı, KAPIDAN KAÇ!")
                    print("Süre doldu. Canavar Room3'te aktifleşti.")
                    if game_sounds["monster_chase"]:
                        game_sounds["monster_chase"].play(-1) # Sürekli çal
                        game_sounds["monster_chase"].set_volume(0.3)
                    if "background_ambience" in game_sounds:
                        game_sounds["background_ambience"].set_volume(0.1) # Ambiyans sesini kıs
                # Süre dolduğunda kapıyı aç!
                door_room3_to_room4_locked = False


    elif current_game_state == JUMP_SCARE_ACTIVE:
        player.update() # Oyuncu hala hareket edebilir (isteğe bağlı)
        current_time = time.time()
        if current_time - jump_scare_start_time >= JUMP_SCARE_DURATION:
            current_game_state = MONSTER_CHASE # Jump scare bitince canavar takibine geç
            monster_active = True
            monster.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4) # Canavarı ekranda görünür yap
            if game_sounds["monster_chase"]:
                game_sounds["monster_chase"].play(-1)
                game_sounds["monster_chase"].set_volume(0.3)
            if "background_ambience" in game_sounds:
                game_sounds["background_ambience"].set_volume(0.5) # Ambiyans sesini normale döndür
            print("Canavar aktif oldu ve takip başlıyor!")

    elif current_game_state == MONSTER_CHASE or current_game_state == TIMER_MONSTER_CHASE:
        player.update()
        # Canavar sadece Room1, Room2 veya Room3'te (süre dolduğunda) aktifse takip eder
        if monster_active and (current_room == ROOM1 or current_room == ROOM2 or (current_room == ROOM3 and monster_spawned_room3)):
            monster.update(player.rect)

            # Kovalamaca sırasında anahtar toplama
            if current_room == ROOM2 and key_visible and player.rect.colliderect(key.rect):
                player.has_key = True
                key_visible = False
                show_message("Bir anahtar buldun!")
                if game_sounds["key_pickup"]:
                    game_sounds["key_pickup"].play()
                print("Anahtar alındı (kovalamaca sırasında)!")

            # Canavar oyuncuyu yakalarsa
            if player.rect.colliderect(monster.rect):
                print("Canavar sizi yakaladı! Jump scare tetikleniyor...")
                current_game_state = CATCH_JUMP_SCARE_ACTIVE # Yakalanma jump scare'ine geç
                catch_jump_scare_start_time = time.time()
                # Sesleri durdur
                pygame.mixer.stop() # Tüm sesleri durdur
                if game_sounds["jump_scare_scream"]:
                    game_sounds["jump_scare_scream"].play()

    elif current_game_state == CATCH_JUMP_SCARE_ACTIVE:
        current_time = time.time()
        if current_time - catch_jump_scare_start_time >= JUMP_SCARE_DURATION:
            current_game_state = MAIN_MENU # Jump scare bitince oyun biter
            print("Oyun Bitti: Yakalandın!")
            # Eğer menü müziği varsa başlat
            if game_sounds["menu_music"]:
                game_sounds["menu_music"].play(-1)
                game_sounds["menu_music"].set_volume(0.4)

    # Ekranı temizle (her karede baştan çizilir)
    screen.fill(BLACK)

    # Oyun durumuna ve oda durumuna göre çizim yap
    if current_game_state == MAIN_MENU:
        if game_images["menu_background"]:
            screen.blit(game_images["menu_background"], (0, 0))
        else:
            screen.fill(BLACK)

        title_text = menu_font.render("KORKU EVİ", True, RED)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_text, title_rect)
        title_text = menu_font.render("Kapı etkileşimi için [E]", True, BLUE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.2))
        screen.blit(title_text, title_rect)
        title_text = menu_font.render("Hareket için [W, A, S, D]", True, BLUE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.7))
        screen.blit(title_text, title_rect)

        # "Oyuna Başla" butonu
        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        pygame.draw.rect(screen, GRAY, start_button_rect)
        screen.blit(start_text, start_text.get_rect(center=start_button_rect.center))

        # "Çıkış" butonu
        exit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
        pygame.draw.rect(screen, GRAY, exit_button_rect)
        screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

    elif current_game_state == MAIN_GAME or current_game_state == JUMP_SCARE_ACTIVE or \
         current_game_state == MONSTER_CHASE or current_game_state == TIMER_MONSTER_CHASE:
        if current_room == ROOM1:
            screen.blit(game_images["room1_background"], (0, 0))
            # Room1'den Room2'ye kapıyı çiz
            door_img_scaled = pygame.transform.scale(game_images["small_door"], (door_width, door_height))
            screen.blit(door_img_scaled, door_rect_room1_to_room2)

            # Room1'deki kilitli kapıyı çiz
            locked_door_img_scaled = pygame.transform.scale(game_images["locked_door"], (door_width, door_height))
            screen.blit(locked_door_img_scaled, locked_door_rect_room1)

        elif current_room == ROOM2:
            screen.blit(game_images["room2_background"], (0, 0))
            # Room2'den Room1'e kapıyı çiz
            door_img_scaled = pygame.transform.scale(game_images["small_door"], (door_width, door_height))
            screen.blit(door_img_scaled, door_rect_room2_to_room1)

            if key_visible: # Anahtar görünürse çiz
                screen.blit(key.image, key.rect)

        elif current_room == ROOM3:
            screen.blit(game_images["room3_background"], (0, 0))

            # Room3'ten Room4'e giden kapı (kilitli veya açık duruma göre)
            door_img_scaled_locked = pygame.transform.scale(game_images["locked_door_for_room3_to_room4"], (door_width, door_height))
            door_img_scaled_unlocked = pygame.transform.scale(game_images["small_door"], (door_width, door_height))

            if door_room3_to_room4_locked:
                screen.blit(door_img_scaled_locked, door_rect_room3_to_room4)
            else:
                screen.blit(door_img_scaled_unlocked, door_rect_room3_to_room4)

            # Basınç Plakalarını Çiz (basılı olup olmamalarına göre)
            for plate_data in pressure_plates_data:
                if plate_data["is_pressed"]:
                    screen.blit(game_images["pressure_plate_down"], plate_data["rect"])
                else:
                    screen.blit(game_images["pressure_plate_up"], plate_data["rect"])

            # Room3 için sayaç çizimi (canavar gelmediyse veya bulmaca çözülmediyse)
            if room3_timer_active and not puzzle_solved and not monster_spawned_room3:
                remaining_time = max(0, int(room3_time_limit - (time.time() - room3_start_time)))
                timer_text = timer_font.render(f"Süre: {remaining_time:02d}", True, YELLOW)
                screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 20))

        elif current_room == ROOM4:
            screen.blit(game_images["room4_background"], (0, 0))
            # Room4'ten Room3'e kapıyı çiz
            door_img_scaled = pygame.transform.scale(game_images["small_door"], (door_width, door_height))
            screen.blit(door_img_scaled, door_rect_room4_to_room3)

            # Room 4'teki bulmaca ipucu ve girilen şifre
            if room4_puzzle_active and not room4_door_open:
                puzzle_hint_text = font.render("Kolu var bacağı yok, dikdörtgeni vardır, karesi yok. Şifreyi Tuşla.", True, YELLOW)
                hint_rect = puzzle_hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(puzzle_hint_text, hint_rect)

                # Oyuncunun şu ana kadar girdiği şifreyi göstermek
                entered_chars = [chr(k).upper() for k in player_password_input if k >= pygame.K_a and k <= pygame.K_z]
                current_input_display = font.render(
                    "".join(entered_chars), True, WHITE
                )
                input_rect = current_input_display.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                screen.blit(current_input_display, input_rect)

        # Oyuncu ve canavarı çiz
        screen.blit(player.image, player.rect)
        # Canavar sadece belirli odalarda aktifse ve görünür alandaysa çizilir
        if monster_active and (current_room == ROOM1 or current_room == ROOM2 or (current_room == ROOM3 and monster_spawned_room3)) and \
           monster.rect.x > -100 and monster.rect.y > -100: # Canavarın ekran dışında olmadığından emin ol
              screen.blit(monster.image, monster.rect)

    # Jump Scare anı (yakalanınca)
    elif current_game_state == CATCH_JUMP_SCARE_ACTIVE:
        screen.blit(game_images["jump_scare"], (0, 0)) # Jump scare görselini tam ekranda göster

    # Oyun Bitti (Kaybettin) ekranı
    elif current_game_state == GAME_OVER:
        screen.fill(BLACK)
        text = game_over_font.render("YAKALANDIN!", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)

        small_font = pygame.font.Font(None, 36)
        restart_text = small_font.render("Oyundan Çıkmak İçin Tıkla", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    # Oyun Bitti (Kazandın) ekranı (Şimdi bu ekrana geçmeden doğrudan menüye dönecek)
    elif current_game_state == GAME_WON:
        # Bu kısım artık doğrudan menüye yönlendirildiği için kullanılmayacak,
        # ancak kodu bozmamak adına şimdilik bırakabiliriz veya kaldırabiliriz.
        # Menüye geçiş mantığı zaten yukarıda implemente edildi.
        pass

    # Mesajları çiz (eğer aktifse)
    if display_message:
        current_time = time.time()
        if current_time - message_start_time < MESSAGE_DURATION:
            message_surface = font.render(message_text, True, WHITE)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            screen.blit(message_surface, message_rect)
        else:
            display_message = False # Mesaj süresi dolduysa gizle

    # Ekranı güncelle
    pygame.display.flip()

# Pygame'ı kapat
pygame.quit()
