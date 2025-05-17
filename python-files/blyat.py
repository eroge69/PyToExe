import sys
import os

def convert_file(file_path):
    if file_path.endswith(".gd"):
        new_file = file_path[:-3] + "txt"
    elif file_path.endswith(".txt"):
        new_file = file_path[:-4] + "gd"
    else:
        print(f"Skipped: {file_path}")
        return

    try:
        os.replace(file_path, new_file)
        print(f"Renamed: {file_path} -> {new_file}")
    except Exception as e:
        print(f"Error renaming {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Drag and drop .gd or .txt files onto this script.")
    else:
        for file in sys.argv[1:]:
            convert_file(file)
