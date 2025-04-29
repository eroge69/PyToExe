import os
import sys
import ctypes
import subprocess

def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_user_to_admin_group(username):
    """Add the current user to the Administrators group."""
    try:
        # Command to add user to Administrators group
        command = f'net localgroup Administrators "{username}" /add'
        subprocess.run(command, check=True, shell=True)
        print(f"Success! User '{username}' added to Administrators group.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add user to Administrators group: {e}")

def main():
    if not is_admin():
        print("Requesting admin privileges... (UAC prompt will appear)")
        # Re-run the script with admin rights (triggers UAC)
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1
        )
        sys.exit(0)
    
    # Running as admin now
    print("Running with admin privileges.")
    current_user = os.getenv("USERNAME")
    
    if current_user:
        add_user_to_admin_group(current_user)
    else:
        print("Could not determine current username.")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()