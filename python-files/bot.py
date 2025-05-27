import subprocess
import time
import argparse

# Configura o argparse para aceitar o caminho do script como argumento
parser = argparse.ArgumentParser(description="Run a PowerShell script in a loop.")
parser.add_argument("script", help="Path to the PowerShell script (e.g., script.ps1)")
args = parser.parse_args()

powershell_script = args.script

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
