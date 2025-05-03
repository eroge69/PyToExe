import customtkinter as ctk
import requests
import subprocess
import platform

# Configuración de estilo
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

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
        estado_label.configure(text="✅ KeyAuth está en línea", text_color="green")
    else:
        estado_label.configure(text="❌ KeyAuth no responde", text_color="red")

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
            estado_label.configure(text=f"✅ DNS cambiado a {dns_name}", text_color="green")
        else:
            estado_label.configure(text="❌ Error al cambiar DNS\n¿Ejecutaste como administrador?", text_color="red")

# Restaurar DNS con feedback
def restaurar_dns_con_feedback():
    if restore_dns():
        estado_label.configure(text="🔁 DNS restaurado", text_color="blue")
    else:
        estado_label.configure(text="❌ Error al restaurar DNS", text_color="red")

# GUI principal
app = ctk.CTk()
app.title("🔐 KeyAuth Checker & DNS Tool")
app.geometry("450x550")
app.resizable(False, False)

# Frame principal
frame = ctk.CTkFrame(app, corner_radius=25, fg_color="#2C3E50", border_color="#1C2A36", border_width=4)
frame.pack(padx=20, pady=20, fill="both", expand=True)

# Título
ctk.CTkLabel(frame, text="🔐 KeyAuth Checker", font=("Helvetica", 26, "bold"), text_color="white").pack(pady=(25, 15))

# Botón de verificación
ctk.CTkButton(frame, text="🌐 Verificar Conexión", command=verificar_conexion, width=230, height=55, corner_radius=12, hover_color="#5D6D7E", font=("Helvetica", 14, "bold")).pack(pady=15)

# Etiqueta de estado
estado_label = ctk.CTkLabel(frame, text="⏳ Esperando prueba...", font=("Helvetica", 16), text_color="white")
estado_label.pack(pady=15)

# Selector de DNS
ctk.CTkLabel(frame, text="🔧 Selecciona un DNS", font=("Helvetica", 16), text_color="white").pack(pady=(25, 10))
dns_dropdown = ctk.CTkOptionMenu(frame, values=["Cloudflare", "Google", "Quad9", "OpenDNS", "AdGuard"], command=cambiar_dns_opcion, height=45, corner_radius=12, dynamic_resizing=True)
dns_dropdown.pack(pady=10)

# Botón de restaurar DNS
ctk.CTkButton(frame, text="♻️ Restaurar DNS por defecto", command=restaurar_dns_con_feedback, width=230, height=55, corner_radius=12, hover_color="#5D6D7E", font=("Helvetica", 14, "bold")).pack(pady=(35, 20))

# Footer
ctk.CTkLabel(frame, text="Hecho Por GetBoosted", font=("Helvetica", 12, "italic"), text_color="white").pack(pady=15)

# Ejecutar
app.mainloop()
