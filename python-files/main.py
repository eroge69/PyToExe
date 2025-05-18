import os
import fnmatch
import sys
import time

# Установка заголовка окна
sys.stdout.write("\x1b]2;Icysystem anticheat v2.5\x07")

# Список известных чит-клиентов и файлов с названием, похожим на читы
CHEAT_CLIENT_NAMES = [
    "Badlion", "Rise", "LiteLoader", "HackPack", "Impact", "NoCheatPlus",
    "Skidware", "Nova", "AutoClicker", "FlyHack", "ESP", "SpeedHack",
    "HitBoxEnlarger", "AntiKnockback", "Freecam", "KillAura", "Regen",
    "FastPlace", "GodMode", "Flight", "VelocityHack", "Nuke", "Minimap",
    "Radar", "Wallhack", "TriggerBot", "SilentAim", "DamageBoost",
    "SuperJump", "SuperSpeed", "XRay", "StepAssist", "InvEdit", "Scaffold",
    "ReconCraft", "Omnipotent", "Phase", "ItemPhysic", "Clip", "PortalGun",
    "GhostBlocks", "Swarm", "Vape", "CaveFinder", "Fullbright", "Freecam",
    "Crits", "Burrow", "LiquidInteract", "ProjectilePredict", "Invisibledamage",
    "SpiderClimb", "PingSpoofer", "ClickTP", "Breaker", "Bridge", "Spiderman",
    "BuildGod", "CombatGod", "Ghostly", "AntiAFK", "Disabler", "Reach",
    "AutoFish", "PathFinder", "ArrowBlock", "ArmorStand", "LegitGod",
    "LagSwitch", "TargetStrafe", "NoFall", "NoSlowdown", "FakeLag",
    "BlockOverlay", "LogRemover", "OverExtend", "HiveESP", "RotationResetter",
    "FreeCam", "SneakOn", "KillEffect", "Highwayman", "Skywalker", "Scout",
    "AutoRespawn", "Paralyzer", "FPSBooster", "MoveAssist", "InventoryCleaner",
    "ChunkEsp", "Crash", "Criticals", "Vanilla++", "Archer", "PortalTravel",
    "MorePackets", "AutoTool", "ChestStealer", "AntiVoid", "Hitmarker",
    "Projectiles", "SoundAlert", "FastLadder", "WorldBorder", "SpectatorGod",
    "Bouncer", "MobESP", "Teleporter", "Range", "SurvivalGod", "AutoPotato",
    "Baritone", "BattleGod", "ChunkSpy", "DeathCry", "DoubleTap", "Guardian",
    "Matrix", "MiniMap", "Morph", "Phantom", "Pixelmon", "Rainbow",
    "Revolver", "Shulkertap", "Smasher", "Spinner", "Tricks", "VeinMiner",
    "Warrior", "WaterWalk", "YPort", "Zoom", "Zulu", "Quiver", "AimLock",
    "HotbarSwapper", "AutoSoup", "BeamESP", "Blaze", "BloodESP", "BossESP",
    "BoneMeal", "Butterfly", "CameraESP", "Catfish", "ChainESP", "Chicken",
    "CircleESP", "Clarity", "ClickCounter", "CowESP", "CrosshairChanger",
    "DebugESP", "DimensionESP", "Disguiser", "DoorESP", "DurabilityESP",
    "EntityESP", "FarmESP", "FieldESP", "FireworkESP", "FlowerESP", "FoodESP",
    "FoxESP", "FriendESP", "GateESP", "GrassESP", "GravityESP", "HealESP",
    "HealthESP", "HopperESP", "IceESP", "IronESP", "LightningESP", "LocESP",
    "LootESP", "LoveESP", "MarkerESP", "MaturityESP", "MonsterESP",
    "MotionESP", "MultiShot", "MusicESP", "NightVision", "ParticleESP",
    "PauseESP", "PickupESP", "PortalESP", "PowerESP", "PumpkinESP",
    "RandomESP", "RedstoneESP", "RideESP", "RotatingESP", "RuneESP",
    "SandESP", "SearchESP", "SkeletonESP", "SlimeESP", "SnowESP",
    "SpawnESP", "SplitESP", "SpongeESP", "SpiderESP", "StarESP",
    "StoneESP", "SunflowerESP", "ThunderESP", "TimerESP", "TotemESP",
    "TrapESP", "TreeESP", "UnderwaterESP", "VillageESP", "WitchESP",
    "WitherESP", "WoodESP", "XPESP", "ZombieESP", "ZombieAttack"
]

# Функция для сканирования папки .minecraft
def scan_minecraft_folder(folder_path):
    found_cheat_clients = []
    total_items = sum(len(files) + len(dirs) for _, dirs, files in os.walk(folder_path))
    processed_items = 0

    print("Идет проверка...")

    for root, directories, filenames in os.walk(folder_path):
        for filename in filenames + directories:
            for cheat_name in CHEAT_CLIENT_NAMES:
                if fnmatch.fnmatch(filename.lower(), "*" + cheat_name.lower() + "*"):
                    found_cheat_clients.append(os.path.join(root, filename))
            processed_items += 1
            percent_complete = (processed_items / total_items) * 100
            print(f"{percent_complete:.2f}%", end='\r')

    return found_cheat_clients

# Главный сценарий
if __name__ == "__main__":
    folder_path = input("Введите путь к папке '.minecraft': ")

    if os.path.isdir(folder_path):
        detected_cheats = scan_minecraft_folder(folder_path)
        if detected_cheats:
            print("\nОбнаружены подозрительные файлы, похожие на чит-клиенты:")
            for cheat_client in detected_cheats:
                print(cheat_client)
        else:
            print("\nНет подозрительных файлов, похоже всё чисто.")
        print("\nicysystem.ru - лучшее решение для Minecraft")
    else:
        print("Указанная папка не найдена. Убедитесь, что ввели верный путь.")
while True:
    key = input("Хотите выйти? (yes/no)")
    if key.strip().lower() == "yes":
        break
