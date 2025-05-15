import os
import sys
import time
import random
import yt_dlp  # YouTube downloader library
import youtube_dl  # YouTube downloader library
import requests
import platform
import psutil
import paramiko  # SSH library
import getpass
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    print(Fore.CYAN + "Available functions:")
    print(Fore.YELLOW + "exit" + Fore.RESET + " - Exit the program")
    print(Fore.YELLOW + "help" + Fore.RESET + " - Show this help message")
    print(Fore.YELLOW + "clear" + Fore.RESET + " - Clear the console")
    print(Fore.YELLOW + "random" + Fore.RESET + " - Generate a random number")
    print(Fore.YELLOW + "time" + Fore.RESET + " - Show the current time")
    print(Fore.YELLOW + "cls" + Fore.RESET + " - Clear the console (alias for clear)")
    print(Fore.YELLOW + "su" + Fore.RESET + " - Show information about SU multi-tool")
    print(Fore.YELLOW + "speedup" + Fore.RESET + " - Remove temporary files and folders")
    print(Fore.YELLOW + "run" + Fore.RESET + " - Run a program (e.g., chrome, firefox, explorer)")
    print(Fore.YELLOW + "yt2mp3" + Fore.RESET + " - Convert YouTube video to MP3")
    print(Fore.YELLOW + "yt2mp4" + Fore.RESET + " - Convert YouTube video to MP4")
    print(Fore.YELLOW + "search" + Fore.RESET + " - Search for a file in a directory")
    print(Fore.YELLOW + "sysinfo" + Fore.RESET + " - Display system information (System Info)")  # 'sysinfo' is a custom command
    print(Fore.YELLOW + "calc" + Fore.RESET + " - Perform basic arithmetic operations")
    print(Fore.YELLOW + "ssh" + Fore.RESET + " - Connect to a server via SSH and run a command")  # <-- Added line
    print(Fore.YELLOW + "cmd" + Fore.RESET + " - Runs a CMD command inside of the su multitool")  # <-- Added line
    print(Fore.RED + "Note: Some functions may require administrative privileges.")
    
    
cmd_mode = False

def run_cmd():
    global cmd_mode
    while True:
        if not cmd_mode:
            command = input(Fore.YELLOW + "Enter the CMD command to run (or type 'cmd toggle' to enable CMD mode): ").strip()
            if command.lower() == "cmd toggle":
                cmd_mode = True
                print(Fore.GREEN + "CMD mode enabled. Type 'cmd toggle' again to disable.")
                continue
            elif command == "":
                break
            try:
                result = os.popen(command).read()
                print(Fore.GREEN + f"Output:\n{result}")
            except Exception as e:
                print(Fore.RED + f"Failed to run CMD command: {e}")
            break
        else:
            print(Fore.GREEN + "CMD mode is enabled. Type commands to run, or 'cmd toggle' to exit CMD mode.")
            while cmd_mode:
                command = input(Fore.YELLOW + "CMD> ").strip()
                if command.lower() == "cmd toggle":
                    cmd_mode = False
                    print(Fore.GREEN + "CMD mode disabled.")
                    break
                try:
                    result = os.popen(command).read()
                    print(Fore.GREEN + f"Output:\n{result}")
                except Exception as e:
                    print(Fore.RED + f"Failed to run CMD command: {e}")
            break

# In your main loop, add:


def ssh_connect():
    host = input(Fore.YELLOW + "Enter SSH host (e.g., 192.168.1.10): ").strip()
    port = input(Fore.YELLOW + "Enter SSH port (default 22): ").strip()
    port = int(port) if port else 22
    username = input(Fore.YELLOW + "Enter SSH username: ").strip()
    password = input(Fore.YELLOW + "Enter SSH password: ").strip()
    command = input(Fore.YELLOW + "Enter command to run on remote host: ").strip()
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        print(Fore.GREEN + "Output:")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(Fore.RED + "Error:")
            print(err)
        client.close()
    except Exception as e:
        print(Fore.RED + f"SSH connection failed: {e}")

# In your main loop, add:


def generate_random_number():
    print(Fore.GREEN + f"Random number: {random.randint(1, 100)}")

def show_current_time():
    print(Fore.GREEN + f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")


def search_file():
    directory = input(Fore.YELLOW + "Enter the directory to search in: ").strip()
    filename = input(Fore.YELLOW + "Enter the file name to search for: ").strip()
    try:
        for root, _, files in os.walk(directory):
            if filename in files:
                print(Fore.GREEN + f"File found: {os.path.join(root, filename)}")
                return
        print(Fore.RED + "File not found.")
    except Exception as e:
        print(Fore.RED + f"Error during file search: {e}")

def show_system_info():
    print(Fore.GREEN + f"System: {platform.system()} {platform.release()}")
    print(Fore.GREEN + f"Processor: {platform.processor()}")
    print(Fore.GREEN + f"CPU Cores: {psutil.cpu_count(logical=True)}")
    print(Fore.GREEN + f"Memory: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB")

def calculator():
    try:
        expression = input(Fore.YELLOW + "Enter a mathematical expression (e.g., 2 + 2): ").strip()
        result = eval(expression)
        print(Fore.GREEN + f"Result: {result}")
    except Exception as e:
        print(Fore.RED + f"Invalid expression: {e}")

clear_console()
print(Fore.MAGENTA + "Welcome to SU multi-tool!")
print(Fore.CYAN + "For help, type 'help' or 'h'")

while True:
    user_input = input(Fore.YELLOW + "Type the function name to run: ").strip().lower()
    
    if user_input in ["help", "h"]:
        show_help()
    elif user_input == "ssh":
        ssh_connect()
    elif user_input == "exit":
        print(Fore.RED + "Exiting the program. Goodbye!")
        sys.exit()
    elif user_input == "clear":
        clear_console()
    elif user_input == "random":
        generate_random_number()
    elif user_input == "time":
        show_current_time()
    elif user_input == "cls":
        clear_console()
    elif user_input == "su":
        print(Fore.BLUE + "SU is a powerful tool for system administration.")
    elif user_input == "speedup":
        temp_folder = os.getenv('TEMP')
        if temp_folder and os.path.exists(temp_folder):
            for root, dirs, files in os.walk(temp_folder, topdown=False):  # Traversing temp folder. 'topdown' is a parameter for os.walk.
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception as e:
                        print(Fore.RED + f"Failed to remove file {file}: {e}")
                for dir in dirs:
                    try:
                        os.rmdir(os.path.join(root, dir))
                    except Exception as e:
                        print(Fore.RED + f"Failed to remove directory {dir}: {e}")
            print(Fore.GREEN + "Temporary files and folders removed.")
        else:
            print(Fore.RED + "Temporary folder not found.")
    elif user_input == "run":
        program = input(Fore.YELLOW + "Enter the program name (e.g., chrome, firefox, explorer): ").strip().lower()
        try:
            os.system(program)
        except Exception as e:
            print(Fore.RED + f"Failed to run the program {program}: {e}")
    elif user_input == "yt2mp3":
        url = input(Fore.YELLOW + "Enter the YouTube video URL: ").strip()
        output_folder = input(Fore.YELLOW + "Enter the output folder path: ").strip()
        try:
            ydl_opts = {
                'format': 'bestaudio',  # Best audio quality. 'bestaudio' is a yt-dlp format option.
                'postprocessors': [{  # Post-processing options. 'postprocessors' is a yt-dlp configuration key.
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',  # Preferred codec for audio. 'preferredcodec' is a yt-dlp configuration key.
                    'preferredquality': '192',  # Preferred quality for audio. 'preferredquality' is a yt-dlp configuration key.
                }],
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),  # Output template. 'outtmpl' is a yt-dlp configuration key.
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(Fore.GREEN + "Download and conversion completed successfully.")
        except Exception as e:
            print(Fore.RED + f"Failed to convert YouTube video to MP3: {e}")
    elif user_input == "yt2mp4":
        url = input(Fore.YELLOW + "Enter the YouTube video URL: ").strip()
        output_folder = input(Fore.YELLOW + "Enter the output folder path: ").strip()
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio',  # Best video and audio quality. 'bestvideo' and 'bestaudio' are yt-dlp format options.
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(Fore.GREEN + "Download completed successfully.")
        except Exception as e:
            print(Fore.RED + f"Failed to convert YouTube video to MP4: {e}")
    elif user_input == "search":
        search_file()
    elif user_input == "sysinfo":  # System Info command. 'sysinfo' is a custom command.
        show_system_info()
    elif user_input == "calc":
        calculator()
    elif user_input == "cmd":
        run_cmd()
    else:
        print(Fore.RED + "Unknown command. Type 'help' or 'h' for a list of available commands.")
