import os
import subprocess

def run_command(cmd, desc=""):
    print(f"\n[🛠] {desc} Komanda: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("[✔] Uğurla tamamlandı.")
    else:
        print(f"[❌] Xəta baş verdi:\n{result.stderr}")

def restart_all_services():
    print("\n🔄 Aktiv servislər yenidən başladılır...")
    run_command(
        'powershell -Command "Get-Service | Where-Object {$_.Status -eq \'Running\'} | ForEach-Object { Restart-Service $_.Name -Force }"',
        "Bütün aktiv servislərin restart olunması"
    )

def fix_printer_services():
    print("\n🖨 Printer xidmətləri düzəldilir...")
    run_command("net stop spooler", "Spooler xidməti dayandırılır")
    run_command("del /Q /F %systemroot%\\System32\\spool\\PRINTERS\\*.*", "Çap növbəsi təmizlənir")
    run_command("net start spooler", "Spooler xidməti yenidən başladılır")

def update_certificates():
    print("\n🔐 Sertifikatlar yenilənir...")
    run_command("certutil -generateSSTFromWU roots.sst", "Yeni sertifikat siyahısı yaradılır")
    run_command("certutil -addstore -f root roots.sst", "Sertifikatlar sistemə əlavə olunur")
    run_command("del roots.sst", "Müvəqqəti fayl silinir")

def reset_firewall():
    print("\n🔥 Firewall parametrləri sıfırlanır...")
    run_command("netsh advfirewall reset", "Firewall reset edilir")

def fix_network():
    print("\n🌐 Şəbəkə problemi düzəldilir...")
    run_command("ipconfig /flushdns", "DNS cache təmizlənir")
    run_command("ipconfig /release", "IP ünvanı buraxılır")
    run_command("ipconfig /renew", "Yeni IP ünvan alınır")
    run_command("netsh int ip reset", "IP interfeysi sıfırlanır")
    run_command("netsh winsock reset", "Winsock reset olunur")

def main():
    print("\n🚀 Windows Sistem Həll Aləti Başlayır...\n")
    restart_all_services()
    fix_printer_services()
    update_certificates()
    reset_firewall()
    fix_network()
    print("\n✅ Bütün proseslər uğurla tamamlandı. Sisteminizi yenidən başladın (təklif olunur).")

if __name__ == "__main__":
    main()
