import subprocess
import os
# Replace 'your-script.bat' with the actual path to your .bat file


bat_path = "E:\ModEngine-2.1.0.0-win64\ModEngine-2.1.0.0-win64\Dummy.bat"
subprocess.run(f'start cmd /k "{bat_path}"', shell=True)
