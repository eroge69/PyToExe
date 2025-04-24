
import time

def launch_attack(target, duration, method, threads):
    print(f"Launching {method} attack on {target} for {duration} seconds with {threads} threads.")
    print("Simulating multi-method DDoS attack... (placeholder)")
    time.sleep(3)
    print("Attack completed.")

def main():
    print("\033[96m╔══════════════════════════════╗")
    print("║          5RDDOS TOOL         ║")
    print("╠══════════════════════════════╣")
    target = input("║ TARGET   : ")
    duration = int(input("║ TIME (s) : "))
    method = input("║ METHOD   : ")
    threads = input("║ THREADS  : ")
    print("╚══════════════════════════════╝\033[0m")
    
    if duration > 172800:
        print("Max allowed time is 172800 seconds (48 hours). Setting to max.")
        duration = 172800

    launch_attack(target, duration, method, threads)

if __name__ == "__main__":
    main()
