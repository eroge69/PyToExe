from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController # سنعدله ليصبح منظور شخص ثالث
import random

# --- إعدادات اللعبة الأولية ---
BOT_COUNT = 10
PLAYER_SPEED = 5
PLAYER_JUMP_HEIGHT = 0.3
PLAYER_CROUCH_SPEED_MULTIPLIER = 0.6
PLAYER_RUN_SPEED_MULTIPLIER = 1.5 # عند الضغط على Z

# --- تعريف الأسلحة (كمثال بسيط) ---
WEAPONS = {
    "UMP": {"damage": 15, "fire_rate": 0.1, "ammo": 30, "model": 'cube', "color": color.dark_gray, "scale": (0.1, 0.2, 0.5)},
    "Deagle": {"damage": 50, "fire_rate": 0.5, "ammo": 7, "model": 'cube', "color": color.silver, "scale": (0.08, 0.15, 0.3)}
}

class VoxelPlayer(Entity):
    def __init__(self, position=(0,2,0), **kwargs):
        super().__init__(model='cube', collider='box', color=color.orange, position=position, **kwargs)
        self.speed = PLAYER_SPEED
        self.base_speed = PLAYER_SPEED
        self.jump_height = PLAYER_JUMP_HEIGHT
        self.gravity = 1
        self.grounded = False
        self.crouching = False
        self.running = False

        # أسلحة اللاعب
        self.current_weapon_index = 0
        self.available_weapons = ["UMP", "Deagle"]
        self.weapon_entity = None
        self.equip_weapon()

        # كاميرا منظور الشخص الثالث
        self.camera_pivot = Entity(parent=self, y=1.5) # نقطة دوران الكاميرا فوق اللاعب
        camera.parent = self.camera_pivot
        camera.position = (0, 2, -7) # ابعاد الكاميرا عن اللاعب
        camera.rotation = (-10, 0, 0) # ميل الكاميرا للأسفل قليلاً
        camera.fov = 90
        mouse.locked = True # لإخفاء مؤشر الفأرة والتحكم بالكاميرا

    def equip_weapon(self):
        if self.weapon_entity:
            destroy(self.weapon_entity)
        
        weapon_name = self.available_weapons[self.current_weapon_index]
        stats = WEAPONS[weapon_name]
        self.weapon_entity = Entity(
            parent=camera, # السلاح يتبع الكاميرا ليكون في مرمى النظر
            model=stats["model"],
            color=stats["color"],
            scale=stats["scale"],
            position=(0.3, -0.3, 1), # موقع السلاح بالنسبة للكاميرا
            rotation=(0,0,0)
        )
        print(f"Equipped: {weapon_name}")

    def update(self):
        # الحركة
        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
        ).normalized()

        # تحديد السرعة بناءً على الجري أو الجلوس
        current_speed = self.base_speed
        if self.running:
            current_speed *= PLAYER_RUN_SPEED_MULTIPLIER
        elif self.crouching:
            current_speed *= PLAYER_CROUCH_SPEED_MULTIPLIER

        # تطبيق الحركة
        origin = self.world_position + (self.up*.5)
        hit_info = raycast(origin , self.direction, ignore=(self,), distance=.5, debug=False)
        if not hit_info.hit:
            self.position += self.direction * current_speed * time.dt

        # دوران اللاعب مع الفأرة
        self.rotation_y += mouse.velocity[0] * 40
        self.camera_pivot.rotation_x -= mouse.velocity[1] * 40
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -60, 60) # تحديد زاوية نظر الكاميرا

        # الجاذبية والقفز
        if not self.grounded:
            self.y -= self.gravity * time.dt * 2 # تسريع السقوط قليلاً
            # تحقق بسيط من الأرض (يمكن تحسينه)
            ground_check = raycast(self.world_position + Vec3(0,-0.49,0), self.down, ignore=(self,), distance=0.1)
            if ground_check.hit:
                self.y = اداکار.entity.y + 0.5 # تأكد من أن y هو المكان الصحيح
                self.grounded = True
        else:
            # اذا كان على الارض يمكنه القفز
            if held_keys['space']:
                self.y += self.jump_height
                self.grounded = False
    
    def input(self, key):
        if key == 'left mouse down':
            self.shoot()
        elif key == 'right mouse down':
            print("Scope (Not implemented yet)") # هنا يمكنك إضافة منطق السكوب
        elif key == 'e':
            self.switch_weapon()
        elif key == 'a' and not (held_keys['w'] or held_keys['s'] or held_keys['d']): # A لوضع الجدار (تأكد ألا تتعارض مع الحركة)
            self.place_gloo_wall()
        elif key == 'left shift': # أو 'shift'
            self.crouch()
        elif key == 'left shift up':
            self.stand_up()
        elif key == 'z':
            self.running = True
        elif key == 'z up':
            self.running = False
        elif key == 'space': # القفز يتم التعامل معه في update عند grounded
            if self.grounded:
                self.y += self.jump_height * 20 * time.dt # دفعة أولية للقفز
                self.grounded = False
                
    def shoot(self):
        if self.weapon_entity:
            weapon_name = self.available_weapons[self.current_weapon_index]
            print(f"Player shoots with {weapon_name}!")
            # تتبع الطلقة (Raycast)
            # اتجاه الطلقة هو اتجاه نظر الكاميرا
            hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(self, self.weapon_entity), debug=False)
            if hit_info.hit:
                print(f"Hit: {hit_info.entity}")
                if isinstance(hit_info.entity, Bot):
                    hit_info.entity.take_damage(WEAPONS[weapon_name]["damage"])
            
            # تأثير بسيط لإطلاق النار (يمكنك إضافة صوت أو ضوء هنا)
            Bullet(position=self.weapon_entity.world_position + camera.forward * 0.5, direction=camera.forward)


    def switch_weapon(self):
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.available_weapons)
        self.equip_weapon()

    def place_gloo_wall(self):
        print("Player places Gloo Wall!")
        # تحديد مكان وضع الجدار أمام اللاعب
        # يجب أن يتم التحقق من عدم التداخل مع كائنات أخرى
        wall_pos = self.position + self.forward * 2 + Vec3(0,0.5,0) # أمام اللاعب وعلى ارتفاع مناسب
        
        # التحقق من عدم وجود عوائق كبيرة في مكان وضع الجدار
        overlap_check = boxcast(wall_pos, direction=(0,0,0), thickness=(1,2,0.5), distance=0.1, ignore=(self,))
        if not overlap_check.hit:
            GlooWall(position=wall_pos, rotation_y=self.rotation_y)
        else:
            print("Cannot place gloo wall here, obstruction.")


    def crouch(self):
        if not self.crouching:
            print("Player crouches.")
            self.crouching = True
            self.scale_y = 0.6 # تصغير اللاعب
            self.y -= 0.2 # إنزاله قليلاً ليظل على الأرض
            # يمكن أيضًا تقليل ارتفاع الكاميرا إذا أردت
            # self.camera_pivot.y = 1.0
            
    def stand_up(self):
        if self.crouching:
            print("Player stands up.")
            self.crouching = False
            self.scale_y = 1.0 # إعادة حجم اللاعب
            self.y += 0.2 # إعادته لارتفاعه الطبيعي
            # self.camera_pivot.y = 1.5


class GlooWall(Entity):
    def __init__(self, position=(0,0,0), **kwargs):
        super().__init__(
            model='cube',
            color=color.cyan,
            collider='box',
            position=position,
            scale=(3, 2.5, 0.5), # حجم الجدار
            **kwargs
        )
        # يمكن إضافة مؤقت لتدمير الجدار ذاتيًا
        # self.health = 100
        destroy(self, delay=15) # يدمر الجدار بعد 15 ثانية

class Bullet(Entity):
    def __init__(self, position, direction):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=0.1,
            position=position,
            collider=None # الطلقات عادة لا تحتاج مصادم إلا إذا أردت تفاعلات معقدة
        )
        self.direction = direction.normalized()
        self.speed = 50
        destroy(self, delay=1) # الطلقة تختفي بعد ثانية

    def update(self):
        self.position += self.direction * self.speed * time.dt


class Bot(Entity):
    def __init__(self, position=(0,1,0), target_player=None):
        super().__init__(model='cube', collider='box', color=color.red, position=position)
        self.health = 100
        self.speed = 2
        self.target_player = target_player
        self.state = "idle" # يمكن أن يكون 'idle', 'chasing', 'attacking'
        self.patrol_point = self.position + Vec3(random.uniform(-10,10), 0, random.uniform(-10,10))
        self.shoot_cooldown = 0
        self.vision_range = 20
        self.attack_range = 15

    def update(self):
        self.shoot_cooldown -= time.dt
        if not self.target_player:
            return

        dist_to_player = distance_xz(self.position, self.target_player.position)

        if dist_to_player < self.vision_range:
            self.state = "chasing"
            self.look_at_2d(self.target_player.position, 'y') # النظر نحو اللاعب على محور Y فقط
            
            if dist_to_player > self.attack_range / 2: # يتحرك نحو اللاعب إذا كان بعيدًا
                 # تحقق من العوائق قبل الحركة
                hit_info = raycast(self.world_position + Vec3(0,0.5,0), self.forward, ignore=(self,self.target_player), distance=1)
                if not hit_info.hit:
                    self.position += self.forward * self.speed * time.dt
            
            if dist_to_player < self.attack_range and self.shoot_cooldown <= 0:
                self.shoot_at_player()
        else:
            self.state = "idle"
            # منطق دورية بسيط
            if distance_xz(self.position, self.patrol_point) < 2:
                self.patrol_point = self.position + Vec3(random.uniform(-15,15), 0, random.uniform(-15,15))
            else:
                self.look_at_2d(self.patrol_point, 'y')
                self.position += self.forward * (self.speed / 2) * time.dt


    def shoot_at_player(self):
        if self.target_player:
            print(f"Bot shoots at player from {self.position}!")
            self.shoot_cooldown = random.uniform(0.5, 2) # وقت عشوائي بين الطلقات
            # يمكن إضافة Raycast هنا للتحقق من إصابة اللاعب
            # Bullet(position=self.world_position + self.forward * 0.5, direction=self.forward) # إذا أردت أن يطلق البوت طلقات مرئية

    def take_damage(self, amount):
        self.health -= amount
        print(f"Bot took {amount} damage, health: {self.health}")
        if self.health <= 0:
            self.die_and_respawn()

    def die_and_respawn(self):
        print("Bot died and will respawn.")
        # إعادة تعيين الموقع والصحة (يمكنك إضافة تأثير انفجار أو اختفاء)
        self.position = (random.uniform(-20, 20), 1, random.uniform(-20, 20))
        self.health = 100
        self.state = "idle"


# --- إعداد اللعبة الرئيسي ---
app = Ursina(borderless=False, fullscreen=False) # يمكنك تغيير هذا لـ fullscreen=True لاحقًا

# إنشاء اللاعب
player = VoxelPlayer(position=(0,2,0))

# إنشاء الأرضية
ground = Entity(model='plane', scale=(100,1,100), color=color.rgb(50,150,50), texture='white_cube', texture_scale=(100,100), collider='box')
# إنشاء بعض العوائق البسيطة
for i in range(10):
    Entity(model='cube', color=color.gray, collider='box', 
           position=(random.uniform(-40,40), random.uniform(1,3), random.uniform(-40,40)),
           scale = (random.uniform(1,5), random.uniform(1,6), random.uniform(1,5)))


# إنشاء الأعداء (Bots)
bots = []
for i in range(BOT_COUNT):
    bot_pos = (random.uniform(-20, 20), 1, random.uniform(-20, 20))
    # تأكد ألا يظهر البوت داخل اللاعب أو عائق آخر
    while distance(Vec3(bot_pos), player.position) < 5 :
         bot_pos = (random.uniform(-20, 20), 1, random.uniform(-20, 20))
    bots.append(Bot(position=bot_pos, target_player=player))


# إضاءة بسيطة (اختياري)
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky() # سماء بسيطة

# تشغيل اللعبة
app.run()