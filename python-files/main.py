
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
grass_texture = "white cube"
stone_texture = "white cube"
brick_texture = "white cube"

app = Ursina()

# Настройки окна
window.title = "Minecraft на Ursina"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False


# Выбор блока
selected_block = 'grass'


# Создаем каркас мира
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            texture=texture,
            color=color.white,
            highlight_color=color.lime,
            scale=1.0,
            origin_y=0.5
        )

    def input(self, key):
        if self.hovered:
            if key == 'o' :
                quit()
            if key == 'left mouse down':
                if selected_block == 'grass':
                    voxel = Voxel(position=self.position + mouse.normal, texture=grass_texture)
                elif selected_block == 'stone':
                    voxel = Voxel(position=self.position + mouse.normal, texture=stone_texture)
                elif selected_block == 'brick':
                    voxel = Voxel(position=self.position + mouse.normal, texture=brick_texture)
            elif key == 'right mouse down':
                destroy(self)


# Генерация платформы
for x in range(8):
    for z in range(8):
        voxel = Voxel(position=(x, 0, z))

# Камера от первого лица
player = FirstPersonController(
    position=(4, 5, 4),  # Стартовая позиция над платформой
    speed=5  # Скорость движения
)


# Горячие клавиши для выбора блоков
def update():
    global selected_block
    if held_keys['1']: selected_block = 'grass'
    if held_keys['2']: selected_block = 'stone'
    if held_keys['3']: selected_block = 'brick'





app.run()