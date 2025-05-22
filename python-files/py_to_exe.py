import subprocess
import sys
import os

def py_to_exe(py_file):
    if not os.path.isfile(py_file):
        print(f"Το αρχείο {py_file} δεν βρέθηκε.")
        return
    
    # Εντολή PyInstaller για .exe σε ένα αρχείο
    command = ["pyinstaller", "--onefile", "--windowed", py_file]
    
    try:
        subprocess.run(command, check=True)
        print(f"Το εκτελέσιμο για το {py_file} δημιουργήθηκε με επιτυχία.")
        print("Το .exe βρίσκεται μέσα στο φάκελο 'dist'")
    except subprocess.CalledProcessError as e:
        print(f"Σφάλμα κατά την εκτέλεση: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Χρήση: python py_to_exe.py το_αρχείο_σου.py")
    else:
        py_to_exe(sys.argv[1])
