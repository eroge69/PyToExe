import ctypes
import win32api
import win32process
import win32con

def inject_dll(pid, dll_path):
    try:
        # Open the process
        h_process = win32api.OpenProcess(win32con.PROCESS_CREATE_THREAD | win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_OPERATION | win32con.PROCESS_VM_WRITE | win32con.PROCESS_VM_READ, False, pid)

        # Allocate memory for the DLL path
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        ntdll = ctypes.WinDLL('ntdll', use_last_error=True)
        dll_path_bytes = dll_path.encode('utf-8') + b'\x00'
        dll_path_addr = kernel32.VirtualAllocEx(h_process, None, len(dll_path_bytes), win32con.MEM_COMMIT, win32con.PAGE_READWRITE)

        # Write the DLL path to the allocated memory
        kernel32.WriteProcessMemory(h_process, dll_path_addr, dll_path_bytes, len(dll_path_bytes), None)

        # Get the address of the LoadLibraryA function
        load_library_addr = kernel32.GetProcAddress(kernel32.GetModuleHandleA(b'kernel32'), b'LoadLibraryA')

        # Create a remote thread to load the DLL
        kernel32.CreateRemoteThread(h_process, None, 0, load_library_addr, dll_path_addr, 0, None)

        # Close handles
        kernel32.VirtualFreeEx(h_process, dll_path_addr, 0, win32con.MEM_RELEASE)
        win32api.CloseHandle(h_process)

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    pid = int(input("Enter the process ID: "))
    dll_path = input("Enter the DLL path: ")
    if inject_dll(pid, dll_path):
        print("DLL injected successfully.")
    else:
        print("Failed to inject DLL.")

    # Keep the script open
    while True:
        user_input = input("Press 'q' to quit: ")
        if user_input.lower() == 'q':
            break
