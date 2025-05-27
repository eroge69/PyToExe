import subprocess
import time

powershell_script = "script.ps1"

try:
    while True:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script],
            capture_output=False,
            text=True
        )

        print("Making request...")
        time.sleep(3)

except KeyboardInterrupt:
    print("\nEnd...")
