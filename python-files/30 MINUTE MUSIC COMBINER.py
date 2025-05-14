import os
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
import random
import datetime

def popup_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_paths_tuple = filedialog.askopenfilenames(
        title="Select Audio files",
        filetypes=(("Audio files", "*.mp3;*.wav;*.flac"), ("All files", "*.*"))
    )
    root.destroy()
    file_paths = list(file_paths_tuple)
    return file_paths

def get_durations(file_paths):
    durations = {}
    print("Calculating durations for each file, please wait...")
    for i, fp in enumerate(file_paths, start=1):
        audio = AudioSegment.from_file(fp)
        durations[fp] = len(audio) // 1000  # durasi dalam detik
        print(f"  [{i}/{len(file_paths)}] {os.path.basename(fp)} duration: {durations[fp]} seconds")
    return durations

def select_random_subset_by_duration(file_paths, durations_cache, min_duration_sec=1740, max_duration_sec=1860, max_attempts=1000):
    total_files = len(file_paths)

    for attempt in range(1, max_attempts + 1):
        subset_size = random.randint(1, total_files)
        selected_indices = random.sample(range(total_files), subset_size)
        total_duration = sum(durations_cache[file_paths[i]] for i in selected_indices)

        print(f"Attempt {attempt}: subset size={subset_size}, total duration={total_duration} seconds")

        if min_duration_sec <= total_duration <= max_duration_sec:
            print(f"Selected subset on attempt {attempt} with duration {total_duration} seconds")
            return [file_paths[i] for i in selected_indices]

    print(f"Warning: Tidak ditemukan subset dengan durasi antara {min_duration_sec} - {max_duration_sec} detik setelah {max_attempts} percobaan.")
    return []

def combine_audio(file_paths, output_dir, export_format="mp3"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    random.shuffle(file_paths)

    combined = AudioSegment.empty()
    track_info = []

    total_files = len(file_paths)
    for i, file_path in enumerate(file_paths, start=1):
        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".mp3":
            audio = AudioSegment.from_mp3(file_path)
        elif extension == ".wav":
            audio = AudioSegment.from_wav(file_path)
        elif extension == ".flac":
            audio = AudioSegment.from_file(file_path, format="flac")
        else:
            print(f"Unsupported format: {file_path}")
            continue

        audio = audio.fade_in(1000).fade_out(2000)  # fade in 1 detik, fade out 2 detik
        start_time = len(combined)
        combined += audio
        end_time = len(combined)
        track_info.append((start_time, end_time, os.path.basename(file_path)))

        print(f"Processing file {i}/{total_files}: {os.path.basename(file_path)}")

    output_file = os.path.join(output_dir, f"Combined Playlist.{export_format}")
    if os.path.exists(output_file):
        output_file = increment_filename(output_file)

    if export_format == "mp3":
        combined.export(output_file, format="mp3", bitrate="320k")
    elif export_format == "wav":
        combined.export(output_file, format="wav")

    print(f"Combined {export_format.upper()} saved to:", output_file)

    save_track_info(output_file, track_info, export_format)

def save_track_info(output_file, track_info, export_format):
    txt_output_file = output_file.replace(f".{export_format}", ".txt")
    with open(txt_output_file, "w") as txt_file:
        for start_time, _, filename in track_info:
            start_time_seconds = start_time // 1000
            start_time_str = str(datetime.timedelta(seconds=start_time_seconds))
            time_parts = start_time_str.split(':')
            if len(time_parts) == 2:
                start_time_str = "00:" + start_time_str
            elif len(time_parts) == 3:
                pass
            filename_without_extension = os.path.splitext(filename)[0]
            txt_file.write(f"{start_time_str} - {filename_without_extension}\n")
    print(f"Track info saved to: {txt_output_file}")

def increment_filename(filename):
    base, ext = os.path.splitext(filename)
    i = 1
    while os.path.exists(filename):
        filename = f"{base}_{i}{ext}"
        i += 1
    return filename

if __name__ == "__main__":
    all_file_paths = popup_file_dialog()
    if len(all_file_paths) == 0:
        print("No audio files selected.")
    else:
        durations_cache = get_durations(all_file_paths)
        selected_files = select_random_subset_by_duration(all_file_paths, durations_cache)
        if not selected_files:
            print("Failed to select subset with desired total duration.")
        else:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            choice = input("Choose export format: 1 = mp3, 2 = wav (default 1): ").strip()
            if choice == "2":
                export_format = "wav"
            else:
                export_format = "mp3"
            combine_audio(selected_files, output_dir, export_format)
