import tkinter as tk
import requests
import subprocess
import platform

# Función para testear la conexión
def test_keyauth():
    try:
        response = requests.get("https://keyauth.win/api/1.3/", timeout=5)
        return response.status_code in (200, 405)
    except requests.exceptions.RequestException:
        return False

# Cambiar DNS según sistema operativo
def change_dns(primary, secondary):
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["netsh", "interface", "ip", "set", "dns", "name=Wi-Fi", "static", primary], check=True)
            subprocess.run(["netsh", "interface", "ip", "add", "dns", "name=Wi-Fi", secondary, "index=2"], check=True)
            subprocess.run(["netsh", "interface", "ip", "set", "dns", "name=Ethernet", "static", primary], check=True)
            subprocess.run(["netsh", "interface", "ip", "add", "dns", "name=Ethernet", secondary, "index=2"], check=True)
        elif system == "Linux":
            subprocess.run(["sudo", "nmcli", "dev", "mod", "enp0s3", "ipv4.dns", primary, secondary], check=True)
        else:
            raise Exception("Sistema no soportado")
        return True
    except subprocess.CalledProcessError:
        return False

# Restaurar configuración DNS original
def restore_dns():
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["netsh", "interface", "ip", "set", "dns", "name=Wi-Fi", "dhcp"], check=True)
            subprocess.run(["netsh", "interface", "ip", "set", "dns", "name=Ethernet", "dhcp"], check=True)
        elif system == "Linux":
            subprocess.run(["sudo", "nmcli", "dev", "mod", "enp0s3", "ipv4.dns", "none"], check=True)
        else:
            raise Exception("Sistema no soportado")
        return True
    except subprocess.CalledProcessError:
        return False

# Actualiza la etiqueta de estado con la conexión a KeyAuth
def verificar_conexion():
    if test_keyauth():
        estado_label.config(text="✅ KeyAuth está en línea", fg="green")
    else:
        estado_label.config(text="❌ KeyAuth no responde", fg="red")

# Cambiar DNS desde menú
def cambiar_dns_opcion(dns_name):
    dns_map = {
        "Cloudflare": ("1.1.1.1", "1.0.0.1"),
        "Google": ("8.8.8.8", "8.8.4.4"),
        "Quad9": ("9.9.9.9", "149.112.112.112"),
        "OpenDNS": ("208.67.222.222", "208.67.220.220"),
        "AdGuard": ("94.140.14.14", "94.140.15.15")
    }
    if dns_name in dns_map:
        primary, secondary = dns_map[dns_name]
        if change_dns(primary, secondary):
            estado_label.config(text=f"✅ DNS cambiado a {dns_name}", fg="green")
        else:
            estado_label.config(text="❌ Error al cambiar DNS\n¿Ejecutaste como administrador?", fg="red")

# Restaurar DNS con feedback
def restaurar_dns_con_feedback():
    if restore_dns():
        estado_label.config(text="🔁 DNS restaurado", fg="blue")
    else:
        estado_label.config(text="❌ Error al restaurar DNS", fg="red")

# GUI principal
app = tk.Tk()
app.title("🔐 KeyAuth Checker & DNS Tool")
app.geometry("450x550")
app.resizable(False, False)

# Frame principal
frame = tk.Frame(app, bg="#2C3E50", bd=4)
frame.pack(padx=20, pady=20, fill="both", expand=True)

# Título
tk.Label(frame, text="🔐 KeyAuth Checker", font=("Helvetica", 26, "bold"), fg="white", bg="#2C3E50").pack(pady=(25, 15))

# Botón de verificación
tk.Button(frame, text="🌐 Verificar Conexión", command=verificar_conexion, width=30, height=2, font=("Helvetica", 14, "bold"), bg="#5D6D7E", fg="white").pack(pady=15)

# Etiqueta de estado
estado_label = tk.Label(frame, text="⏳ Esperando prueba...", font=("Helvetica", 16), fg="white", bg="#2C3E50")
estado_label.pack(pady=15)

# Selector de DNS
tk.Label(frame, text="🔧 Selecciona un DNS", font=("Helvetica", 16), fg="white", bg="#2C3E50").pack(pady=(25, 10))
dns_dropdown = tk.OptionMenu(frame, *["Cloudflare", "Google", "Quad9", "OpenDNS", "AdGuard"], command=cambiar_dns_opcion)
dns_dropdown.config(width=20, height=2, font=("Helvetica", 12))
dns_dropdown.pack(pady=10)

# Botón de restaurar DNS
tk.Button(frame, text="♻️ Restaurar DNS por defecto", command=restaurar_dns_con_feedback, width=30, height=2, font=("Helvetica", 14, "bold"), bg="#5D6D7E", fg="white").pack(pady=(35, 20))

# Footer
tk.Label(frame, text="Hecho Por GetBoosted", font=("Helvetica", 12, "italic"), fg="white", bg="#2C3E50").pack(pady=15)

# Ejecutar
app.mainloop()
