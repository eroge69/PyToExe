import pygame
import sys
import math
import random

# Initialize Pygame and mixer for sound
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
BOUNCE_FACTOR = 0.8
FRICTION = 0.99
ROTATION_SPEED = 0.5  # degrees per frame
SOUND_THRESHOLD = 4.3  # Minimum speed to trigger bounce sound

# Colors
SOFT_DARK_BLUE = (36, 54, 99)
SOFT_GREY = (200, 200, 200)
WHITE = (255, 255, 255)
RED = (255, 100, 100)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Hexagon Physics with Sound")
clock = pygame.time.Clock()

# Load sound
try:
    bounce_sound = pygame.mixer.Sound("bounce.mp3")
except:
    # Create a dummy sound if file not found
    print("Warning: bounce.mp3 not found, using silent sound")
    bounce_sound = pygame.mixer.Sound(buffer=bytearray(44))

# Hexagon parameters
hex_radius = 200
hex_center = (WIDTH // 2, HEIGHT // 2)
hex_border_width = 15  # Fatter borders
hex_rotation = 0

# Ball parameters
ball_radius = 20
ball_pos = [hex_center[0], hex_center[1] - 100]
ball_vel = [random.uniform(-5, 5), random.uniform(-5, 5)]

def get_hex_points(rotation=0):
    """Calculate hexagon points with rotation"""
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30 + rotation
        angle_rad = math.pi / 180 * angle_deg
        x = hex_center[0] + hex_radius * math.cos(angle_rad)
        y = hex_center[1] + hex_radius * math.sin(angle_rad)
        points.append((x, y))
    return points

def point_in_hexagon(point, hex_points):
    """Check if a point is inside a hexagon using ray casting algorithm"""
    x, y = point
    inside = False
    n = len(hex_points)
    
    for i in range(n):
        j = (i + 1) % n
        xi, yi = hex_points[i]
        xj, yj = hex_points[j]
        
        if ((yi > y) != (yj > y)):
            intersect = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < intersect:
                inside = not inside
    return inside

def distance_point_to_line(point, line_start, line_end):
    """Calculate distance from point to line segment"""
    x, y = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    l2 = (x2 - x1)**2 + (y2 - y1)**2
    if l2 == 0:
        return math.sqrt((x - x1)**2 + (y - y1)**2)
    
    t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / l2))
    projection = (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    
    return math.sqrt((x - projection[0])**2 + (y - projection[1])**2)

def check_collision(ball_pos, ball_vel, hex_points):
    """Check for collisions between ball and hexagon walls"""
    collision_occurred = False
    for i in range(len(hex_points)):
        j = (i + 1) % len(hex_points)
        line_start = hex_points[i]
        line_end = hex_points[j]
        
        dist = distance_point_to_line(ball_pos, line_start, line_end)
        
        if dist <= ball_radius + hex_border_width/2:
            # Calculate speed before collision
            speed_before = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2)
            
            # Calculate normal vector to the line
            nx = -(line_end[1] - line_start[1])
            ny = line_end[0] - line_start[0]
            norm_length = math.sqrt(nx**2 + ny**2)
            if norm_length > 0:
                nx /= norm_length
                ny /= norm_length
            
            dot_product = ball_vel[0] * nx + ball_vel[1] * ny
            
            # Reflect velocity
            ball_vel[0] -= 2 * dot_product * nx * BOUNCE_FACTOR
            ball_vel[1] -= 2 * dot_product * ny * BOUNCE_FACTOR
            
            # Move ball outside collision
            overlap = (ball_radius + hex_border_width/2) - dist
            ball_pos[0] += overlap * nx
            ball_pos[1] += overlap * ny
            
            # Apply friction
            ball_vel[0] *= FRICTION
            ball_vel[1] *= FRICTION
            
            # Play sound if collision was hard enough
            if speed_before > SOUND_THRESHOLD:
                bounce_sound.play()
            
            collision_occurred = True
    return collision_occurred

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                # Reset ball position and velocity
                ball_pos = [hex_center[0], hex_center[1] - 100]
                ball_vel = [random.uniform(-5, 5), random.uniform(-5, 5)]
            elif event.key == pygame.K_LEFT:
                ROTATION_SPEED -= 0.1
            elif event.key == pygame.K_RIGHT:
                ROTATION_SPEED += 0.1
    
    # Update hexagon rotation
    hex_rotation = (hex_rotation + ROTATION_SPEED) % 360
    hex_points = get_hex_points(hex_rotation)
    
    # Update physics
    ball_vel[1] += GRAVITY
    
    # Update position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    
    # Check collisions with hexagon walls
    check_collision(ball_pos, ball_vel, hex_points)
    
    # Keep ball inside hexagon (in case it somehow gets out)
    if not point_in_hexagon(ball_pos, hex_points):
        # Find closest hexagon point and push ball inside
        closest_dist = float('inf')
        closest_point = None
        for point in hex_points:
            dist = math.sqrt((ball_pos[0] - point[0])**2 + (ball_pos[1] - point[1])**2)
            if dist < closest_dist:
                closest_dist = dist
                closest_point = point
        
        if closest_point:
            direction = [ball_pos[0] - closest_point[0], ball_pos[1] - closest_point[1]]
            length = math.sqrt(direction[0]**2 + direction[1]**2)
            if length > 0:
                direction = [direction[0]/length, direction[1]/length]
                ball_pos[0] = closest_point[0] + direction[0] * (ball_radius + hex_border_width/2)
                ball_pos[1] = closest_point[1] + direction[1] * (ball_radius + hex_border_width/2)
    
    # Draw everything
    screen.fill(SOFT_DARK_BLUE)
    
    # Draw hexagon with fatter borders
    pygame.draw.polygon(screen, SOFT_GREY, hex_points, 0)  # Fill
    pygame.draw.polygon(screen, (150, 150, 150), hex_points, hex_border_width)  # Border
    
    # Draw ball
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
    
    # Display rotation speed
    font = pygame.font.SysFont('Arial', 20)
    speed_text = font.render(f"Rotation Speed: {ROTATION_SPEED:.1f}°/frame (LEFT/RIGHT to adjust)", True, WHITE)
    screen.blit(speed_text, (10, 10))
    
    # Display collision info
    current_speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2)
    speed_info = font.render(f"Ball Speed: {current_speed:.1f} (Sound > {SOUND_THRESHOLD})", True, WHITE)
    screen.blit(speed_info, (10, 40))
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()