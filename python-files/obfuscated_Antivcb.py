#!/usr/bin/env python3
import os, sys, time, ctypes, shutil, base64, random
from datetime import datetime

# More sophisticated obfuscation using multiple encoding layers
def d3c0d3(s):
    return base64.b64decode(base64.b64decode(s + b'=' * (-len(s) % 4))).decode()

# Split strings across multiple variables and join them at runtime
_p = "T1pUc1"
_t = "TlZONVUz"
_h = "UmxiWFE="
_a = base64.b64encode(b"QzpcV2luZG93c1xTeXN0ZW0zMlxkcml2ZXJzXGV0Y1xob3N0cw==").decode()

# Dynamically build paths using lambda functions
g3t_p4th = lambda: base64.b64decode(base64.b64decode(_a).decode()).decode()
b4ck_p4th = lambda: os.path.join(os.path.expanduser("~" + ""), "system" + "_" + "backup")

# Use XOR for IP obfuscation
def x0r(data, key=42):
    return ''.join(chr(ord(c) ^ key) for c in data)

r_1p = x0r('JAJAJA')  # XORed "0.0.0.0"

# Mix up the site lists with decoys and noise
_d3c0y = ["google.com", "microsoft.com", "apple.com", "amazon.com"]
_n01s3 = ["example.com", "test.org", "sample.net"]

# Actual sites encoded with multiple layers
_s1t3s_1 = [
    base64.b64encode(base64.b64encode(b"cGVyZi1ldmVudHMuY2xvdWQudW5pdHkzZC5jb20=").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"Y2RwLmNsb3VkLnVuaXR5M2QuY29t").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"Y29uZmlnLnVjYS5jbG91ZC51bml0eTNkLmNvbQ==").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"ZmlyZWhvc2UudXMtZWFzdC0yLmFtYXpvbmF3cy5jb20=").decode().encode()).decode()
]

_s1t3s_2 = [
    base64.b64encode(base64.b64encode(b"ZXZlbnRzLmFwcHNmbHllci5jb20=").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"ZXZlbnRzLmJhY2t0cmFjZS5pbw==").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"c3VibWl0LmJhY2t0cmFjZS5pbw==").decode().encode()).decode()
]

_s1t3s_3 = [
    base64.b64encode(base64.b64encode(b"bW9kZXJhdGlvbi5yZWMubmV0").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"YXBpLnJlYy5uZXQvYXBpL1BsYXllclJlcG9ydGluZw==").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"YXBpLnJlYy5uZXQvYXBpL1BsYXllclJlcG9ydGluZy92MS9yZWZlcmVl").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"YXBpLnJlYy5uZXQvYXBpL21vZGVyYXRpb24vdjI=").decode().encode()).decode()
]

_s1t3s_4 = [
    base64.b64encode(base64.b64encode(b"YXBpLnJlYy5uZXQvYXBpL3BsYXllcnMvdjIvYmFuc3RhdHVz").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"YXBpLnJlYy5uZXQvYXBpL3BsYXllcm1vZGVyYXRpb24vdjE=").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"YXBpLnJlYy5uZXQvYXBpL3NhbmN0aW9ucy92MQ==").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"YXBpLnJlYy5uZXQvYXBpL3BsYXllcnMvdjEvc3RhdHVz").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"bW9kZXJhdGlvbmFwaS5yZWMubmV0").decode().encode()).decode()
]

_s1t3s_5 = [
    base64.b64encode(base64.b64encode(b"YW5hbHl0aWNzLmVhc3lhbnRpY2hlYXQubmV0").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"dGVsZW1ldHJ5LmVhc3lhbnRpY2hlYXQubmV0").decode().encode()).decode(),
    base64.b64encode(base64.b64encode(b"cmVwb3J0cy5lYXN5YW50aWNoZWF0Lm5ldA==").decode().encode()).decode()
]

# Function to rebuild the complete list at runtime
def _b1ld_s1t3s():
    _all = []
    _layers = [_s1t3s_1, _s1t3s_2, _s1t3s_3, _s1t3s_4, _s1t3s_5]
    
    for _layer in _layers:
        for _item in _layer:
            try:
                _decoded = base64.b64decode(base64.b64decode(_item).decode()).decode()
                _all.append(_decoded)
            except:
                pass  # Ignore any decoding errors
    
    # Insert some random reordering to make it harder to track
    if random.randint(0, 10) > 5:
        random.shuffle(_all)
    
    return _all

# Checker functions with fake alternatives
def _v3r1fy_p3rms():
    """Check for privileges - primary"""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

def _ch3ck_p3rms():
    """Check for privileges - fallback"""
    try:
        return _v3r1fy_p3rms()
    except Exception:
        return False

def _g3t_p3rms():
    """Get required privileges"""
    if not _ch3ck_p3rms():
        print(f"{'Requesting administrator privileges...'}")
        try:
            args = ' '.join(f'"{arg}"' for arg in sys.argv)
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, args, None, 1
            )
        except Exception:
            input("Press Enter to exit...")
        sys.exit()

def _cr34t3_b4ckup():
    """Save backup file"""
    _p4th = g3t_p4th()
    _b4ck = b4ck_p4th()
    
    if not os.path.exists(_p4th):
        print(f"Error: Target file not found!")
        return False
        
    try:
        os.makedirs(_b4ck, exist_ok=True)
        _t1m3 = datetime.now().strftime("%Y%m%d_%H%M%S")
        _bck_f1l3 = os.path.join(_b4ck, f"backup_{_t1m3}.bak")
        shutil.copy2(_p4th, _bck_f1l3)
        print(f"Backup created.")
        return True
    except Exception as e:
        print(f"Backup failed: {str(e)}")
        return False

def _r3st0r3_b4ckup():
    """Restore from backup"""
    _p4th = g3t_p4th()
    _b4ck = b4ck_p4th()
    
    try:
        _f1l3s = [os.path.join(_b4ck, f) for f in os.listdir(_b4ck) 
                if f.startswith("backup_") and f.endswith(".bak")]
        
        if not _f1l3s:
            print("No backups found")
            return False
            
        _l4t3st = max(_f1l3s, key=os.path.getmtime)
        shutil.copy2(_l4t3st, _p4th)
        print(f"Restored from backup")
        return True
    except Exception as e:
        print(f"Restore failed: {str(e)}")
        return False

def _ch3ck_st4tus():
    """Check current status"""
    _p4th = g3t_p4th()
    
    try:
        if not os.path.exists(_p4th):
            print(f"Target file not found!")
            return False
            
        with open(_p4th, "r") as file:
            _c0nt3nt = file.read()
        
        _s1t3s = _b1ld_s1t3s()
        return any(site in _c0nt3nt for site in _s1t3s)
    except Exception as e:
        print(f"Status check failed: {str(e)}")
        return False

def _t0ggl3_4ct10n(force=None):
    """Toggle target settings"""
    _p4th = g3t_p4th()
    _1p = x0r(r_1p)
    
    try:
        if not os.path.exists(_p4th):
            print(f"Target file not found!")
            return False
            
        _cr34t3_b4ckup()
        
        with open(_p4th, "r") as file:
            _l1n3s = file.readlines()
        
        _s1t3s = _b1ld_s1t3s()
        _4ct1v3 = any(
            any(site in line for site in _s1t3s) for line in _l1n3s
        )
        
        _3n4bl3 = not _4ct1v3 if force is None else force
        
        if _3n4bl3:
            _f1lt3r3d = [line for line in _l1n3s if not any(site in line for site in _s1t3s)]
            _f1lt3r3d.append("\n# System configuration - added automatically\n")
            for site in _s1t3s:
                _f1lt3r3d.append(f"0.0.0.0 {site}\n")
            print("Protection enabled")
        else:
            _f1lt3r3d = [line for line in _l1n3s if not any(site in line for site in _s1t3s)]
            print("Protection disabled")
        
        with open(_p4th, "w") as file:
            file.writelines(_f1lt3r3d)
            
        return True
    except Exception as e:
        print(f"Toggle failed: {str(e)}")
        return False

def _4pply_ch4ng3s():
    """Apply changes"""
    try:
        _cmd = base64.b64decode(b"aXBjb25maWcgL2ZsdXNoZG5z").decode()
        os.system(_cmd)
        print("Applied system changes")
        return True
    except Exception as e:
        print(f"Failed to apply: {str(e)}")
        return False

def _m41n():
    """Main function with added delay and obfuscation"""
    _g3t_p3rms()
    
    # Add small random delay to make behavior less predictable
    time.sleep(random.uniform(0.1, 0.5))
    
    # Command processing with extra noise
    _4rgs = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Execute decoy operations that don't do anything important
    if random.randint(0, 10) > 7:
        os.path.exists(os.path.join(os.path.expanduser("~"), ".config"))
    
    if "--status" in _4rgs:
        _st4tus = _ch3ck_st4tus()
        print(f"Protection status: {'ON' if _st4tus else 'OFF'}")
    elif "--restore" in _4rgs:
        _r3st0r3_b4ckup()
    elif "--on" in _4rgs:
        _t0ggl3_4ct10n(force=True)
        _4pply_ch4ng3s()
    elif "--off" in _4rgs:
        _t0ggl3_4ct10n(force=False)
        _4pply_ch4ng3s()
    else:
        _st4tus = _ch3ck_st4tus()
        _t0ggl3_4ct10n()
        _4pply_ch4ng3s()
        print(f"Protection has been turned {'OFF' if _st4tus else 'ON'}")
    
    if not _4rgs:
        input("Press Enter to exit...")

# Entry point with additional obfuscation
if __name__ == "__main__" and random.randint(0, 100) < 101:
    try:
        _m41n()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        if random.randint(0, 10) > 5:
            print(f"An error occurred: {str(e)}")
        else:
            print("Operation failed.")
