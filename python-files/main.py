#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
لعبة باتل رويال 3D بسيطة مستوحاة من Free Fire برسومات مكعبة على غرار Minecraft
تم تعديل الكود لإنشاء الأشكال الهندسية برمجياً لتجنب مشاكل الأصول المفقودة.
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import (
    Point3, Vec3, CollisionTraverser, CollisionNode,
    CollisionHandlerQueue, CollisionRay, BitMask32,
    WindowProperties, AmbientLight, DirectionalLight,
    TextNode, NodePath, PandaNode, LVector3,
    GeomVertexFormat, GeomVertexData, Geom, GeomTriangles, GeomVertexWriter,
    GeomNode, Material
)
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame
import sys
import random
import math

# تعريف الثوابت
GROUND_SIZE = 100  # حجم أرضية اللعبة
PLAYER_SPEED = 10  # سرعة اللاعب
JUMP_FORCE = 15    # قوة القفز
GRAVITY = 9.8      # قوة الجاذبية
BOT_COUNT = 10     # عدد البوتات
WEAPON_DAMAGE = {
    "UMP": 10,
    "DEAGLE": 20
}

# دالة لإنشاء مكعب برمجيًا
def create_cube(name="cube"):
    """إنشاء NodePath لمكعب بسيط برمجيًا"""
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData(name, format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    # Vertices for a cube centered at origin with side length 1
    verts = [
        (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5), ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5),
        (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5), ( 0.5,  0.5,  0.5), (-0.5,  0.5,  0.5)
    ]
    
    # Normals for each face
    norms = [
        ( 0,  0, -1), ( 0,  0,  1), (-1,  0,  0), ( 1,  0,  0), ( 0, -1,  0), ( 0,  1,  0)
    ]
    
    # Indices for triangles (two triangles per face)
    indices = [
        (0, 1, 2), (2, 3, 0),  # Bottom face
        (4, 5, 6), (6, 7, 4),  # Top face
        (0, 4, 7), (7, 3, 0),  # Left face
        (1, 5, 6), (6, 2, 1),  # Right face
        (0, 1, 5), (5, 4, 0),  # Back face
        (3, 2, 6), (6, 7, 3)   # Front face
    ]
    
    # Normals corresponding to the faces defined by indices
    face_norms = [norms[0]]*2 + [norms[1]]*2 + [norms[2]]*2 + [norms[3]]*2 + [norms[4]]*2 + [norms[5]]*2

    tris = GeomTriangles(Geom.UHStatic)
    vert_index = 0
    for i in range(len(indices)):
        face_indices = indices[i]
        face_normal = face_norms[i]
        for vi in face_indices:
            vertex.addData3(verts[vi])
            normal.addData3(face_normal)
            color.addData4(1, 1, 1, 1) # Default white color
            texcoord.addData2(0, 0) # Dummy texcoord
            tris.addVertex(vert_index)
            vert_index += 1
        tris.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(tris)

    node = GeomNode(name)
    node.addGeom(geom)

    return NodePath(node)

class BattleRoyaleGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # إعداد النافذة
        self.setBackgroundColor(0.4, 0.6, 1.0)  # لون السماء
        props = WindowProperties()
        props.setTitle("لعبة باتل رويال 3D")
        props.setSize(1024, 768)
        self.win.requestProperties(props)
        
        # إخفاء مؤشر الفأرة وتفعيل وضع التحكم بالكاميرا
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self.disableMouse()
        
        # إعداد الإضاءة
        self.setup_lighting()
        
        # إنشاء العالم
        self.create_world()
        
        # إنشاء اللاعب
        self.create_player()
        
        # إنشاء البوتات (الأعداء)
        self.bots = []
        self.create_bots()
        
        # إعداد نظام التحكم
        self.setup_controls()
        
        # إعداد نظام الاصطدام
        self.setup_collision()
        
        # إعداد واجهة المستخدم
        self.setup_ui()
        
        # متغيرات اللعبة
        self.is_running = False
        self.is_crouching = False
        self.current_weapon = "UMP"
        self.score = 0
        self.health = 100
        
        # إضافة مهام التحديث
        self.taskMgr.add(self.update, "update")
        self.taskMgr.add(self.update_camera, "updateCamera")
        
        # تشغيل الموسيقى (اختياري)
        # self.background_music = self.loader.loadSfx("sounds/background.ogg")
        # self.background_music.setLoop(True)
        # self.background_music.play()
    
    def setup_lighting(self):
        """إعداد الإضاءة في اللعبة"""
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((0.6, 0.6, 0.6, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)
        
        directional_light = DirectionalLight("directional_light")
        directional_light.setColor((0.8, 0.8, 0.8, 1))
        directional_light_np = self.render.attachNewNode(directional_light)
        directional_light_np.setHpr(45, -45, 0)
        self.render.setLight(directional_light_np)
    
    def create_world(self):
        """إنشاء عالم اللعبة"""
        # إنشاء الأرضية باستخدام مكعب برمجي
        self.ground = create_cube("ground_cube")
        self.ground.setScale(GROUND_SIZE, GROUND_SIZE, 1)
        self.ground.setPos(0, 0, -1)
        self.ground.setColor(0.3, 0.7, 0.3)  # لون أخضر للأرضية
        self.ground.reparentTo(self.render)
        
        # إضافة بعض المكعبات العشوائية في العالم باستخدام مكعب برمجي
        for i in range(50):
            cube = create_cube(f"random_cube_{i}")
            x = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
            y = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
            z = 0
            size = random.uniform(1, 3)
            cube.setScale(size, size, size)
            cube.setPos(x, y, z)
            cube.setColor(random.random(), random.random(), random.random())
            cube.reparentTo(self.render)
    
    def create_player(self):
        """إنشاء اللاعب الرئيسي"""
        # إنشاء نموذج اللاعب (مكعب برمجي)
        self.player = create_cube("player_cube")
        self.player.setScale(0.5, 0.5, 1)
        self.player.setPos(0, 0, 1)
        self.player.setColor(0.2, 0.2, 0.8)  # لون أزرق للاعب
        self.player.reparentTo(self.render)
        
        # إعداد الكاميرا
        self.camera.reparentTo(self.player)
        self.camera.setPos(0, -3, 2)  # وضع الكاميرا خلف اللاعب (منظور الشخص الثالث)
        self.camera.lookAt(self.player)
        
        # متغيرات اللاعب
        self.player_velocity = Vec3(0, 0, 0)
        self.is_jumping = False
        self.weapons = ["UMP", "DEAGLE"]
        self.current_weapon_index = 0
        self.current_weapon = self.weapons[self.current_weapon_index]
        
        # إنشاء نموذج السلاح (مكعب برمجي)
        self.weapon_model = create_cube("weapon_cube")
        self.weapon_model.setScale(0.1, 0.5, 0.1)
        self.weapon_model.setPos(0.5, 0.5, 0)
        self.weapon_model.setColor(0.3, 0.3, 0.3)  # لون رمادي للسلاح
        self.weapon_model.reparentTo(self.camera)
    
    def create_bots(self):
        """إنشاء البوتات (الأعداء)"""
        for i in range(BOT_COUNT):
            bot = create_cube(f"bot_cube_{i}")
            bot.setScale(0.5, 0.5, 1)
            
            # وضع البوتات في مواقع عشوائية
            x = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
            y = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
            bot.setPos(x, y, 1)
            bot.setColor(0.8, 0.2, 0.2)  # لون أحمر للبوتات
            bot.reparentTo(self.render)
            
            # إضافة خصائص البوت
            bot_data = {
                "model": bot,
                "health": 100,
                "is_alive": True,
                "respawn_timer": 0,
                "direction": Vec3(random.uniform(-1, 1), random.uniform(-1, 1), 0),
                "change_dir_timer": random.uniform(1, 3)
            }
            self.bots.append(bot_data)
    
    def setup_controls(self):
        """إعداد أزرار التحكم"""
        self.accept("z", self.start_running)
        self.accept("z-up", self.stop_running)
        self.accept("space", self.jump)
        self.accept("shift", self.start_crouching)
        self.accept("shift-up", self.stop_crouching)
        self.accept("e", self.switch_weapon)
        self.accept("a", self.place_gloo_wall)
        self.accept("mouse1", self.fire_weapon)
        self.accept("mouse3", self.toggle_scope)
        self.accept("escape", sys.exit)
    
    def setup_collision(self):
        """إعداد نظام الاصطدام"""
        self.cTrav = CollisionTraverser()
        self.groundHandler = CollisionHandlerQueue()
        
        # إنشاء شعاع للكشف عن الأرضية
        self.groundRay = CollisionRay()
        self.groundRay.setOrigin(0, 0, 0)
        self.groundRay.setDirection(0, 0, -1)
        
        self.groundCol = CollisionNode('groundRay')
        self.groundCol.addSolid(self.groundRay)
        self.groundCol.setFromCollideMask(BitMask32.bit(1))
        self.groundCol.setIntoCollideMask(BitMask32.allOff())
        
        self.groundColNp = self.player.attachNewNode(self.groundCol)
        self.cTrav.addCollider(self.groundColNp, self.groundHandler)
        
        # جعل الأرضية قابلة للاصطدام مع شعاع الأرضية
        self.ground.setCollideMask(BitMask32.bit(1))

    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.weapon_text = OnscreenText(text="السلاح: UMP", pos=(-0.9, 0.9), scale=0.07, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5), align=TextNode.ALeft)
        self.score_text = OnscreenText(text="النقاط: 0", pos=(-0.9, 0.8), scale=0.07, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5), align=TextNode.ALeft)
        self.health_text = OnscreenText(text="الصحة: 100", pos=(-0.9, 0.7), scale=0.07, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5), align=TextNode.ALeft)
        self.crosshair = OnscreenText(text="+", pos=(0, 0), scale=0.07, fg=(1, 0, 0, 1))
    
    def update(self, task):
        """تحديث اللعبة في كل إطار"""
        dt = globalClock.getDt()
        self.update_player_movement(dt)
        self.update_bots(dt)
        self.update_ui()
        return Task.cont
    
    def update_camera(self, task):
        """تحديث الكاميرا (نظام Free Look)"""
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
            self.win.movePointer(0, int(self.win.getXSize() / 2), int(self.win.getYSize() / 2))
            self.player.setH(self.player.getH() - x * 100)
            current_p = self.camera.getP()
            new_p = current_p + y * 50
            new_p = max(-60, min(60, new_p))
            self.camera.setP(new_p)
        return Task.cont
    
    def update_player_movement(self, dt):
        """تحديث حركة اللاعب"""
        # تطبيق الجاذبية
        self.player_velocity.setZ(self.player_velocity.getZ() - GRAVITY * dt)
        
        # التحقق من الاصطدام بالأرضية
        self.cTrav.traverse(self.render)
        on_ground = False
        if self.groundHandler.getNumEntries() > 0:
            self.groundHandler.sortEntries()
            entry = self.groundHandler.getEntry(0)
            # التحقق من أن نقطة الاصطدام أسفل اللاعب مباشرة أو قريبة جداً
            if entry.getSurfacePoint(self.render).getZ() <= self.player.getZ() + 0.1:
                self.player.setZ(entry.getSurfacePoint(self.render).getZ() + 1.0) # إضافة 1.0 لارتفاع اللاعب
                self.player_velocity.setZ(0)
                self.is_jumping = False
                on_ground = True
        
        # إذا لم يكن على الأرض، استمر في تطبيق الجاذبية
        if not on_ground:
             self.is_jumping = True # اعتباره في الهواء

        # تحديث موضع اللاعب بناءً على السرعة
        # حساب الحركة بناءً على اتجاه اللاعب
        move_vec = Vec3(0,0,0)
        if self.keyMap["forward"]:
            move_vec += self.player.getQuat().getForward()
        if self.keyMap["backward"]:
            move_vec -= self.player.getQuat().getForward()
        if self.keyMap["left"]:
            move_vec -= self.player.getQuat().getRight()
        if self.keyMap["right"]:
            move_vec += self.player.getQuat().getRight()
            
        move_vec.setZ(0) # لا نريد تغيير الارتفاع بالحركة الأفقية
        move_vec.normalize()
        
        current_speed = PLAYER_SPEED * (0.5 if self.is_crouching else 1.0) * (1.5 if self.is_running else 1.0)
        
        # تطبيق الحركة الأفقية
        horizontal_movement = move_vec * current_speed * dt
        self.player.setPos(self.player.getPos() + horizontal_movement)

        # تطبيق الحركة الرأسية (الجاذبية والقفز)
        vertical_movement = Vec3(0, 0, self.player_velocity.getZ() * dt)
        self.player.setPos(self.player.getPos() + vertical_movement)
        
        # التأكد من عدم خروج اللاعب عن حدود العالم
        pos = self.player.getPos()
        half_ground = GROUND_SIZE / 2
        self.player.setX(max(-half_ground, min(half_ground, pos.getX())))
        self.player.setY(max(-half_ground, min(half_ground, pos.getY())))
        # منع اللاعب من السقوط تحت الأرضية
        if pos.getZ() < 0: 
            self.player.setZ(0)
            self.player_velocity.setZ(0)
            self.is_jumping = False

    def update_bots(self, dt):
        """تحديث البوتات"""
        for bot_data in self.bots:
            if bot_data["is_alive"]:
                bot = bot_data["model"]
                bot_data["change_dir_timer"] -= dt
                if bot_data["change_dir_timer"] <= 0:
                    bot_data["direction"] = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), 0)
                    bot_data["direction"].normalize()
                    bot_data["change_dir_timer"] = random.uniform(1, 3)
                
                speed = 3
                player_pos = self.player.getPos()
                bot_pos = bot.getPos()
                distance = (player_pos - bot_pos).length()
                
                if distance < 20:
                    direction_to_player = player_pos - bot_pos
                    direction_to_player.setZ(0) # تجاهل الارتفاع عند التوجيه
                    direction_to_player.normalize()
                    bot_data["direction"] = direction_to_player
                    bot.lookAt(self.player)
                    if distance < 10 and random.random() < 0.02: # زيادة طفيفة في معدل إطلاق النار
                        self.bot_fire(bot)
                
                bot.setPos(bot.getPos() + bot_data["direction"] * speed * dt)
                
                pos = bot.getPos()
                half_ground = GROUND_SIZE / 2
                if not (-half_ground < pos.getX() < half_ground):
                    bot.setX(max(-half_ground, min(half_ground, pos.getX())))
                    bot_data["direction"].setX(-bot_data["direction"].getX())
                if not (-half_ground < pos.getY() < half_ground):
                    bot.setY(max(-half_ground, min(half_ground, pos.getY())))
                    bot_data["direction"].setY(-bot_data["direction"].getY())
                if pos.getZ() < 0: # منع البوتات من السقوط
                    bot.setZ(0)
            else:
                bot_data["respawn_timer"] -= dt
                if bot_data["respawn_timer"] <= 0:
                    self.respawn_bot(bot_data)
    
    def update_ui(self):
        """تحديث واجهة المستخدم"""
        self.weapon_text.setText(f"السلاح: {self.current_weapon}")
        self.score_text.setText(f"النقاط: {self.score}")
        self.health_text.setText(f"الصحة: {max(0, int(self.health))}") # تأكد من أن الصحة لا تقل عن 0

    # --- وظائف التحكم --- 
    def setup_controls(self):
        """إعداد أزرار التحكم"""
        self.keyMap = {"forward": 0, "backward": 0, "left": 0, "right": 0}
        
        self.accept("w", self.setKey, ["forward", 1])
        self.accept("s", self.setKey, ["backward", 1])
        self.accept("a", self.setKey, ["left", 1])
        self.accept("d", self.setKey, ["right", 1])
        self.accept("w-up", self.setKey, ["forward", 0])
        self.accept("s-up", self.setKey, ["backward", 0])
        self.accept("a-up", self.setKey, ["left", 0])
        self.accept("d-up", self.setKey, ["right", 0])

        self.accept("z", self.start_running)
        self.accept("z-up", self.stop_running)
        self.accept("space", self.jump)
        self.accept("shift", self.start_crouching)
        self.accept("shift-up", self.stop_crouching)
        self.accept("e", self.switch_weapon)
        self.accept("q", self.place_gloo_wall) # تغيير زر الجدار إلى Q
        self.accept("mouse1", self.fire_weapon)
        self.accept("mouse3", self.toggle_scope)
        self.accept("escape", sys.exit)

    def setKey(self, key, value):
        self.keyMap[key] = value

    def start_running(self):
        self.is_running = True
    
    def stop_running(self):
        self.is_running = False
    
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.player_velocity.setZ(JUMP_FORCE)
    
    def start_crouching(self):
        if not self.is_crouching:
            self.is_crouching = True
            self.player.setScale(0.5, 0.5, 0.5)
    
    def stop_crouching(self):
        if self.is_crouching:
            self.is_crouching = False
            self.player.setScale(0.5, 0.5, 1)
    
    def switch_weapon(self):
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)
        self.current_weapon = self.weapons[self.current_weapon_index]
        if self.current_weapon == "UMP":
            self.weapon_model.setScale(0.1, 0.5, 0.1)
            self.weapon_model.setColor(0.3, 0.3, 0.3)
        else:
            self.weapon_model.setScale(0.1, 0.3, 0.1)
            self.weapon_model.setColor(0.5, 0.5, 0.2)
    
    def place_gloo_wall(self):
        """وضع جدار جلو"""
        angle = self.player.getH() * math.pi / 180
        dx = math.sin(angle)
        dy = math.cos(angle)
        wall_pos = self.player.getPos() + Point3(dx * 3, dy * 3, 0)
        wall = create_cube("gloo_wall")
        wall.setScale(2, 0.5, 2)
        wall.setPos(wall_pos)
        wall.setH(self.player.getH() + 90)
        wall.setColor(0.7, 0.7, 1.0, 0.8) # لون أزرق فاتح وشبه شفاف
        wall.setTransparency(True)
        wall.reparentTo(self.render)
        # يمكن إضافة مؤقت لإزالة الجدار بعد فترة
        # taskMgr.doMethodLater(10, self.remove_node, 'removeWall', extraArgs=[wall], appendTask=True)

    # def remove_node(self, node, task):
    #     node.removeNode()
    #     return Task.done

    def fire_weapon(self):
        """إطلاق النار"""
        # استخدام اتجاه الكاميرا لإطلاق النار بدقة أكبر
        cam_forward = self.camera.getQuat(self.render).getForward()
        ray_start = self.camera.getPos(self.render)
        ray_end = ray_start + cam_forward * 100
        
        # إنشاء شعاع للكشف عن الإصابة
        pickerRay = CollisionRay()
        pickerRay.setFromLens(self.camNode, 0, 0) # إطلاق الشعاع من مركز الشاشة
        
        pickerNode = CollisionNode('pickerRay')
        pickerNode.addSolid(pickerRay)
        pickerNode.setFromCollideMask(BitMask32.bit(2)) # قناع تصادم خاص للبوتات
        pickerNode.setIntoCollideMask(BitMask32.allOff())
        pickerNP = self.camera.attachNewNode(pickerNode)
        
        handler = CollisionHandlerQueue()
        temp_trav = CollisionTraverser('fireTrav')
        temp_trav.addCollider(pickerNP, handler)
        
        # جعل البوتات قابلة للاصطدام مع شعاع إطلاق النار
        for bot_data in self.bots:
            if bot_data["is_alive"]:
                bot_data["model"].find("**/+GeomNode").node().setIntoCollideMask(BitMask32.bit(2))
        
        temp_trav.traverse(self.render)
        pickerNP.removeNode()
        
        if handler.getNumEntries() > 0:
            handler.sortEntries()
            entry = handler.getEntry(0)
            hit_node_path = entry.getIntoNodePath()
            
            # البحث عن البوت الذي تم إصابته
            for bot_data in self.bots:
                if bot_data["is_alive"] and hit_node_path.isAncestorOf(bot_data["model"]):
                    damage = WEAPON_DAMAGE[self.current_weapon]
                    bot_data["health"] -= damage
                    if bot_data["health"] <= 0:
                        bot_data["is_alive"] = False
                        bot_data["model"].setColor(0.3, 0.3, 0.3)
                        bot_data["respawn_timer"] = 5
                        self.score += 10
                    break # تم العثور على البوت المصاب
        
        # إعادة قناع التصادم للبوتات إلى الوضع الافتراضي (إذا لزم الأمر)
        # for bot_data in self.bots:
        #     if bot_data["is_alive"]:
        #         bot_data["model"].find("**/+GeomNode").node().setIntoCollideMask(BitMask32.allOff())

    def toggle_scope(self):
        """تفعيل/إلغاء السكوب"""
        if self.camLens.getFov() == self.camLens.getDefaultFov():
            self.camLens.setFov(30) # تقريب الكاميرا (تغيير مجال الرؤية)
            self.crosshair.setScale(0.05)
        else:
            self.camLens.setFov(self.camLens.getDefaultFov()) # إعادة مجال الرؤية الافتراضي
            self.crosshair.setScale(0.07)
    
    def bot_fire(self, bot):
        """إطلاق النار من البوت"""
        distance = (self.player.getPos() - bot.getPos()).length()
        hit_chance = max(0.1, min(0.7, 1.0 - (distance / 25.0))) # تعديل طفيف في حساب الاحتمالية
        if random.random() < hit_chance:
            damage = random.randint(5, 10)
            self.health -= damage
            if self.health <= 0:
                self.player_death()
    
    def player_death(self):
        """موت اللاعب"""
        print("Player Died!") # رسالة للمطور
        self.health = 100
        x = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
        y = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
        self.player.setPos(x, y, 1)
        self.player_velocity = Vec3(0,0,0) # إيقاف حركة اللاعب عند الموت
        self.score = max(0, self.score - 5)
    
    def respawn_bot(self, bot_data):
        """إعادة إحياء البوت"""
        bot_data["is_alive"] = True
        bot_data["health"] = 100
        x = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
        y = random.uniform(-GROUND_SIZE/2 + 5, GROUND_SIZE/2 - 5)
        bot_data["model"].setPos(x, y, 1)
        bot_data["model"].setColor(0.8, 0.2, 0.2)

# تشغيل اللعبة
game = BattleRoyaleGame()
game.run()

