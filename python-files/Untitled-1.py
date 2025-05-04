
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "ursina"], check=True)
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import uniform

import ursina
import json
app = Ursina()
player = FirstPersonController()
x = 15
y = 4
z = 15
textures_path = ursina.__file__.replace("__init__.py", "textures")
label = Text(text="Block Choosen: Grass", color=color.white, scale=2, position = (0.2, 0.3))
saved_message = Text(text="", color=color.green, position=(0, 0.3))
label2 = Text(text="Health: null", color=color.white, scale=2, position = (0.2, 0.5))
label3 = Text(text="map1: load = c, save = t | map2: load = n, save = p| map3: load = l, save = k ", color=color.white, scale=2, position = (-0.5, 0.4))
label4 = Text(text="Map Name: Empty", color=color.white, scale=2, position = (-0.3, 0.5))


label3.scale_x = 1  # Makes text wider
label3.scale_y = 1

user_folder = os.path.expanduser("~")
save_folder = os.path.join(user_folder, "GameSaves") 
os.makedirs(save_folder, exist_ok=True)
file_path = os.path.join(save_folder, "saved_map.json")
file_path2 = os.path.join(save_folder, "saved_map2.json")
file_path3 = os.path.join(save_folder, "saved_map3.json")
script_dir = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(script_dir, "data")
steve_hand = Entity(model="cube", scale=(0.3, 1, 0.2), parent=camera)
steve_hand.position = Vec3(0.5, -0.5, 1)
print(player.scale)
steve_hand.rotation = Vec3(0, 10, -10)
mouse.sensitivity = Vec2(2, 2)
#print("File exists:", os.path.exists(tntsounds))
tntsound = Audio("explosion.ogg", autoplay=False, volume=1.5)
player.jump_height = 1
player.camera_pivot.y = 1.8
yForSpawn = 0
switch = False
velocity = 0
block = "grass"
position = Vec3(0, 1, 0)
spawner = Entity(model="cube", position=position, color=color.blue, scale=(0.5, 0.5, 0.5), origin_y=0.5)
isChange = False
health = 100
countdown = 11
isJump = False
Sky()
canEdit = True
isDead = False
hit_info = (0,0,0)
hit_info2 = (0, 0, 0)
boxes = []
tnts = []
heightLimit = []
boxestoremove = []
loaded_boxes = []
boxes_data = []

hit_info = raycast(camera.position, camera.forward, distance=5, ignore=[player])
def highlight_box(box2):
    box2.color = color.rgba(0, 255, 0, 1)   # Change color to indicate selection

def remove_highlight(box2):
    box2.color = color.white  # Reset color when not selected


def build():
    for x2 in range(x):
        for z2 in range(z):
            for y2 in range(y):
                box = Entity(color=color.white, model='cube', position=(x2,-y2,z2), texture= "grass.png", parent=scene, origin_y=0.5,collider="box")
                box.name = "block"
                boxes.append(box)
    for x2 in range(x):
        for z2 in range(z):
            for y2 in range(y):
                if x2 != 0:
                    box = Entity(color=color.white, model='cube', position=(-x2,-y2,-z2), texture= "grass.png", parent=scene, origin_y=0.5, collider="box")
                    box.name = "block"
                    boxes.append(box)
                       
    for x2 in range(x):
        for z2 in range(z):
            for y2 in range(y):
                if x2 != 0 and z2 != 0:
                    box = Entity(color=color.white, model='cube', position=(-x2,-y2,z2), texture= "grass.png", parent=scene, origin_y=0.5,collider="box")
                    box.name = "block"
                    boxes.append(box)

    for x2 in range(x):
        for z2 in range(z):
            for y2 in range(y):
                if z2 != 0:
                    box = Entity(color=color.white, model='cube', position=(x2,-y2,-z2), texture= "grass.png", parent=scene, origin_y=0.5,collider="box")
                    box.name = "block"
                    boxes.append(box) 
def swing_hand():
    steve_hand.animate_rotation(Vec3(30, 10, -10), duration=0.1, curve=curve.linear)
    invoke(reset_hand, delay=0.2)  # Reset after animation

def reset_hand():
    steve_hand.rotation = Vec3(0, 10, -10)
def savedInfo():
    saved_message.text = ""
                
def respawn():
    global yForSpawn
    global health
    global position
    global isDead
    camera.position = Vec3(0, 0, 0)  # Default position
    camera.rotation = Vec3(0, 0, 0)  # Default rotation
    isDead = False
    player.speed = 5
    player.camera_pivot.y = 1.8
    #player.speed = 
    yForSpawn = 0
    health = 100
    reference_box = None
    for box in boxes:
        if box.position.x == position.x and box.position.z == position.z:
            heightLimit.append(box)
    for limiter in heightLimit:
        if yForSpawn < limiter.y:
            yForSpawn = limiter.y
            reference_box = limiter
    heightLimit.clear()

    if reference_box is not None:
        player.position = Vec3(position.x, yForSpawn , position.z)
    else:
        player.position = Vec3(position.x, yForSpawn , position.z)
def changeColor():
    global isChange
    global switch
    for tnt in tnts:
        if isChange == False:
            tnt.color = color.rgb(255,255,255)
            isChange = True
        else:
            tnt.color = color.rgb(255,0,0)
            isChange = False
    if switch == True:
        invoke(changeColor, delay = 0.2)  
def unlockEdit():
    global canEdit
    canEdit = True

def animateSpawner():
    spawner.animate_rotation(Vec3(0, spawner.rotation.y + 360, 0), duration=2, curve=curve.linear)
    invoke(animateSpawner, delay=2)
animateSpawner()
def update():
    global countdown
    global velocity
    global switch
    global health
    global position
    global yForSpawn
    global label2
    global hit_info
    global hit_info2
    global isDead
    spawner.position = Vec3(spawner.position.x, yForSpawn + 1, spawner.position.z)
    yForSpawn = 0
    for box in boxes:
        if box.position.x == position.x and box.position.z == position.z:
            heightLimit.append(box)
    for limiter in heightLimit:
        if yForSpawn < limiter.y:
            yForSpawn = limiter.y
            reference_box = limiter
    heightLimit.clear()
    position = spawner.position
    if time.dt < 0.016:
        return
    for box in boxes:
        if box.enabled and not box.visible:
            box.enabled = False
    label2.text = "Health: " + str(health)
    hit_info = raycast(player.position+ Vec3(0, player.height, 0), direction=(0,1,0), distance=1, ignore=[player], debug=False)
    hit_info2 = raycast(player.position+ Vec3(0, 0.1, 0), direction=(0,1,0), distance=1, ignore=[player], debug=False)
    for box in boxes:
        if box.hovered:
            highlight_box(box)
        else:
            remove_highlight(box)
    

    if hit_info.hit and isDead == False:
        player.jump_height = 0
    else:
        if isDead == False:
            player.jump_height = 1
        
    if hit_info2.hit and hit_info.hit:
        if hit_info.entity == hit_info2.entity and isDead == False and len(hit_info2.entities) <= 1:
            player.position -= Vec3(0, 1, 0)
        elif len(hit_info2.entities) > 1 and isDead == False:
            health -= 1
        if hit_info.entity != hit_info2.entity and isDead == False and len(hit_info2.entities) <= 1:
            health -= 1
        
        
    
    if health <= 0 and isDead == False:
        camera.animate_position(camera.position + Vec3(0, -1.5, 0), duration=1, curve=curve.in_out_quad)
        camera.animate_rotation(Vec3(0, 0, 90), duration=1, curve=curve.in_out_back)  # Head tilting while falling
        player.speed = 0
        player.jump_height = 0
        invoke(respawn, delay=5)
        isDead = True
    if countdown > 0 and countdown != 11:
        countdown -= time.dt
        if switch == False:
            invoke(changeColor, delay = 0.2)
            switch = True
        
            
    else:
        if countdown != 11:
            tntsound.play()
            for box in boxes:
                if len(tnts) > 0:
                    for tnt in tnts[:]:
                        if (box.position - tnt.position).length() < 3:
                            
                            boxestoremove.append(box)

            if len(tnts) > 0:                
                for tnt in tnts[:]:
                    if (player.position - tnt.position).length() < 6:
                        if health > 0:
                            health -= 25
                            if health > 0:
                                player.animate_position(player.position + (Vec3(player.position.x, player.position.y + 6, player.position.z) - tnt.position).normalized() * 3, duration=0.5, curve=curve.in_out_back)
                            
                            
                        
                    tnts.remove(tnt)
                    destroy(tnt)
                    
            if len(boxestoremove) > 0:
                for boxer in boxestoremove[:]:
                    boxestoremove.remove(boxer)
                    boxes.remove(boxer)
                    boxer.animate_position(boxer.position + Vec3(uniform(-0.2, 0.2), uniform(-0.2, 0.2), uniform(-0.2, 0.2)), duration=0.2)
                    invoke(destroy, boxer, delay=0.4)
                boxestoremove.clear()  
            
              
            switch = False
            countdown = 11        
              
    for tnt in tnts:
        if countdown == 11:
            velocity = 0
        
        if tnt.y > -y and not tnt.intersects().hit:  # Stop falling at ground level
            velocity -= 0.5  # Simulate gravity
            tnt.y += velocity * time.dt  # Apply velocity
        else:
            velocity = 1  # Adjusted for box scale
            tnt.y += velocity * time.dt  # Moves up just 1 unit
    if player.y < -y:
        respawn()
    if len(boxes) <= 0:
        build()
def save_map(path, name):
    global boxes_data
    global position
    global label4
    did = False
    boxes_data = [{"x": box.position.x, "y": box.position.y, "z" : box.position.z, "texture": box.texture.name} for box in boxes]
    point = Vec3(0, 0, 0)
    
    for box in boxes:
        if box.hovered:
            did = True
            point = Vec3(box.position.x, box.position.y + 1, box.position.z)
    if did == False:
        saved_message.color = color.red
        saved_message.text = "Hover on a block."
        invoke(savedInfo, delay=3)
        invoke(unlockEdit, delay=3)
        return
    player_data = {
        "x": round(point.x, 2),
        "y": round(point.y, 2),
        "z": round(point.z, 2)
    }
    spawner.position = point
    position = spawner.position

    map_data = {
        "boxes": boxes_data,   # Stores all block positions
        "spawn_point": player_data  # Saves player's spawn location with "Spawn" label
    }
    label4.text = "Map Name: " + name
        # Save to a file
    with open(path, "w") as file:
        json.dump(map_data, file)  
    boxes_data.clear()
    saved_message.color = color.green
    saved_message.text = "Saved Map!"
    invoke(savedInfo, delay=3)
    invoke(unlockEdit, delay=3)       
def load_map(path, name):
    global position
    global loaded_boxes
    global boxes
    global label4
    if not os.path.exists(path):
        saved_message.color = color.red
        saved_message.text = "File Not Found."
        invoke(savedInfo, delay=3)
        invoke(unlockEdit, delay=3)
        return
    label4.text = "Map Name: " + name
    saved_message.color = color.green
    saved_message.text = "Loaded Map!"
    for box2 in boxes[:]:
        boxes.remove(box2)
        destroy(box2)
    with open(path, "r") as file:
        loaded_boxes = json.load(file)
    
    if "boxes" in loaded_boxes:
        # Create boxes from saved data
        for data in loaded_boxes["boxes"]:
            new = Entity(model="cube", position=(data["x"], data["y"], data["z"]), texture=data["texture"], collider="box", parent=scene, color=color.white, origin_y = 0.5)
            new.name = "block"
            boxes.append(new)
        if "spawn_point" in loaded_boxes:
            spawner.position = Vec3(loaded_boxes["spawn_point"]["x"], loaded_boxes["spawn_point"]["y"], loaded_boxes["spawn_point"]["z"])
            position = spawner.position
    else:
        for data in loaded_boxes:
            new = Entity(model="cube", position=(data["x"], data["y"], data["z"]), texture=data["texture"], collider="box", parent=scene, color=color.white, origin_y = 0.5)
            new.name = "block"
            boxes.append(new)
        spawner.position = Vec3(0, 1, 0)
        position = spawner.position
    loaded_boxes.clear()
    invoke(savedInfo, delay=3)
    invoke(unlockEdit, delay=3)    
    respawn()  
      



def input(key):
    global block
    global label
    global countdown
    global canEdit
    global isJump
    
    if key == "space":
        isJump = True
    if key == "r" or key == "R" :
        if block == "grass":
            block = "brick"
            label.text = "Block Choosen: Brick"
        else:
            block = "grass"    
            label.text = "Block Choosen: Grass"
    if key == "m" and countdown == 11 and isDead == False : #
        box = Entity(model='cube', color=color.red, collider='box', position=player.position + (0, 5, 0))  
        box.animate_scale(box.scale * 1.5, duration=2, curve=curve.in_out_bounce)
        tnts.append(box)
        countdown = 2
    if key == "o":
        label4.text = "Map Name: Empty"
        for box2 in boxes[:]:
            boxes.remove(box2)
            destroy(box2)
        build()
        respawn()
    if key == "t" and canEdit:
        canEdit = False
        save_map(file_path, "World1")
    if key == "p" and canEdit:
        canEdit = False
        save_map(file_path2, "World2")
    if key == "k" and canEdit:
        canEdit = False
        save_map(file_path3, "World3")
    if key == 'escape':
        application.quit()
    if key == "f":
        window.fullscreen = not window.fullscreen 
       
    if key == "c" and canEdit:
        canEdit = False
        load_map(file_path, "World1")
    if key == "n" and canEdit:
        canEdit = False
        load_map(file_path2, "World2")
    if key == "l" and canEdit:
        canEdit = False
        load_map(file_path3, "World3")
    if len(boxes) > 0:
        for box in boxes: 
            if key == "right mouse down" or key == "left mouse down":
                if not isinstance(box, dict) and box.hovered:
                    if key == "right mouse down" and isDead == False and (player.position - box.position).length() < 8 and (player.position - box.position).length() > 0.5:
                        swing_hand()
                        if block == "brick":
                            new = Entity(color=color.white, model='cube', position=box.position + mouse.normal, texture= "brick.png", parent=scene, origin_y=0.5, collider="box") 
                            new.name = "blocknew"       
                            boxes.append(new)
                        else:
                            new = Entity(color=color.white, model='cube', position=box.position + mouse.normal, texture= "grass.png", parent=scene, origin_y=0.5, collider="box")        
                            new.name = "blocknew"
                            boxes.append(new)
                    if key == "left mouse down" and isDead == False and (player.position - box.position).length() < 8:    
                        swing_hand()
                        boxes.remove(box)
                        destroy(box) 
              
            
build()
app.run()