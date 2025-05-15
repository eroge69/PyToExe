from scapy.all import sniff
import time


# IP kamery EUFY
CAMERA_IP = "192.168.1.121"


# Porty do monitorowania (RTSP, HTTPS, HTTP, inne)
WATCH_PORTS = [554, 443, 80]


# Czas bezruchu po którym uznajemy, że kamera jest "nieużywana"
IDLE_TIMEOUT = 60  # sekund


last_seen = 0


def packet_callback(packet):
    global last_seen
    if packet.haslayer("IP"):
        ip_layer = packet["IP"]
        if ip_layer.src == CAMERA_IP or ip_layer.dst == CAMERA_IP:
            if packet.haslayer("TCP") and packet["TCP"].dport in WATCH_PORTS:
                print(f"[{time.ctime()}] Detected connection on port {packet['TCP'].dport}")
                last_seen = time.time()


def monitor_camera():
    global last_seen
    last_seen = 0
    print("Monitoring started...")
    try:
        sniff(filter=f"host {CAMERA_IP}", prn=packet_callback, store=0)
    except KeyboardInterrupt:
        print("Monitoring stopped.")


if __name__ == "__main__":
    monitor_camera()