from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Define Minecraft-like textures
textures = {
    'grass': load_texture('assets/grass.png'),
    'dirt': load_texture('assets/dirt.png'),
    'stone': load_texture('assets/stone.png'),
    'wood': load_texture('assets/wood.png'),
    'leaf': load_texture('assets/leaf.png'),
    'brick': load_texture('assets/brick.png'),
    'bedrock': load_texture('assets/bedrock.png')
}

# You'll need to download these textures from Minecraft or create similar ones
# Place them in an 'assets' folder in the same directory as your script

# Block types
block_types = {
    'grass': {'texture': textures['grass'], 'color': color.green},
    'dirt': {'texture': textures['dirt'], 'color': color.brown},
    'stone': {'texture': textures['stone'], 'color': color.gray},
    'wood': {'texture': textures['wood'], 'color': color.rgb(139, 69, 19)},
    'leaf': {'texture': textures['leaf'], 'color': color.lime},
    'brick': {'texture': textures['brick'], 'color': color.red},
    'bedrock': {'texture': textures['bedrock'], 'color': color.black}
}

# Voxel class
class Voxel(Button):
    def __init__(self, position=(0,0,0), block_type='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/block',
            origin_y=0.5,
            texture=block_types[block_type]['texture'],
            color=block_types[block_type]['color'],
            highlight_color=color.lime,
        )
    
    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                destroy(self)
            elif key == 'right mouse down':
                Voxel(position=self.position + mouse.normal, block_type='grass')

# Generate terrain
for z in range(16):
    for x in range(16):
        for y in range(2):
            if y == 1:
                block_type = 'grass'
            else:
                block_type = 'dirt'
            voxel = Voxel(position=(x,y,z), block_type=block_type)

# Player
player = FirstPersonController()
player.cursor.visible = False

# Sky
sky = Sky()

# Hand (like in Minecraft)
hand = Entity(
    parent=camera.ui,
    model='assets/arm',
    texture=textures['wood'],
    scale=0.2,
    rotation=Vec3(150,-10,0),
    position=Vec2(0.6,-0.6)
)

def update():
    if held_keys['escape']:
        application.quit()

app.run()
