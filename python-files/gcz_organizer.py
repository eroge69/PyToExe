
import os
import shutil
import struct

def extract_game_id_from_gcz(file_path):
    with open(file_path, "rb") as f:
        f.seek(0)
        if f.read(4) != b'GCZ\x00':
            return None, None
        f.seek(0x10)
        header = f.read(6)
        game_id = header.decode('ascii', errors='ignore')
        return game_id, game_id[:4]

def main():
    input_dir = "I:/Temp/In"
    output_dir = "I:/Temp/Out"

    if not os.path.exists(input_dir):
        print(f"Eingabeordner {input_dir} wurde nicht gefunden.")
        return

    os.makedirs(output_dir, exist_ok=True)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(".gcz")]
    if not files:
        print("Keine .gcz-Dateien im Eingabeordner gefunden.")
        return

    for filename in files:
        src_path = os.path.join(input_dir, filename)
        game_id, short_id = extract_game_id_from_gcz(src_path)

        if not game_id:
            print(f"Ungültige GCZ-Datei: {filename}")
            continue

        folder_name = f"{filename.rsplit('.', 1)[0]} [{game_id}]"
        folder_path = os.path.join(output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        dst_path = os.path.join(folder_path, "game.gcz")
        shutil.copy2(src_path, dst_path)

        print(f"✔ {filename} → {folder_name}/game.gcz")

    print("\nAlle Dateien wurden erfolgreich umbenannt und verschoben.")

if __name__ == "__main__":
    main()
