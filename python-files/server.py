import subprocess
import keyboard

# Your NVIDIA Profile Inspector path
INSPECTOR_PATH = r"C:\Users\pepsi\OneDrive\Desktop\robloxfpsinside\NvidiaProfileInspector.exe"

# Roblox profile name
ROBLOX_PROFILE = "RobloxPlayerBeta.exe"

# NVIDIA Max Frame Rate settings
FPS_LIMIT_ON = "0x00F5AC45 = 350000"      # 35 FPS
FPS_LIMIT_OFF = "0x00F5AC45 = 0x00000000" # Unlimited FPS

def set_fps_limit(enable=True):
    fps_setting = FPS_LIMIT_ON if enable else FPS_LIMIT_OFF
    cmd = [
        INSPECTOR_PATH,
        "-setBaseProfile", ROBLOX_PROFILE,
        "-set", fps_setting
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"{'✅ Enabled' if enable else '❌ Disabled'} FPS cap for Roblox.")
    except subprocess.CalledProcessError as e:
        print("🚫 Failed to set FPS cap:", e)

print("\n🎮 Roblox FPS Toggle Script")
print("➡ Press [E] to ENABLE 35 FPS cap")
print("➡ Press [R] to REMOVE the FPS cap")
print("🛑 Press Ctrl+C to exit the script\n")

while True:
    if keyboard.is_pressed('e'):
        set_fps_limit(True)
        keyboard.wait('e')
    elif keyboard.is_pressed('r'):
        set_fps_limit(False)
        keyboard.wait('r')
