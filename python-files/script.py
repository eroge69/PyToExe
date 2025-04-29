import subprocess

output_file = "systeminfo.txt"

with open(output_file, "w") as file:
    subprocess.run("systeminfo", stdout=file, text=True)

subprocess.run(["notepad", output_file])