
import os
import string
from pathlib import Path

MOVIE_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
DESKTOP_PATH = Path("C:/Users/shahab/Desktop")
OUTPUT_FILENAME = 'لیست فیلم‌ها.txt'
OUTPUT_FILE = DESKTOP_PATH / OUTPUT_FILENAME

# Load previous data if available
previous_data = {}
if OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        current_drive = None
        for line in f:
            line = line.strip()
            if line.startswith("درایو"):
                current_drive = line.split()[1].strip(':')
                previous_data[current_drive] = []
            elif current_drive:
                previous_data[current_drive].append(line)

# Function to scan a drive for video files
def scan_drive(drive_letter):
    movie_list = []
    for root, _, files in os.walk(f"{drive_letter}:/", topdown=True):
        for file in files:
            if any(file.lower().endswith(ext) for ext in MOVIE_EXTENSIONS):
                clean_name = file.replace('.', ' ')
                movie_list.append(clean_name)
    return movie_list

# Scan all drives except C
updated_data = previous_data.copy()
for letter in string.ascii_uppercase:
    if letter == 'C':
        continue
    drive_path = f"{letter}:/"
    if os.path.exists(drive_path):
        movies = scan_drive(letter)
        if movies:
            updated_data[letter] = sorted(set(movies))

# Save to output file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for drive, movies in updated_data.items():
        f.write(f"درایو {drive}:\n")
        for movie in movies:
            f.write(f"  {movie}\n")
        f.write("\n")
print("لیست فیلم‌ها با موفقیت روی دسکتاپ ذخیره شد.")
input("برای بستن برنامه Enter را بزنید...")
