import arcade
import os

Win_width = 1400
Win_height = 800
Win_title = 'Cool-Platformer'
Title_width = 124
Player_speed = 10
Player_jump = 15
Rainbow = 'Rainbowdash'

Dir_right = 0
Dir_left = 1

PATH = os.path.dirname(__file__) + os.sep

class PlayerCharacter(arcade.Sprite):
    def __init__(self, path_image, scale, physic_engine):
        image_def = path_image + '_idle.png'

        super().__init__(image_def, scale=scale)
        self.path_assets = path_image
        self.scale = scale
        self.frame = 0
        self.physic_engine = physic_engine

        self.direction = Dir_right

        self.idle_texture = [arcade.load_texture(self.path_assets + ".png"),
                             arcade.load_texture(self.path_assets + ".png", flipped_horizontally=True)
        ]
        self.jump_texture = [arcade.load_texture(self.path_assets + "_jump.png"),
                             arcade.load_texture(self.path_assets + "_jump.png", flipped_horizontally=True)
        ]

        self.fall_texture = [arcade.load_texture(self.path_assets + "_fall.png", flipped_horizontally=True),
                             arcade.load_texture(self.path_assets + "_fall.png")
        ]

        self.walk_textures = [[], []]

        for i in range(8):
            self.walk_textures[Dir_right].append(arcade.load_texture(self.path_assets + f'_walking{str(i)}.png')),
            self.walk_textures[Dir_left].append(arcade.load_texture(self.path_assets + f'_walking{str(i)}.png', flipped_horizontally=True))

        

    def update_animation(self):
        
        self.texture = self.idle_texture[self.direction]
        if self.change_y != 0:
            self.texture = self.jump_texture[self.direction]
        if self.change_y < 0:
            self.texture = self.fall_texture[self.direction]
        if self.change_x != 0 and self.change_y == 0:
            self.texture = self.walk_textures[self.direction][self.frame]
        if self.frame >= len(self.walk_textures[self.direction]) - 1:
            self.frame = 0
        else:
            self.frame += 1

class Enemy(PlayerCharacter):
    def update(self):
        if self.right > self.boundary_right:
            self.change_x = change_x * -1

# class StartScene(arcade.View):
#     def __init__(self):
#         super().__init__()

#         self.button = arcade.Sprite('')
#         self.button.center_x = Win_width / 2
#         self.button.center_y = Win_height / 2

#     def on_draw(self):
#         self.button.draw()

#     def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):

#         Platformer = 

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(Win_width, Win_height, Win_title, False, True)
        
        self.background_color = None
        self.background_sprite = None
        self.scene = None
        self.player = None
        self.physic_engine = None
        self.camera = None
        self.direction = None 
        self.score = 0

        self.keydown = {"Left": False, "Right": False}
        self.limits_worlds = {}

    def setup(self):
        self.background_color = arcade.color.ANDROID_GREEN
        arcade.set_background_color(self.background_color)
        self.title_map = arcade.load_tilemap(PATH + 'Map2.json')
        self.scene = arcade.Scene.from_tilemap(self.title_map)

        self.background_sprite = arcade.Sprite('background1.jpg')
        self.background_sprite.width = Win_width
        self.background_sprite.height = Win_height

        self.enemies_init = self.title_map.object_lists
        #Add enemies
        # for point in self.enemies_init:
        #     enemy = Enemy('zombie_idle.png')
        #     print(point.shape)
        #     enemy.left = point.shape[0]
        #     enemy.top = point.shape[1]
        #     enemy.change_x = point.properties['change_x']
        #     enemy.change_left = point.properties['boundary_left']
        #     enemy.change_right = point.properties['boundary_right']
        #     enemy.physic_engine = arcade.PhysicsEnginePlatformer(
        #         enemy, self.scene['Wall'], 0.50
        # )
        #     self.scene.add_sprite('Enemies', enemy)

        #Камера
        self.camera = arcade.Camera()
        self.limits_worlds['Left'] = 0
        self.limits_worlds['Right'] = Title_width * 35
        self.limits_worlds['Down'] = 0  

        #Игрок
        self.player = PlayerCharacter(Rainbow, 2, self.physic_engine)
        self.player.center_x = 200
        self.player.center_y = 280
        self.scene.add_sprite('Player', self.player)

        self.physic_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.scene['Wall'], 0.30
        )

    def on_update(self, delta_time):
        self.player.change_x = 0
        if self.keydown ["Left"] == True:
           self.player.change_x = -Player_speed 
           self.player.direction = Dir_left
        if self.keydown ["Right"] == True:
            self.player.change_x = Player_speed
            self.player.direction = Dir_right
        self.physic_engine.update()

        # for enemy in self.scene['Enemies']:
        #     enemy.update()
        #     enemy.physic_engine.update()
        #     enemy.update_animation(delta_time)

        self.player.update_animation()
        #self.scene.update(["Enemies"])

        self.background_sprite.left = self.camera.position[0]
        self.background_sprite.bottom = self.camera.position[1]

        self.player_camera()
    
        col_obj = arcade.check_for_collision_with_list(self.player, self.scene['Coins'])

        for obj in col_obj:
            obj.remove_from_sprite_lists()
            self.score = self.score + 1

    def player_camera(self):
        camera_x = self.player.center_x - (self.camera.viewport_width / 2)
        camera_y = self.player.center_y - (self.camera.viewport_height / 2)

        if camera_x < self.limits_worlds['Left']:
            camera_x = self.limits_worlds['Left']

        if camera_x + self.camera.viewport_width > self.limits_worlds['Right']:
            camera_x = self.limits_worlds['Right'] - self.camera.viewport_width

        if camera_y < self.limits_worlds['Down']:
            camera_y = self.limits_worlds['Down']
            
        self.camera.move_to((camera_x, camera_y), 0.1)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.LEFT:
            self.keydown ["Left"] = True

        if symbol == arcade.key.RIGHT:
            self.keydown ["Right"] = True

        if symbol == arcade.key.UP:
            if self.physic_engine.can_jump():
                self.player.change_y = Player_jump

        if symbol == arcade.key.DOWN:
            self.player.change_y = -Player_jump

        # if symbol == arcade.key.C:
        #     self.score += 1
            

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.keydown ['Left'] = False

        if symbol == arcade.key.RIGHT:
            self.keydown ['Right'] = False

    def AdminConsole(self, symbol: int, modifiers: int):
        ...

    def on_draw(self):
        self.clear()
        self.background_sprite.draw()
        self.camera.use()
        self.scene.draw()
        
        #GUI
        arcade.draw_text("Очки:" + str(self.score), 0 + self.camera.position[0], 700 + self.camera.position[1], font_size=50, color=arcade.color.SCHOOL_BUS_YELLOW)

Platformer = MyGame()
Platformer.setup()

# start_scene = StartScene()
# Platformer.show_view(start_scene)

arcade.run()