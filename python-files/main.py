#!/usr/bin/env python3
"""
TCP Client Loader
Compiles and runs the C++ TCP client with various configuration options.
"""

import os
import sys
import subprocess
import platform
import argparse
import shutil
from pathlib import Path

class ClientLoader:
    def __init__(self):
        self.system = platform.system().lower()
        self.client_name = "tcp_client"
        self.source_file = "client.cpp"
        self.executable = self.client_name + (".exe" if self.system == "windows" else "")
        
    def check_compiler(self):
        """Check if a C++ compiler is available"""
        compilers = []
        
        if self.system == "windows":
            compilers = ["g++", "clang++", "cl"]
        else:
            compilers = ["g++", "clang++"]
            
        for compiler in compilers:
            if shutil.which(compiler):
                print(f"✓ Found compiler: {compiler}")
                return compiler
                
        print("❌ No C++ compiler found!")
        print("Please install one of the following:")
        if self.system == "windows":
            print("  - MinGW-w64 (g++)")
            print("  - Visual Studio Build Tools (cl)")
            print("  - Clang (clang++)")
        else:
            print("  - GCC (g++)")
            print("  - Clang (clang++)")
            print("  - On Ubuntu/Debian: sudo apt install build-essential")
            print("  - On CentOS/RHEL: sudo yum groupinstall 'Development Tools'")
            print("  - On macOS: xcode-select --install")
        return None
        
    def compile_client(self, compiler="g++", debug=False):
        """Compile the C++ client"""
        print(f"Compiling {self.source_file}...")
        
        # Basic compilation flags
        flags = ["-std=c++11", "-pthread"]
        
        if debug:
            flags.extend(["-g", "-DDEBUG"])
            print("Building in debug mode...")
        else:
            flags.extend(["-O2"])
            
        # Platform-specific flags
        if self.system == "windows":
            flags.extend(["-lws2_32"])
            
        # Compile command
        cmd = [compiler] + flags + ["-o", self.executable, self.source_file]
        
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Compilation successful! Created {self.executable}")
                return True
            else:
                print("❌ Compilation failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
        except FileNotFoundError:
            print(f"❌ Compiler '{compiler}' not found")
            return False
        except Exception as e:
            print(f"❌ Compilation error: {e}")
            return False
            
    def run_client(self, args):
        """Run the compiled client with given arguments"""
        if not os.path.isfile(self.executable):
            print(f"❌ Executable {self.executable} not found!")
            print("Run with --compile first")
            return False
            
        cmd = [f"./{self.executable}"] + args
        
        try:
            print(f"Starting client: {' '.join(cmd)}")
            print("=" * 50)
            subprocess.run(cmd)
            return True
        except KeyboardInterrupt:
            print("\n🛑 Client stopped by user")
            return True
        except Exception as e:
            print(f"❌ Error running client: {e}")
            return False
            
    def clean(self):
        """Clean compiled files"""
        files_to_clean = [self.executable]
        
        for file in files_to_clean:
            if os.path.isfile(file):
                os.remove(file)
                print(f"Removed {file}")
                
        print("Clean complete")
        
    def show_status(self):
        """Show current status"""
        print("TCP Client Status")
        print("=" * 30)
        print(f"System: {platform.system()} {platform.machine()}")
        print(f"Source file: {self.source_file} {'✓' if os.path.isfile(self.source_file) else '❌'}")
        print(f"Executable: {self.executable} {'✓' if os.path.isfile(self.executable) else '❌'}")
        
        compiler = self.check_compiler()
        print(f"Compiler: {compiler if compiler else 'Not found'}")

def main():
    parser = argparse.ArgumentParser(description="TCP Client Loader")
    parser.add_argument("--compile", "-c", action="store_true", help="Compile the client")
    parser.add_argument("--run", "-r", action="store_true", help="Run the client")
    parser.add_argument("--clean", action="store_true", help="Clean compiled files")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    parser.add_argument("--debug", "-d", action="store_true", help="Compile in debug mode")
    parser.add_argument("--compiler", default="g++", help="Specify compiler (default: g++)")
    
    # Client arguments
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=2998, help="Server port (default: 2998)")
    parser.add_argument("--name", default="Python Loaded Client", help="Client name")
    parser.add_argument("--version", default="1.0.0", help="Client version")
    
    args = parser.parse_args()
    
    loader = ClientLoader()
    
    # Handle different actions
    if args.status:
        loader.show_status()
        return
        
    if args.clean:
        loader.clean()
        return
        
    if args.compile:
        if not loader.check_compiler():
            sys.exit(1)
        if not loader.compile_client(args.compiler, args.debug):
            sys.exit(1)
            
    if args.run:
        client_args = []
        client_args.extend(["--host", args.host])
        client_args.extend(["--port", str(args.port)])
        client_args.extend(["--name", args.name])
        client_args.extend(["--version", args.version])
        
        if not loader.run_client(client_args):
            sys.exit(1)
            
    # If no specific action, show help
    if not any([args.compile, args.run, args.clean, args.status]):
        parser.print_help()
        print("\nQuick start:")
        print("  python loader.py --compile --run")
        print("  python loader.py -c -r --host 192.168.1.100 --port 2998")

if __name__ == "__main__":
    main()