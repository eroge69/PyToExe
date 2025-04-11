import subprocess
import sys

# Function to install required libraries
def install_libraries():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ftplib", "socket"])

# Function to check FTP server
def check_ftp_server(url):
    try:
        # Connect to the FTP server
        ftp = ftplib.FTP(url)
        
        # Attempt anonymous login
        ftp.login()
        print(f"Connected to {url} as anonymous user.")
        
        # List directories and services
        ftp.retrlines('LIST')
        
        # Close the connection
        ftp.quit()
    except ftplib.all_errors as e:
        print(f"Failed to connect or login to {url}: {e}")
    except socket.error as e:
        print(f"Socket error: {e}")

if __name__ == "__main__":
    # Install required libraries
    install_libraries()
    
    # Prompt user for FTP server URL
    url = input("Enter the URL of the FTP server: ")
    
    # Check the FTP server
    check_ftp_server(url)
