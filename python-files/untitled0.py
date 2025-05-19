import pygame
pygame.init()
window_size = (640, 480)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Птичка")
color = (216, 233, 243)
frame_images = []
for i in range(1, 9):
    frame_images.append(pygame.image.load(f"frame{i}.jpg"))
animation_length = len(frame_images)
animation_speed = 15
current_frame_index = 0
animation_timer = 0
frame_position = [0, 0]
window_height = screen.get_height()
window_width = screen.get_width()
frame_height = frame_images[0].get_height()
frame_position[1] = int(window_height * 0.45) - int(frame_height / 2)
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    time_delta = clock.tick(60) / 1000.0
    animation_timer += time_delta
    if animation_timer >= 1.0 / animation_speed:
        current_frame_index = (current_frame_index + 1) % animation_length
        animation_timer -= 1.0 / animation_speed
    screen.fill(color)
    current_frame = frame_images[current_frame_index]
    screen.blit(current_frame, frame_position)
    frame_position[0] += 4
    if frame_position[0] > window_width:
        frame_position[0] = -120
    pygame.display.flip()
pygame.quit()