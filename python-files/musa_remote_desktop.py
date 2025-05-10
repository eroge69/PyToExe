import os
import sys
import subprocess
import socket
import platform
import re
import time
import json
import ctypes
import win32com.client
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QComboBox, QListWidget, 
                            QTabWidget, QMessageBox, QCheckBox, QSpinBox, QFileDialog,
                            QSystemTrayIcon, QMenu, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QCursor

class MusaInstaller:
    @staticmethod
    def create_desktop_shortcut():
        """Create a desktop shortcut for the application"""
        try:
            if platform.system() == 'Windows':
                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                shortcut_path = os.path.join(desktop, 'Musa Remote Desktop.lnk')
                
                if not os.path.exists(shortcut_path):
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.TargetPath = sys.executable
                    shortcut.Arguments = f'"{os.path.abspath(__file__)}"'
                    shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
                    shortcut.IconLocation = sys.executable
                    shortcut.save()
                return True
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False

    @staticmethod
    def install_dependencies():
        """Install required Python packages"""
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyqt5', 'pywin32'])
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False

class VPNManager:
    @staticmethod
    def is_vpn_active():
        """Check if VPN is active on the system"""
        try:
            if platform.system() == 'Windows':
                # Check for common VPN interface names
                result = subprocess.run(['powershell', 'Get-NetAdapter | Where-Object {$_.InterfaceDescription -match "VPN"} | Select-Object -ExpandProperty Status'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return "Up" in result.stdout
            else:
                # Linux/Mac - check for tun/tap interfaces
                result = subprocess.run(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return "tun" in result.stdout or "tap" in result.stdout
        except Exception:
            return False

    @staticmethod
    def get_vpn_server_ip():
        """Try to detect VPN server IP"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['powershell', 'Get-VpnConnection | Select-Object -ExpandProperty ServerAddress'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.stdout.strip()
        except Exception:
            return None

class DNSChecker:
    @staticmethod
    def flush_dns():
        """Flush DNS cache"""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['ipconfig', '/flushdns'], check=True)
            elif platform.system() == 'Linux':
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_dns_servers():
        """Get current DNS servers"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['powershell', 'Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.stdout.strip().split()
            else:
                # Linux/Mac
                with open('/etc/resolv.conf', 'r') as f:
                    lines = f.readlines()
                    return [line.split()[1] for line in lines if line.startswith('nameserver')]
        except Exception:
            return []

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.connection_timeout = 10  # seconds
        
    def create_connection(self, session_data):
        """Create a new remote connection"""
        connection_type = session_data.get('type', 'vnc').lower()
        host = session_data.get('host', '')
        port = session_data.get('port', 5900 if connection_type == 'vnc' else 3389)
        username = session_data.get('username', '')
        password = session_data.get('password', '')
        
        try:
            if connection_type == 'vnc':
                return self._create_vnc_connection(host, port, password)
            elif connection_type == 'rdp':
                return self._create_rdp_connection(host, port, username, password)
            elif connection_type == 'ssh':
                return self._create_ssh_connection(host, port, username, password)
            else:
                return False, "Unsupported connection type"
        except Exception as e:
            return False, str(e)
    
    def _create_vnc_connection(self, host, port, password):
        """Create VNC connection"""
        vnc_client = self._find_vnc_client()
        if not vnc_client:
            return False, "No VNC client found"
        
        cmd = [vnc_client, f"{host}::{port}"]
        if password:
            cmd.extend(['-passwd', password])
        
        try:
            process = subprocess.Popen(cmd)
            self.active_connections.append(process)
            return True, f"VNC connection started to {host}:{port}"
        except Exception as e:
            return False, str(e)
    
    def _create_rdp_connection(self, host, port, username, password):
        """Create RDP connection"""
        if platform.system() == 'Windows':
            cmd = ['mstsc', '/v:', f"{host}:{port}"]
            try:
                process = subprocess.Popen(cmd)
                self.active_connections.append(process)
                return True, f"RDP connection started to {host}:{port}"
            except Exception as e:
                return False, str(e)
        else:
            # For Linux/Mac, use xfreerdp or similar
            cmd = ['xfreerdp', f'/v:{host}:{port}', '/f']
            if username:
                cmd.extend([f'/u:{username}'])
            if password:
                cmd.extend([f'/p:{password}'])
            
            try:
                process = subprocess.Popen(cmd)
                self.active_connections.append(process)
                return True, f"RDP connection started to {host}:{port}"
            except Exception as e:
                return False, str(e)
    
    def _create_ssh_connection(self, host, port, username, password):
        """Create SSH connection"""
        if platform.system() == 'Windows':
            cmd = ['putty', '-ssh', f"{username}@{host}", '-P', str(port)]
            if password:
                # Note: Putty doesn't support password in command line for security reasons
                pass
        else:
            cmd = ['ssh', '-p', str(port), f"{username}@{host}"]
        
        try:
            process = subprocess.Popen(cmd)
            self.active_connections.append(process)
            return True, f"SSH connection started to {host}:{port}"
        except Exception as e:
            return False, str(e)
    
    def _find_vnc_client(self):
        """Find installed VNC client"""
        clients = ['vncviewer', 'tightvnc', 'tigervnc', 'remmina', 'ultravnc']
        for client in clients:
            try:
                if platform.system() == 'Windows':
                    subprocess.run(['where', client], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    subprocess.run(['which', client], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return client
            except subprocess.CalledProcessError:
                continue
        return None
    
    def close_all_connections(self):
        """Close all active connections"""
        for process in self.active_connections:
            try:
                process.terminate()
            except:
                pass
        self.active_connections = []
        return True, "All connections closed"

class AutoFixThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, session_data):
        super().__init__()
        self.session_data = session_data
        self.connection_manager = ConnectionManager()
    
    def run(self):
        host = self.session_data.get('host', '')
        port = self.session_data.get('port', 5900)
        connection_type = self.session_data.get('type', 'vnc').lower()
        
        self.update_signal.emit("Starting auto-fix procedure...")
        
        # Step 1: Check host resolution
        self.update_signal.emit("\n1. Checking host resolution...")
        try:
            ip = socket.gethostbyname(host)
            self.update_signal.emit(f"   ✓ Resolved to: {ip}")
        except socket.gaierror:
            self.update_signal.emit("   ✗ Failed to resolve hostname")
            # Try flushing DNS
            if DNSChecker.flush_dns():
                self.update_signal.emit("   ✓ Flushed DNS cache")
                try:
                    ip = socket.gethostbyname(host)
                    self.update_signal.emit(f"   ✓ Resolved to: {ip} after DNS flush")
                except socket.gaierror:
                    self.finished_signal.emit(False, "Host resolution failed")
                    return
            else:
                self.finished_signal.emit(False, "Host resolution failed")
                return
        
        # Step 2: Check port connectivity
        self.update_signal.emit("\n2. Checking port connectivity...")
        if not self._check_port(ip, port):
            self.update_signal.emit(f"   ✗ Port {port} is not responding")
            
            # Try common ports for the service
            common_ports = {
                'vnc': [5900, 5901, 5902, 5800, 5801],
                'rdp': [3389, 3390],
                'ssh': [22, 2222]
            }.get(connection_type, [port])
            
            self.update_signal.emit(f"   Trying common {connection_type.upper()} ports...")
            for test_port in common_ports:
                if self._check_port(ip, test_port):
                    self.session_data['port'] = test_port
                    self.update_signal.emit(f"   ✓ Found working port: {test_port}")
                    break
            else:
                self.finished_signal.emit(False, "No working port found")
                return
        else:
            self.update_signal.emit(f"   ✓ Port {port} is responding")
        
        # Step 3: Check VPN status
        self.update_signal.emit("\n3. Checking VPN status...")
        if VPNManager.is_vpn_active():
            vpn_server = VPNManager.get_vpn_server_ip()
            self.update_signal.emit(f"   ✓ VPN detected (Server: {vpn_server or 'Unknown'})")
            
            # Check if host is in private IP range
            if self._is_private_ip(ip):
                self.update_signal.emit("   ✓ Host is in private IP range (VPN connection should work)")
            else:
                self.update_signal.emit("   ! Host is not in private IP range (check VPN routing)")
        else:
            self.update_signal.emit("   ✓ No VPN detected")
        
        # Step 4: Check required client software
        self.update_signal.emit("\n4. Checking client software...")
        if connection_type == 'vnc':
            client = self.connection_manager._find_vnc_client()
            if client:
                self.update_signal.emit(f"   ✓ Found VNC client: {client}")
            else:
                self.update_signal.emit("   ✗ No VNC client found")
                self.finished_signal.emit(False, "VNC client not installed")
                return
        
        self.update_signal.emit("\nAuto-fix completed successfully!")
        self.finished_signal.emit(True, "Auto-fix completed")
    
    def _check_port(self, host, port, timeout=2):
        """Check if port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return s.connect_ex((host, port)) == 0
        except Exception:
            return False
    
    def _is_private_ip(self, ip):
        """Check if IP is in private range"""
        priv_ranges = [
            ('10.0.0.0', '10.255.255.255'),
            ('172.16.0.0', '172.31.255.255'),
            ('192.168.0.0', '192.168.255.255')
        ]
        
        ip_num = int(''.join(f"{int(x):03d}" for x in ip.split('.')), 10)
        for start, end in priv_ranges:
            start_num = int(''.join(f"{int(x):03d}" for x in start.split('.')), 10)
            end_num = int(''.join(f"{int(x):03d}" for x in end.split('.')), 10)
            if start_num <= ip_num <= end_num:
                return True
        return False

class MusaTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon.fromTheme('applications-internet'))
        
        menu = QMenu(parent)
        self.show_action = menu.addAction("Show Musa")
        self.show_action.triggered.connect(parent.show)
        menu.addSeparator()
        self.exit_action = menu.addAction("Exit")
        self.exit_action.triggered.connect(parent.close)
        
        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_activate)
    
    def on_tray_activate(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.parent().show()

class MusaMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Musa - Advanced Remote Desktop Manager")
        self.setWindowIcon(QIcon.fromTheme('applications-internet'))
        self.resize(1000, 700)
        
        # Initialize components
        self.connection_manager = ConnectionManager()
        self.sessions = []
        self.current_session = None
        self.config_file = os.path.join(os.path.expanduser('~'), '.musa_sessions.json')
        
        # Setup UI
        self.setup_ui()
        
        # Load saved sessions
        self.load_sessions()
        
        # Setup system tray
        self.tray_icon = MusaTrayIcon(self)
        self.tray_icon.show()
        
        # Check for first run
        self.check_first_run()
    
    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel - session list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.load_session)
        self.session_list.itemDoubleClicked.connect(self.connect_to_session)
        left_layout.addWidget(QLabel("Saved Sessions:"))
        left_layout.addWidget(self.session_list)
        
        # Session buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_session)
        btn_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_session)
        btn_layout.addWidget(self.remove_btn)
        
        left_layout.addLayout(btn_layout)
        left_panel.setLayout(left_layout)
        
        # Right panel - session details and tools
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        
        # Connection tab
        connection_tab = QWidget()
        connection_layout = QVBoxLayout()
        
        # Session type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["VNC", "RDP", "SSH"])
        type_layout.addWidget(self.type_combo)
        connection_layout.addLayout(type_layout)
        
        # Host
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host:"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("hostname or IP address")
        host_layout.addWidget(self.host_input)
        connection_layout.addLayout(host_layout)
        
        # Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5900)
        port_layout.addWidget(self.port_input)
        
        self.auto_port_check = QCheckBox("Auto-detect")
        self.auto_port_check.setChecked(True)
        port_layout.addWidget(self.auto_port_check)
        connection_layout.addLayout(port_layout)
        
        # Credentials
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Username:"))
        self.user_input = QLineEdit()
        user_layout.addWidget(self.user_input)
        connection_layout.addLayout(user_layout)
        
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.pass_input)
        connection_layout.addLayout(pass_layout)
        
        # Display name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Display Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        connection_layout.addLayout(name_layout)
        
        # Save/Connect buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_session)
        button_layout.addWidget(self.save_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_to_session)
        button_layout.addWidget(self.connect_btn)
        
        connection_layout.addLayout(button_layout)
        connection_tab.setLayout(connection_layout)
        self.tabs.addTab(connection_tab, "Connection")
        
        # Troubleshooting tab
        trouble_tab = QWidget()
        trouble_layout = QVBoxLayout()
        
        self.trouble_log = QLabel("Troubleshooting log will appear here...")
        self.trouble_log.setWordWrap(True)
        self.trouble_log.setAlignment(Qt.AlignTop)
        trouble_layout.addWidget(self.trouble_log)
        
        self.auto_fix_btn = QPushButton("Auto Fix")
        self.auto_fix_btn.clicked.connect(self.run_auto_fix)
        trouble_layout.addWidget(self.auto_fix_btn)
        
        trouble_tab.setLayout(trouble_layout)
        self.tabs.addTab(trouble_tab, "Troubleshooting")
        
        # Status bar
        self.status_bar = QLabel()
        self.status_bar.setAlignment(Qt.AlignCenter)
        self.status_bar.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        
        right_layout.addWidget(self.tabs)
        right_layout.addWidget(self.status_bar)
        right_panel.setLayout(right_layout)
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
    
    def check_first_run(self):
        """Check if this is the first run and perform initial setup"""
        first_run = not os.path.exists(self.config_file)
        if first_run:
            # Create desktop shortcut
            MusaInstaller.create_desktop_shortcut()
            
            # Check for dependencies
            if not self.connection_manager._find_vnc_client():
                self.prompt_vnc_install()
    
    def prompt_vnc_install(self):
        reply = QMessageBox.question(
            self, 'VNC Client Required',
            'No VNC client detected. Would you like to install TigerVNC now?',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.install_vnc_client()
    
    def install_vnc_client(self):
        self.status_bar.setText("Installing VNC client...")
        
        if platform.system() == 'Windows':
            try:
                subprocess.run(['winget', 'install', 'TigerVNC.TigerVNC', '-e'], check=True)
                self.status_bar.setText("VNC client installed successfully!")
            except subprocess.CalledProcessError:
                self.status_bar.setText("Failed to install VNC client")
    
    def load_sessions(self):
        """Load saved sessions from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.sessions = json.load(f)
                    self.update_session_list()
        except Exception as e:
            self.status_bar.setText(f"Error loading sessions: {str(e)}")
    
    def save_sessions(self):
        """Save sessions to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            self.status_bar.setText(f"Error saving sessions: {str(e)}")
    
    def update_session_list(self):
        """Update the session list widget"""
        self.session_list.clear()
        for session in self.sessions:
            name = session.get('name', f"{session.get('host', 'Unknown')}:{session.get('port', '?')}")
            self.session_list.addItem(name)
    
    def add_session(self):
        """Add a new empty session"""
        self.current_session = None
        self.type_combo.setCurrentIndex(0)
        self.host_input.clear()
        self.port_input.setValue(5900)
        self.user_input.clear()
        self.pass_input.clear()
        self.name_input.clear()
    
    def remove_session(self):
        """Remove the selected session"""
        if not self.session_list.currentItem():
            return
        
        index = self.session_list.currentIndex().row()
        if 0 <= index < len(self.sessions):
            reply = QMessageBox.question(
                self, 'Confirm Delete',
                'Are you sure you want to delete this session?',
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                del self.sessions[index]
                self.save_sessions()
                self.update_session_list()
                self.add_session()
    
    def load_session(self, item):
        """Load session details into the form"""
        index = self.session_list.row(item)
        if 0 <= index < len(self.sessions):
            self.current_session = index
            session = self.sessions[index]
            
            # Set type
            type_map = {'vnc': 0, 'rdp': 1, 'ssh': 2}
            self.type_combo.setCurrentIndex(type_map.get(session.get('type', 'vnc'), 0))
            
            # Set other fields
            self.host_input.setText(session.get('host', ''))
            self.port_input.setValue(session.get('port', 5900))
            self.user_input.setText(session.get('username', ''))
            self.pass_input.setText(session.get('password', ''))
            self.name_input.setText(session.get('name', ''))
    
    def save_session(self):
        """Save the current session"""
        session_data = {
            'type': self.type_combo.currentText().lower(),
            'host': self.host_input.text(),
            'port': self.port_input.value(),
            'username': self.user_input.text(),
            'password': self.pass_input.text(),
            'name': self.name_input.text() or f"{self.host_input.text()}:{self.port_input.value()}"
        }
        
        if not session_data['host']:
            QMessageBox.warning(self, "Error", "Host cannot be empty!")
            return
        
        if self.current_session is not None:
            # Update existing session
            self.sessions[self.current_session] = session_data
        else:
            # Add new session
            self.sessions.append(session_data)
        
        self.save_sessions()
        self.update_session_list()
        self.status_bar.setText("Session saved successfully!")
    
    def connect_to_session(self):
        """Connect to the selected session"""
        if not self.session_list.currentItem():
            QMessageBox.warning(self, "Error", "No session selected!")
            return
        
        index = self.session_list.currentIndex().row()
        if 0 <= index < len(self.sessions):
            session = self.sessions[index]
            
            # Check if we should auto-detect port
            if self.auto_port_check.isChecked():
                self.run_auto_fix(session)
            else:
                success, message = self.connection_manager.create_connection(session)
                self.status_bar.setText(message)
                
                if not success:
                    QMessageBox.warning(self, "Connection Failed", message)
    
    def run_auto_fix(self, session=None):
        """Run auto-fix procedure for the selected session"""
        if session is None:
            if not self.session_list.currentItem():
                QMessageBox.warning(self, "Error", "No session selected!")
                return
            
            index = self.session_list.currentIndex().row()
            if 0 <= index < len(self.sessions):
                session = self.sessions[index]
            else:
                return
        
        self.trouble_log.setText("Starting auto-fix...")
        
        # Create and start auto-fix thread
        self.auto_fix_thread = AutoFixThread(session)
        self.auto_fix_thread.update_signal.connect(self.update_trouble_log)
        self.auto_fix_thread.finished_signal.connect(self.auto_fix_finished)
        self.auto_fix_thread.start()
    
    def update_trouble_log(self, message):
        """Update the troubleshooting log"""
        self.trouble_log.setText(self.trouble_log.text() + "\n" + message)
    
    def auto_fix_finished(self, success, message):
        """Handle auto-fix completion"""
        if success:
            self.trouble_log.setText(self.trouble_log.text() + "\n" + message)
            self.status_bar.setText("Auto-fix completed successfully!")
            
            # Try to connect after successful fix
            index = self.session_list.currentIndex().row()
            if 0 <= index < len(self.sessions):
                session = self.sessions[index]
                success, message = self.connection_manager.create_connection(session)
                self.status_bar.setText(message)
        else: 

self.trouble_log.setText(self.trouble_log.text() + "\n" + message)
            self.status_bar.setText("Auto-fix failed!")
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, 'Exit Musa',
            'Do you want to minimize to system tray instead of exiting?',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        
        if reply == QMessageBox.Yes:
            self.hide()
            event.ignore()
        elif reply == QMessageBox.No:
            self.connection_manager.close_all_connections()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    # Check and install dependencies if needed
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        MusaInstaller.install_dependencies()
    
    # Create desktop shortcut if it doesn't exist
    MusaInstaller.create_desktop_shortcut()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MusaMainWindow()
    window.show()
    
    sys.exit(app.exec_())