import os
import sys
import shutil
import subprocess
import urllib.request
import tempfile
import time
import ctypes

def show_credits():
    print("=" * 60)
    print("RobloxLoader Portable v2.0.0")
    print("Developed by: JulianNizah")
    print("Special thanks to: Contributors and Supporters")
    print("=" * 60)
    print()

def allocate_console():
    if ctypes.windll.kernel32.GetConsoleWindow() == 0:
        ctypes.windll.kernel32.AllocConsole()
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)
        sys.stderr = open("CONOUT$", "w", encoding="utf-8", buffering=1)
        sys.stdin = open("CONIN$", "r", encoding="utf-8", buffering=1)

def initialize():
    print("Initializing RobloxLoader Portable...")
    local_appdata = os.getenv('LOCALAPPDATA')
    base_portable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roblox")
    roblox_folder_map = {
        os.path.join(local_appdata, "Roblox"): os.path.join(base_portable_path, "AppDataLocalRoblox"),
        r"C:\\Program Files (x86)\\Roblox": os.path.join(base_portable_path, "ProgramFilesx86Roblox"),
        r"C:\\ProgramData\\Roblox": os.path.join(base_portable_path, "ProgramDataRoblox")
    }
    for system_path, portable_path in roblox_folder_map.items():
        try:
            if not os.path.exists(portable_path):
                os.makedirs(portable_path)
                print("[+] Created portable folder")
            if os.path.exists(system_path):
                if os.path.islink(system_path):
                    os.unlink(system_path)
                    print("[+] Removed existing symbolic link")
                elif os.path.isdir(system_path):
                    shutil.rmtree(system_path)
                    print("[+] Removed existing directory")
                else:
                    print("[-] Path exists but is not a link or directory")
            os.symlink(portable_path, system_path, target_is_directory=True)
            print("[+] Created symbolic link")
        except Exception as e:
            print(f"[x] Error linking: {e}")
    portable_roblox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roblox")
    reg_folder_path = os.path.join(portable_roblox_path, "Reg")
    if not os.path.exists(portable_roblox_path):
        os.makedirs(portable_roblox_path)
        print("[+] Created portable Roblox folder")
    if not os.path.exists(reg_folder_path):
        os.makedirs(reg_folder_path)
        print("[+] Created Reg folder")
    reg_files = [
        os.path.join(reg_folder_path, "roblox.reg"),
        os.path.join(reg_folder_path, "roblox_corp.reg"),
        os.path.join(reg_folder_path, "roblox_player.reg"),
        os.path.join(reg_folder_path, "roblox_studio.reg")
    ]
    for reg_file in reg_files:
        if os.path.exists(reg_file):
            try:
                subprocess.run(["reg", "import", reg_file], check=True)
                print("[+] Imported registry file")
            except subprocess.CalledProcessError as e:
                print(f"[x] Failed to import registry file: {e}")
        else:
            print("[-] Registry file not found")

def kill_roblox_processes():
    processes = ["RobloxPlayerBeta.exe", "RobloxStudioBeta.exe"]
    for proc in processes:
        try:
            subprocess.run(["taskkill", "/F", "/IM", proc], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[+] Killed process: {proc}")
        except subprocess.CalledProcessError:
            print(f"[-] Process not running or failed to kill: {proc}")

def move_folder_with_progress(src, dst):
    total_size = 0
    for root, dirs, files in os.walk(src):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
            except Exception:
                pass
    moved_size = 0
    bar_length = 40
    if os.path.exists(dst):
        shutil.rmtree(dst)
        print("[+] Removed existing portable folder")
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, rel_path)
        os.makedirs(dest_dir, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dest_file = os.path.join(dest_dir, f)
            try:
                shutil.move(src_file, dest_file)
                moved_size += os.path.getsize(dest_file)
                percent = moved_size / total_size if total_size > 0 else 1
                block = int(round(bar_length * percent))
                text = f"\r[=] Moving: [{'#' * block + '-' * (bar_length - block)}] {percent*100:.2f}%"
                print(text, end='', flush=True)
            except Exception as e:
                print(f"\n[x] Error moving file: {e}")
    print()
    for root, dirs, files in os.walk(src, topdown=False):
        try:
            os.rmdir(root)
        except Exception:
            pass
    try:
        os.rmdir(src)
    except Exception:
        pass

def download_roblox():
    print("[=] Starting Roblox download...")
    roblox_installer_url = "https://www.roblox.com/id/download/client?os=win"
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".exe")
        os.close(fd)
        print(f"[=] Downloading Roblox installer from {roblox_installer_url}...")
        response = urllib.request.urlopen(roblox_installer_url)
        total_size = int(response.getheader('Content-Length').strip())
        bytes_so_far = 0
        start_time = time.time()
        with open(tmp_path, 'wb') as out_file:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                out_file.write(chunk)
                bytes_so_far += len(chunk)
                elapsed = time.time() - start_time
                speed = bytes_so_far / 1024 / 1024 / elapsed if elapsed > 0 else 0
                percent = float(bytes_so_far) / total_size
                bar_length = 40
                block = int(round(bar_length * percent))
                text = f"\r[=] Downloading: [{'#' * block + '-' * (bar_length - block)}] {percent*100:.2f}% {speed:.2f} MB/s"
                print(text, end='', flush=True)
        print()
        print("[=] Downloaded Roblox installer")
        print("[=] Running Roblox installer...")
        proc = subprocess.Popen([tmp_path])
        proc.wait()
        print("[+] Roblox installer finished.")
    except Exception as e:
        print(f"[x] Failed to download or run Roblox installer: {e}")
        return
    print("[+] Roblox download and installation completed.")
    local_appdata = os.getenv('LOCALAPPDATA')
    original_folders = {
        os.path.join(local_appdata, "Roblox"),
        r"C:\\Program Files (x86)\\Roblox",
        r"C:\\ProgramData\\Roblox"
    }
    base_portable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roblox")
    roblox_folder_map = {
        os.path.join(local_appdata, "Roblox"): os.path.join(base_portable_path, "AppDataLocalRoblox"),
        r"C:\\Program Files (x86)\\Roblox": os.path.join(base_portable_path, "ProgramFilesx86Roblox"),
        r"C:\\ProgramData\\Roblox": os.path.join(base_portable_path, "ProgramDataRoblox")
    }
    kill_roblox_processes()
    for original_path, portable_path in roblox_folder_map.items():
        if os.path.exists(original_path):
            move_folder_with_progress(original_path, portable_path)
        else:
            print("[-] Original folder does not exist")

def cleanup():
    print("[=] Starting cleanup of Roblox folders and registry keys...")
    local_appdata = os.getenv('LOCALAPPDATA')
    system_folders = [
        os.path.join(local_appdata, "Roblox"),
        r"C:\Program Files (x86)\Roblox",
        r"C:\ProgramData\Roblox"
    ]
    for folder in system_folders:
        try:
            if os.path.exists(folder):
                if os.path.islink(folder):
                    os.unlink(folder)
                    print("[+] Removed symbolic link")
                elif os.path.isdir(folder):
                    shutil.rmtree(folder)
                    print("[+] Deleted folder")
                else:
                    print("[-] Path exists but is not a directory or symbolic link")
            else:
                print("[-] Folder not found, skipping")
        except Exception as e:
            print(f"[x] Error deleting folder: {e}")
    registry_keys = [
        r"HKCR\ROBLOX",
        r"HKLM\SOFTWARE\WOW6432Node\ROBLOX Corporation",
        r"HKCR\roblox-player",
        r"HKCR\roblox-studio"
    ]
    for key in registry_keys:
        try:
            check = subprocess.run(["reg", "query", key], capture_output=True, text=True)
            if check.returncode != 0:
                print("[-] Registry key not found, skipping")
                continue
            subprocess.run(["reg", "delete", key, "/f"], check=True)
            print("[+] Deleted registry key")
        except subprocess.CalledProcessError as e:
            print(f"[x] Failed to delete registry key: {e}")

def get_roblox_install_path():
    """
    Get Roblox install path and version from registry, compatible with all users.
    Returns (versions_base_path, current_version) or (None, None) if not found.
    """
    try:
        # Query both possible registry locations for Roblox Player
        reg_keys = [
            r'HKLM\SOFTWARE\WOW6432Node\ROBLOX Corporation\Environments\roblox-player',
            r'HKCU\SOFTWARE\ROBLOX Corporation\Environments\roblox-player'
        ]
        version = None
        client_exe = None
        for reg_key in reg_keys:
            reg_query = f'reg query "{reg_key}"'
            result = subprocess.run(reg_query, capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                continue
            output = result.stdout
            for line in output.splitlines():
                line = line.strip()
                if line.lower().startswith("version"):
                    parts = line.split()
                    if len(parts) >= 3:
                        version = parts[-1].strip()
                elif line.lower().startswith("clientexe"):
                    parts = line.split()
                    if len(parts) >= 3:
                        client_exe = parts[-1].strip()
            if version or client_exe:
                break

        # Try to infer the base path from client_exe if possible
        base_path = None
        if client_exe and os.path.exists(client_exe):
            # Example: C:\Program Files (x86)\Roblox\Versions\version-xxxx\RobloxPlayerBeta.exe
            versions_dir = os.path.dirname(os.path.dirname(client_exe))
            base_path = os.path.dirname(versions_dir)
            version_folder = os.path.basename(versions_dir)
            if not version:
                version = version_folder
            return base_path, version
        # Fallback to default path if version found
        if version:
            base_path = r"C:\Program Files (x86)\Roblox\Versions"
            if os.path.exists(os.path.join(base_path, version)):
                return base_path, version
    except Exception as e:
        print(f"Error querying registry for Roblox install path: {e}")
    return None, None

def delete_roblox_user_cache():
    local_appdata = os.getenv('LOCALAPPDATA')
    if not local_appdata:
        print("[x] Could not determine LOCALAPPDATA environment variable.")
        return
    cache_path = os.path.join(local_appdata, "Roblox", "LocalStorage")
    if os.path.exists(cache_path):
        try:
            for entry in os.listdir(cache_path):
                entry_path = os.path.join(cache_path, entry)
                if os.path.isfile(entry_path) or os.path.islink(entry_path):
                    os.unlink(entry_path)
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
            print("[+] Deleted contents of Roblox user cache folder")
        except Exception as e:
            print(f"[x] Failed to delete contents of Roblox user cache folder: {e}")
    else:
        print("[-] Roblox user cache folder not found")

def run_roblox_client():
    install_path_tuple = get_roblox_install_path()
    if not install_path_tuple or not install_path_tuple[0] or not install_path_tuple[1]:
        print("[-] Roblox installation path or version not found in registry.")
        return
    base_path = install_path_tuple[0]
    version_folder = install_path_tuple[1]
    full_path = os.path.join(base_path, version_folder)
    exe_path = os.path.join(full_path, "RobloxPlayerBeta.exe")
    if not os.path.exists(exe_path):
        print("[-] RobloxPlayerBeta.exe not found")
        return
    try:
        print("[=] Deleting Roblox user cache before launching client...")
        delete_roblox_user_cache()
        print("[=] Launching Roblox client...")
        subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"[x] Failed to launch Roblox client: {e}")

def export_registry_files():
    portable_roblox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roblox")
    reg_folder_path = os.path.join(portable_roblox_path, "Reg")
    if not os.path.exists(reg_folder_path):
        os.makedirs(reg_folder_path)
    registry_keys = {
        r"HKCR\ROBLOX": "roblox.reg",
        r"HKLM\SOFTWARE\WOW6432Node\ROBLOX Corporation": "roblox_corp.reg",
        r"HKCR\roblox-player": "roblox_player.reg",
        r"HKCR\roblox-studio": "roblox_studio.reg"
    }
    for key, filename in registry_keys.items():
        reg_file_path = os.path.join(reg_folder_path, filename)
        try:
            check = subprocess.run(["reg", "query", key], capture_output=True, text=True)
            if check.returncode != 0:
                print("[-] Registry key not found, skipping")
                continue
            result = subprocess.run(["reg", "export", key, reg_file_path, "/y"], capture_output=True, text=True)
            if result.returncode == 0:
                print("[+] Exported registry key")
            else:
                print(f"[x] Failed to export registry key: {result.stderr.strip()}")
        except Exception as e:
            print(f"[x] Exception exporting registry key: {e}")

def clean_empty_versions_folders():
    versions_base_path, current_version = get_roblox_install_path()
    if not versions_base_path or not current_version:
        print("[-] Roblox Versions base path or current version not found.")
        return
    if not os.path.exists(versions_base_path):
        print("[-] Versions base folder not found")
        return
    for entry in os.listdir(versions_base_path):
        folder_path = os.path.join(versions_base_path, entry)
        if os.path.isdir(folder_path):
            if entry == current_version:
                continue
            try:
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)
                    print("[+] Removed empty version folder")
                else:
                    shutil.rmtree(folder_path)
                    print("[+] Removed old version folder")
            except Exception as e:
                print(f"[x] Failed to remove folder: {e}")

def roblox_auto():
    print("[=] Starting Roblox auto update...")
    download_roblox()
    export_registry_files()
    clean_empty_versions_folders()
    print("[+] Roblox auto update completed.")

def roblox_export():
    print("[=] Starting Roblox export and cleanup...")
    export_registry_files()
    clean_empty_versions_folders()
    print("[+] Roblox export and cleanup completed.")

def main():
    show_credits()
    if len(sys.argv) > 1:
        param = sys.argv[1].lower()
        if param == "/init":
            initialize()
        elif param == "/download":
            download_roblox()
        elif param == "/cleanup":
            cleanup()
        elif param == "/auto":
            roblox_auto()
        elif param == "/export":
            roblox_export()
        else:
            # Ignore unknown parameters silently
            pass
    else:
        initialize()
        run_roblox_client()

if __name__ == "__main__":
    main()
