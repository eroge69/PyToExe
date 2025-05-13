from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

app = Ursina()

textures = {
    'grass': load_texture('grass.png'),
    'dirt': load_texture('dirt.png'),
    'stone': load_texture('stone.png'),
    'wood': load_texture('wood.png'),
    'water': load_texture('water.png'),
    'lava': load_texture('lava.png'),
    'glass': load_texture('glass.png'),
    'leaves': load_texture('leaves.png'),
    'sword': load_texture('sword.png'),
    'cow': load_texture('cow.png')
}

block_size = 2
chunk_size = 16          # reduziert für schnelle Ladezeit
render_distance = 1      # reduziert
flying = False
animals = []

class Voxel(Button):
    def __init__(self, position=(0,0,0), texture='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=textures[texture],
            color=color.white,
            scale=block_size
        )
        self.block_type = texture

def get_block_type(x, z):
    noise = (math.sin(x*0.1) + math.cos(z*0.1)) * 10
    if noise < -3:
        return 'stone'
    elif noise < 0:
        return 'dirt'
    elif noise < 2:
        return 'grass'
    elif noise < 3:
        return 'wood'
    elif noise < 5:
        return 'leaves'
    else:
        return random.choice(['grass', 'dirt', 'wood'])

def get_height(x, z):
    return int(4 + math.sin(x * 0.1) * 2 + math.cos(z * 0.1) * 2)

loaded_chunks = {}
def generate_chunk(cx, cz):
    if (cx, cz) in loaded_chunks:
        return
    for x in range(chunk_size):
        for z in range(chunk_size):
            world_x = cx * chunk_size + x
            world_z = cz * chunk_size + z
            h = get_height(world_x, world_z)
            for y in range(h - 3, h + 1):
                t = get_block_type(world_x, world_z)
                Voxel(position=(world_x * block_size, y * block_size, world_z * block_size), texture=t)
    loaded_chunks[(cx, cz)] = True

class Animal(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            texture=textures['cow'],
            position=position,
            scale=(block_size, block_size, block_size),
            collider='box'
        )
        self.speed = 1

    def update(self):
        self.x += time.dt * self.speed * random.uniform(-1, 1)
        self.z += time.dt * self.speed * random.uniform(-1, 1)

def spawn_animals():
    for _ in range(5):
        x = random.randint(-10, 10) * block_size
        z = random.randint(-10, 10) * block_size
        y = get_height(x // block_size, z // block_size) * block_size + block_size
        cow = Animal(position=(x, y, z))
        animals.append(cow)

player = FirstPersonController(position=(0, 60, 0))  # sicher über der Welt
Sky()

def toggle_fly():
    global flying
    flying = not flying
    player.gravity = 0 if flying else 1

def update():
    cx = int(player.x) // (chunk_size * block_size)
    cz = int(player.z) // (chunk_size * block_size)
    for dx in range(-render_distance, render_distance+1):
        for dz in range(-render_distance, render_distance+1):
            generate_chunk(cx + dx, cz + dz)
    if flying:
        player.y += held_keys['0'] * 25 * time.dt
        player.y -= held_keys['left shift'] * 5 * time.dt
    for animal in animals:
        animal.update()

def input(key):
    if key == 'f':
        toggle_fly()
    if key == 'left mouse down':
        for h in mouse.hovered_entities:
            if isinstance(h, Voxel):
                destroy(h)
    if key == 'right mouse down':
        position = mouse.hovered_entity.position + mouse.normal * block_size
        Voxel(position=position, texture='grass')

spawn_animals()
app.run()
