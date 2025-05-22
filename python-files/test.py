import argparse
import os
import getpass
import shutil
import uuid
import json
import uuid
import subprocess
import tempfile
import re
import typing as t
import requests
import time
import psutil

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Reset Cursor telemetry IDs and repack the AppImage."
    )
    parser.add_argument(
        "--appimage",
        required=True,
        help="Path to the Cursor AppImage file.",
        dest="appimage_path",
    )
    return parser.parse_args()

def validate_appimage_path(appimage_path: str) -> None:
    """Validates the provided AppImage path."""
    if not appimage_path:
        raise ValueError("AppImage path is required.")
    if not os.path.exists(appimage_path):
        raise FileNotFoundError(f"AppImage file not found at {appimage_path}")
    if not os.path.isfile(appimage_path):
        raise ValueError(f"{appimage_path} is not a file.")

def get_user_info() -> tuple[str, str]:
    """Gets the real username and home directory."""
    try:
        user = getpass.getuser
        home = os.path.expanduser(f"~{user}")
        return user, home
    except KeyError:
        raise OSError("Unable to determine the user.")

def check_required_commands() -> None:
    """Checks if required commands are available."""
    for cmd in ["uuidgen"]:
        if shutil.which(cmd) is None:
            raise FileNotFoundError(f"Required command '{cmd}' not found.")

def generate_mac_machine_id() -> str:
    """Generates a MAC-like machine ID."""
    random_num = uuid.uuid4().hex
    new_char = hex((int(random_num[12], 16) & 0x3) | 0x8)[2:]
    return random_num[:12] + "4" + random_num[13:16] + new_char + random_num[17:]

def generate_random_id() -> str:
    """Generates a 64-bit random ID."""
    return str(uuid.uuid4()).replace("-", "") + str(uuid.uuid4()).replace("-", "")

def check_cursor_process() -> None:
    """Checks if the Cursor process is running. Now for debugging only."""
    while True:
        cursor_running = False
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                process_name = proc.name().lower()
                cmdline = proc.cmdline()

                if "cursor" in process_name:
                    if process_name == "cursor" or any(
                        arg.lower().endswith("cursor.app") or arg.lower().endswith("cursor.app/contents/macos/cursor") for arg in cmdline
                    ):
                        cursor_running = True
                        break

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # Ignore processes that might disappear

        if cursor_running:
            print("Detected that Cursor is still running.")
            time.sleep(1)
        else:
            print("Cursor is not running. Continuing execution...")
            break

def kill_cursor_processes() -> None:
    """Kills any running Cursor processes."""
    print("WARNING: This script will kill any running Cursor processes.")
    print("Proceeding in 3 seconds...")
    time.sleep(3)

    killed_processes = False
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            process_name = proc.name().lower()
            cmdline = proc.cmdline()

            if "cursor" in process_name:
                if process_name == "cursor" or any(
                    arg.lower().endswith("cursor.app") or arg.lower().endswith("cursor.app/contents/macos/cursor") for arg in cmdline
                ):
                    print(f"Killing process: {process_name} (PID: {proc.pid})")
                    proc.kill()
                    killed_processes = True
                    # wait for process to actually terminate
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        print(f"Warning, timed out waiting for {process_name} PID: ({proc.pid}) to terminate.")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if not killed_processes:
        print("No running Cursor processes found.")
    else:
        print("Cursor processes terminated.")

def update_storage_json(
    home: str,
    new_machine_id: str,
    new_mac_machine_id: str,
    new_dev_device_id: str,
    new_sqm_id: str,
    use_jq: bool,
) -> None:
    """Updates storage.json with new telemetry IDs."""

    storage_json_path = os.path.join(
        home, ".config", "Cursor", "User", "globalStorage", "storage.json"
    )
    if not os.path.exists(storage_json_path):
        print(f"Warning: {storage_json_path} not found. Skipping update.")
        return

    backup_path = storage_json_path + ".bak"
    try:
        shutil.copyfile(storage_json_path, backup_path)
    except OSError as e:
        raise OSError(f"Unable to backup storage.json: {e}") from e

    temp_file = storage_json_path + ".tmp"

    if use_jq and shutil.which("jq"):
        jq_cmd = [
            "jq",
            "--arg", "mid", new_machine_id,
            "--arg", "mmid", new_mac_machine_id,
            "--arg", "did", new_dev_device_id,
            "--arg", "sid", new_sqm_id,
            '.["telemetry.machineId"]=$mid | .["telemetry.macMachineId"]=$mmid | .["telemetry.devDeviceId"]=$did | .["telemetry.sqmId"]=$sid',
            storage_json_path
        ]

        try:
            with open(temp_file, "w") as outfile:
                subprocess.run(jq_cmd, stdout=outfile, stderr=subprocess.PIPE, check=True, text=True)

            if os.path.exists(temp_file):
                shutil.move(temp_file, storage_json_path)
                print("storage.json updated successfully using jq.")
            else:
                print("Error: jq command did not create a temporary file.")

        except subprocess.CalledProcessError as e:
            print(f"Error updating storage.json using jq: {e}")
            print(f"jq stderr: {e.stderr}")
            if os.path.exists(backup_path):
                try:
                    shutil.copyfile(backup_path, storage_json_path)
                    print("Restored storage.json from backup.")
                except OSError as restore_err:
                    print(f"Error restoring from backup: {restore_err}")

    else:
        try:
            with open(storage_json_path, "r+") as f:
                data = json.load(f)
                data["telemetry.machineId"] = new_machine_id
                data["telemetry.macMachineId"] = new_mac_machine_id
                data["telemetry.devDeviceId"] = new_dev_device_id
                data["telemetry.sqmId"] = new_sqm_id
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            print("storage.json updated successfully.")

        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            raise OSError(f"Failed to update storage.json: {e}") from e

def extract_appimage(appimage_path: str, extract_path: str) -> None:
    """Extracts the AppImage to the specified path."""
    print(f"Extracting AppImage to: {extract_path}")
    try:
        subprocess.run(
            [appimage_path, "--appimage-extract"],
            check=True,
            cwd=extract_path,
            capture_output=True,
            text=True,
        )
        print(f"Extracted AppImage to: {extract_path}/squashfs-root")
    except subprocess.CalledProcessError as e:
        raise OSError(f"Failed to extract AppImage: {e}") from e

def modify_files(extract_path: str) -> None:
    """Modifies the files inside the extracted AppImage."""
    files = [
        os.path.join(extract_path, "squashfs-root", "usr", "share", "cursor", "resources", "app", "out", "main.js"),
        os.path.join(
            extract_path,
            "squashfs-root",
            "usr", "share", "cursor",
            "resources",
            "app",
            "out",
            "vs",
            "code",
            "node",
            "cliProcessMain.js",
        ),
    ]
    for file in files:
        if not os.path.exists(file):
            print(f"Warning: File {file} not found")
            continue

        try:
            # Set permissions on the specific file
            os.chmod(file, 0o755)

            with open(file, "r+") as f:
                content = f.read()
                modified_content = re.sub(
                    r'"[^"]*/etc/machine-id[^"]*"', '"uuidgen"', content
                )
                f.seek(0)
                f.write(modified_content)
                f.truncate()
            print(f"Successfully modified {file}")
        except OSError as e:
            raise OSError(f"Failed to modify {file}: {e}") from e

def download_appimagetool(appimagetool_path: str) -> None:
    """Downloads appimagetool."""

    print("appimagetool not found, attempting to download...")
    url = f"https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-{os.uname().machine}.AppImage"

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(appimagetool_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        os.chmod(appimagetool_path, 0o755)
        print(f"Successfully downloaded appimagetool to {appimagetool_path}")

    except requests.RequestException as e:
        raise OSError(f"Failed to download appimagetool: {e}") from e

def repack_appimage(extract_path: str, appimage_path: str) -> None:
    """Repacks the AppImage."""
    appimagetool_path = "/tmp/appimagetool"  # Fixed path
    if not os.path.exists(appimagetool_path):
        download_appimagetool(appimagetool_path)

    print("Repacking AppImage...")
    try:
        subprocess.run(
            [
                appimagetool_path,
                "-n",  # Overwrite
                os.path.join(extract_path, "squashfs-root"),
            ],
            check=True,
            capture_output=True,
            text=True,
            env={"ARCH": "x86_64", "PATH": os.environ["PATH"]},  # Use the correct PATH
        )
        # Find the newly created AppImage (in the same directory as the original)
        appimage_dir = os.path.dirname(appimage_path)
        new_images = [f for f in os.listdir(appimage_dir) if "Cursor-" in f and f.endswith(".AppImage")]

        if not new_images:
            raise FileNotFoundError("Error: No repacked AppImage found.")

        new_images_paths = [os.path.join(appimage_dir, image) for image in new_images]
        new_images_paths.sort(key=os.path.getctime, reverse=True)
        new_image = new_images_paths[0]
        shutil.move(new_image, appimage_path) # Move to overwrite the original
        print(f"Repacked AppImage updated at {appimage_path}")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise OSError(f"Failed to repack AppImage: {e}") from e

def main() -> None:
    """Main function."""
    args = parse_arguments()
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script's directory
    appimage_path = os.path.abspath(args.appimage_path)  # Absolute path to AppImage

    try:
        validate_appimage_path(appimage_path)
        user, home = get_user_info()
        kill_cursor_processes()
        check_cursor_process()

        new_machine_id = generate_random_id()
        new_mac_machine_id = generate_mac_machine_id()
        new_dev_device_id = str(uuid.uuid4())
        new_sqm_id = str(uuid.uuid4()).upper()

        use_jq = False
        if shutil.which("jq"):
            choice = input("Do you want to use 'jq' for updating storage.json? (y/n, default: n): ").strip().lower()
            use_jq = choice == "y"

        update_storage_json(
            home,
            new_machine_id,
            new_mac_machine_id,
            new_dev_device_id,
            new_sqm_id,
            use_jq,
        )

        with tempfile.TemporaryDirectory(dir=script_dir) as temp_dir: # Use script directory.
            extract_path = os.path.abspath(temp_dir)
            extract_appimage(appimage_path, extract_path)
            modify_files(extract_path)
            repack_appimage(extract_path, appimage_path) # Repack

        print("Successfully updated all IDs:")
        print(f"New telemetry.machineId: {new_machine_id}")
        print(f"New telemetry.macMachineId: {new_mac_machine_id}")
        print(f"New telemetry.devDeviceId: {new_dev_device_id}")
        print(f"New telemetry.sqmId: {new_sqm_id}")
        print(f"Reset complete! Please launch Cursor using {appimage_path}")

    except (ValueError, FileNotFoundError, OSError, Exception) as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()