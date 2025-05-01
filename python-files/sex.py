import os
import json

appdata_path = os.getenv('APPDATA')
target_dir = os.path.join(appdata_path, 'Nighty Selfbot')
os.makedirs(target_dir, exist_ok=True)

auth_data = {
    "license": "75iO8fltMM88m59-NIGHTY-esbeTfaN2KDHpHs"
}

auth_file_path = os.path.join(target_dir, 'auth.json')
with open(auth_file_path, 'w') as f:
    json.dump(auth_data, f, indent=2)


print("nighty sexcessfully cracked | @Kamerzystanasyt")