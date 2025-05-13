import os

# List of target directories
directories = [
    r"C:\Users\ASM\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\BOSS\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\ER1\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\ER2\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\TCR1\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\TCR2\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\TUTY\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\PP\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\MIS\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\HO1\AppData\Local\Google\Chrome\User Data\Default\Network",
    r"C:\Users\HO2\AppData\Local\Google\Chrome\User Data\Default\Network"
]

# Create directories and dummy files
for directory in directories:
    try:
        os.makedirs(directory, exist_ok=True)
        dummy_file_path = os.path.join(directory, "dummy.txt")
        with open(dummy_file_path, "w") as f:
            f.write("This is a dummy file.")
        print(f"Created: {dummy_file_path}")
    except Exception as e:
        print(f"Error creating {directory}: {e}")
