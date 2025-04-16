from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties, Vec3, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, BitMask32
from panda3d.core import AmbientLight, DirectionalLight, Texture, TextureStage
import sys
import random

class FPSGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Disable default mouse camera control
        self.disableMouse()
        
        # Set window properties
        props = WindowProperties()
        props.setTitle("Simple FPS Game")
        self.win.requestProperties(props)
        
        # Camera setup
        self.camera.setPos(0, 0, 1.6)  # Eye level
        self.camLens.setFov(75)
        
        # Movement variables
        self.moveSpeed = 10
        self.mouseSensitivity = 0.2
        self.velocity = Vec3(0, 0, 0)
        self.gravity = -20
        self.canJump = True
        
        # Score
        self.score = 0
        self.scoreText = self.aspect2d.attachNewNode(
            self.makeText(0, 0.9, f"Score: {self.score}", 0.05)
        )
        
        # Mouse setup
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
        self.mouseWatcherNode.setGeometry(None)  # Prevent mouse clicks from affecting game
        
        # Setup scene
        self.setupScene()
        self.setupWeapon()
        self.setupEnemies()
        self.setupCollisions()
        
        # Input bindings
        self.accept("w", self.setKey, ["forward", True])
        self.accept("w-up", self.setKey, ["forward", False])
        self.accept("s", self.setKey, ["backward", True])
        self.accept("s-up", self.setKey, ["backward", False])
        self.accept("a", self.setKey, ["left", True])
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])
        self.accept("space", self.jump)
        self.accept("mouse1", self.shoot)
        
        # Tasks
        self.taskMgr.add(self.update, "update")
        self.taskMgr.add(self.updateCamera, "updateCamera")
        
        # Keyboard state
        self.keys = {"forward": False, "backward": False, "left": False, "right": False}
        
    def makeText(self, x, y, text, scale):
        from panda3d.core import TextNode
        tn = TextNode("text")
        tn.setText(text)
        tn.setTextColor(1, 1, 1, 1)
        tn.setAlign(TextNode.A_center)
        np = self.aspect2d.attachNewNode(tn)
        np.setScale(scale)
        np.setPos(x, 0, y)
        return tn
    
    def setupScene(self):
        # Ground
        ground = self.loader.loadModel("models/box")
        ground.setScale(100, 100, 0.1)
        ground.setPos(0, 0, 0)
        tex = self.loader.loadTexture("textures/ground.jpg")
        ground.setTexture(tex, 1)
        ground.reparentTo(self.render)
        
        # Walls
        self.walls = []
        wall_model = self.loader.loadModel("models/box")
        tex = self.loader.loadTexture("textures/wall.jpg")
        for i in range(5):
            wall = wall_model.copyTo(self.render)
            wall.setScale(2, 2, 2)
            wall.setPos(random.uniform(-25, 25), random.uniform(-25, 25), 1)
            wall.setTexture(tex, 1)
            self.walls.append(wall)
        
        # Lighting
        alight = AmbientLight("ambient")
        alight.setColor((0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight("directional")
        dlight.setColor((0.7, 0.7, 0.7, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
    
    def setupWeapon(self):
        # Simple AK-47 representation (cube for now)
        self.weapon = self.loader.loadModel("models/box")
        self.weapon.setScale(0.3, 0.5, 0.1)
        self.weapon.setPos(0.5, -0.5, -0.5)  # Position in front of camera
        tex = self.loader.loadTexture("textures/ak47.jpg")
        self.weapon.setTexture(tex, 1)
        self.weapon.reparentTo(self.camera)
    
    def setupEnemies(self):
        self.enemies = []
        enemy_model = self.loader.loadModel("models/box")
        tex = self.loader.loadTexture("textures/enemy.jpg")
        for i in range(10):
            enemy = enemy_model.copyTo(self.render)
            enemy.setScale(1, 1, 1)
            enemy.setPos(random.uniform(-25, 25), random.uniform(-25, 25), 0.5)
            enemy.setTexture(tex, 1)
            enemy.setTag("enemy", str(i))
            self.enemies.append(enemy)
    
    def setupCollisions(self):
        self.cTrav = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        
        # Ray for shooting
        self.shootRay = CollisionRay()
        self.shootRay.setOrigin(0, 0, 0)
        self.shootRay.setDirection(0, 1, 0)
        cnode = CollisionNode("shootRay")
        cnode.addSolid(self.shootRay)
        cnode.setFromCollideMask(BitMask32.bit(1))
        cnode.setIntoCollideMask(BitMask32.allOff())
        self.shootRayNP = self.camera.attachNewNode(cnode)
        self.cTrav.addCollider(self.shootRayNP, self.queue)
        
        # Set collision masks for enemies
        for enemy in self.enemies:
            enemy.node().setIntoCollideMask(BitMask32.bit(1))
    
    def setKey(self, key, value):
        self.keys[key] = value
    
    def jump(self):
        if self.canJump:
            self.velocity.z = 8
            self.canJump = False
    
    def shoot(self):
        self.cTrav.traverse(self.render)
        for entry in self.queue.getEntries():
            if entry.getIntoNodePath().hasTag("enemy"):
                enemy_np = entry.getIntoNodePath()
                enemy_np.removeNode()
                self.enemies.remove(enemy_np)
                self.score += 10
                self.scoreText.setText(f"Score: {self.score}")
                break
    
    def update(self, task):
        dt = globalClock.getDt()
        
        # Movement
        velocity = Vec3(0, 0, self.velocity.z)
        if self.keys["forward"]:
            velocity.y += self.moveSpeed
        if self.keys["backward"]:
            velocity.y -= self.moveSpeed
        if self.keys["left"]:
            velocity.x -= self.moveSpeed
        if self.keys["right"]:
            velocity.x += self.moveSpeed
        
        # Rotate velocity based on camera heading
        h = self.camera.getH()
        velocity_rot = Vec3(
            velocity.x * math.cos(math.radians(h)) + velocity.y * math.sin(math.radians(h)),
            -velocity.x * math.sin(math.radians(h)) + velocity.y * math.cos(math.radians(h)),
            velocity.z
        )
        
        # Apply gravity
        velocity_rot.z += self.gravity * dt
        self.velocity = velocity_rot
        
        # Update position
        self.camera.setPos(self.camera.getPos() + velocity_rot * dt)
        
        # Ground collision
        if self.camera.getZ() < 1.6:
            self.camera.setZ(1.6)
            self.velocity.z = 0
            self.canJump = True
        
        return Task.cont
    
    def updateCamera(self, task):
        if self.win.getProperties().getMouseMode() == WindowProperties.M_relative:
            md = self.win.getPointer(0)
            dx = md.getX()
            dy = md.getY()
            if dx or dy:
                h = self.camera.getH() - dx * self.mouseSensitivity
                p = self.camera.getP() - dy * self.mouseSensitivity
                p = max(min(p, 90), -90)
                self.camera.setHpr(h, p, 0)
                self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)
        return Task.cont

if __name__ == "__main__":
    import math
    game = FPSGame()
    game.run()