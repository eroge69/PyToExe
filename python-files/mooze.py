import os
import sys
import time
import platform

def main():
    # ASCII art for "test"
    ascii_art = """
ooo         oooo    .ooooooooo.       .ooooooooo.   ooooooooooooo   oooooooooooo
`88.        .888`  d8P       y8b     d8P       y8b d'd888'  `888'      `8
 888b     d`888    888       888     888       888       .888P      888
 B YII. .P  888    III       III     III       III      d888'       888ooooooooo
 8  `888`   888    888       888     888       888    .888P         888
 8          888    823       328     823       328    d888'     .P  888
oBo        oIIIo    'YBbsood8P'       'YBbsood8P'   .88888888888P  oBBoooooooooo  
"""
    
    # Check if we're on Windows
    is_windows = platform.system() == "Windows"
    
    # If on Windows, try to enable ANSI support
    if is_windows:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, mode)
        except:
            pass
    
    # Display ASCII art
    print(ascii_art)
    
    # Prompt for key
    print("[-] Key:", end=" ")
    key = input()
    
    # Check key
    if key == "wdyntest":
        print("[-] Loading...")
        time.sleep(1)
        print("\033[32m[+] Welcome!\033[0m")  # Green text
        input("\nSucessfully Injected into roblox! (press insert ingame to see the menu)")
    else:
        print("\033[31m[-] Incorrect key\033[0m")  # Red text
        time.sleep(1)
        sys.exit()

if __name__ == "__main__":
    main()
