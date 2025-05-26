import os
import subprocess
import sys
import ctypes

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_exclusion(path):
    """Add a path to Windows Defender exclusions using PowerShell"""
    try:
        # Escape the path for PowerShell
        escaped_path = path.replace("'", "''")
        
        # PowerShell command to add exclusion
        ps_command = f"""
        $path = '{escaped_path}'
        if (-not (Test-Path $path)) {{
            Write-Warning "Path does not exist: $path"
            exit 1
        }}
        Add-MpPreference -ExclusionPath $path
        if ($?) {{
            Write-Output "Successfully added exclusion for: $path"
        }} else {{
            Write-Warning "Failed to add exclusion for: $path"
            exit 1
        }}
        """
        
        # Execute PowerShell command
        result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error adding exclusion: {result.stderr}")
            return False
        
        print(result.stdout)
        return True
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def main():
    # Check for admin rights
    if not is_admin():
        print("This script requires administrator privileges. Please run as administrator.")
        sys.exit(1)
    
    # Path to add (C drive)
    c_drive = "C:\\"
    
    print(f"Attempting to add {c_drive} to Windows Security exclusions...")
    
    if add_exclusion(c_drive):
        print("\nOperation completed successfully.")
    else:
        print("\nFailed to add exclusion.")

if __name__ == "__main__":
    main()