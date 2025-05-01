import sys
import serial
import serial.tools.list_ports
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit, QGroupBox,
                             QSpinBox, QFormLayout, QCheckBox, QFileDialog)
from PyQt5.QtCore import QTimer, Qt


class SerialConfigWidget(QGroupBox):
    """Widget for serial port configuration"""
    def __init__(self, parent=None):
        super().__init__("Serial Port Configuration", parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QFormLayout()
        
        # Port selection
        self.port_combo = QComboBox()
        self.refresh_ports()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.refresh_btn)
        
        # Baud rate
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800"])
        self.baud_combo.setCurrentText("115200")
        
        # Data bits
        self.databits_combo = QComboBox()
        self.databits_combo.addItems(["5", "6", "7", "8"])
        self.databits_combo.setCurrentText("8")
        
        # Parity
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["None", "Even", "Odd", "Mark", "Space"])
        self.parity_combo.setCurrentText("None")
        
        # Stop bits
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(["1", "1.5", "2"])
        self.stopbits_combo.setCurrentText("1")
        
        # Flow control
        self.flow_ctrl_combo = QComboBox()
        self.flow_ctrl_combo.addItems(["None", "XON/XOFF", "RTS/CTS", "DSR/DTR"])
        self.flow_ctrl_combo.setCurrentText("None")
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(1)
        self.timeout_spin.setSuffix(" sec")
        
        layout.addRow("Port:", port_layout)
        layout.addRow("Baud Rate:", self.baud_combo)
        layout.addRow("Data Bits:", self.databits_combo)
        layout.addRow("Parity:", self.parity_combo)
        layout.addRow("Stop Bits:", self.stopbits_combo)
        layout.addRow("Flow Control:", self.flow_ctrl_combo)
        layout.addRow("Timeout:", self.timeout_spin)
        
        self.setLayout(layout)
    
    def refresh_ports(self):
        """Refresh available serial ports"""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device, port.device)
        if not ports:
            self.port_combo.addItem("No ports available", None)
    
    def get_config(self):
        """Return current configuration as a dict"""
        return {
            "port": self.port_combo.currentData(),
            "baudrate": int(self.baud_combo.currentText()),
            "bytesize": int(self.databits_combo.currentText()),
            "parity": self.parity_combo.currentText()[0],  # First letter for serial.PARITY_*
            "stopbits": float(self.stopbits_combo.currentText()),
            "xonxoff": self.flow_ctrl_combo.currentText() == "XON/XOFF",
            "rtscts": self.flow_ctrl_combo.currentText() == "RTS/CTS",
            "dsrdtr": self.flow_ctrl_combo.currentText() == "DSR/DTR",
            "timeout": self.timeout_spin.value()
        }


class SerialMonitor(QMainWindow):
    """Main application window for serial monitoring"""
    def __init__(self):
        super().__init__()
        self.serial = None
        self.data_buffer = ""
        self.measurements = {
            "Voltage": 0.0,
            "Current": 0.0,
            "Active Power": 0.0,
            "Positive Active Energy": 0.0
        }
        self.init_ui()
        self.init_serial()
        
    def init_ui(self):
        self.setWindowTitle("STM32 Serial Data Monitor")
        self.setGeometry(100, 100, 800, 600)
        
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Serial configuration
        self.serial_config = SerialConfigWidget()
        layout.addWidget(self.serial_config)
        
        # Connection controls
        self.connect_btn = QPushButton("Open Port")
        self.connect_btn.clicked.connect(self.toggle_serial_connection)
        self.clear_btn = QPushButton("Clear Data")
        self.clear_btn.clicked.connect(self.clear_data)
        self.save_btn = QPushButton("Save Data")
        self.save_btn.clicked.connect(self.save_data)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        # Data display
        self.raw_data_display = QTextEdit()
        self.raw_data_display.setReadOnly(True)
        self.raw_data_display.setPlaceholderText("Raw serial data will appear here...")
        
        # Measurement display
        self.measurement_group = QGroupBox("Measurements")
        measurement_layout = QFormLayout()
        
        self.voltage_label = QLabel("0.00 V")
        self.current_label = QLabel("0.00 A")
        self.power_label = QLabel("0.00 W")
        self.energy_label = QLabel("0.00 Wh")
        
        measurement_layout.addRow("Voltage:", self.voltage_label)
        measurement_layout.addRow("Current:", self.current_label)
        measurement_layout.addRow("Active Power:", self.power_label)
        measurement_layout.addRow("Positive Active Energy:", self.energy_label)
        
        self.measurement_group.setLayout(measurement_layout)
        
        # Add displays to layout
        layout.addWidget(self.raw_data_display)
        layout.addWidget(self.measurement_group)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        # Timer for reading serial data
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        
    def init_serial(self):
        """Initialize serial connection"""
        self.serial = None
        self.connect_btn.setText("Open Port")
        self.timer.stop()
    
    def toggle_serial_connection(self):
        """Toggle serial connection on/off"""
        if self.serial and self.serial.is_open:
            self.close_serial_connection()
            self.connect_btn.setText("Open Port")
        else:
            if self.open_serial_connection():
                self.connect_btn.setText("Close Port")
                self.timer.start(50)  # Check for data every 50ms
    
    def open_serial_connection(self):
        """Open serial connection with current configuration"""
        config = self.serial_config.get_config()
        
        if not config["port"]:
            self.raw_data_display.append("Error: No port selected!")
            return False
            
        try:
            self.serial = serial.Serial(
                port=config["port"],
                baudrate=config["baudrate"],
                bytesize=config["bytesize"],
                parity=config["parity"],
                stopbits=config["stopbits"],
                xonxoff=config["xonxoff"],
                rtscts=config["rtscts"],
                dsrdtr=config["dsrdtr"],
                timeout=config["timeout"]
            )
            self.raw_data_display.append(f"Connected to {config['port']} at {config['baudrate']} baud")
            return True
        except serial.SerialException as e:
            self.raw_data_display.append(f"Error opening port: {str(e)}")
            return False
    
    def close_serial_connection(self):
        """Close serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.raw_data_display.append("Serial port closed")
        self.serial = None
    
    def read_serial_data(self):
        """Read data from serial port and update displays"""
        if not self.serial or not self.serial.is_open:
            return
            
        try:
            # Read all available data
            data = self.serial.read(self.serial.in_waiting or 1).decode('ascii', errors='replace')
            
            if data:
                # Add to raw data display
                self.raw_data_display.moveCursor(self.raw_data_display.textCursor().End)
                self.raw_data_display.insertPlainText(data)
                
                # Buffer data for parsing
                self.data_buffer += data
                
                # Process complete lines
                while '\n' in self.data_buffer:
                    line, self.data_buffer = self.data_buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        self.process_line(line)
                
                # Auto-scroll
                self.raw_data_display.ensureCursorVisible()
                
        except serial.SerialException as e:
            self.raw_data_display.append(f"Serial error: {str(e)}")
            self.close_serial_connection()
            self.connect_btn.setText("Open Port")
    
    def process_line(self, line):
        """Parse a line of data and update measurements"""
        try:
            # Example line: "Voltage\t\t\t:12.34"
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Clean up key by removing extra whitespace and tabs
                key = ' '.join(key.split())
                
                # Update measurement if key is recognized
                if key in self.measurements:
                    try:
                        self.measurements[key] = float(value)
                        self.update_measurement_display()
                    except ValueError:
                        pass  # Ignore lines with invalid numbers
                        
        except Exception as e:
            # Just skip any lines that don't match our expected format
            pass
    
    def update_measurement_display(self):
        """Update the measurement display with current values"""
        self.voltage_label.setText(f"{self.measurements['Voltage']:.2f} V")
        self.current_label.setText(f"{self.measurements['Current']:.2f} A")
        self.power_label.setText(f"{self.measurements['Active Power']:.2f} W")
        self.energy_label.setText(f"{self.measurements['Positive Active Energy']:.2f} Wh")
    
    def clear_data(self):
        """Clear the data displays"""
        self.raw_data_display.clear()
        self.data_buffer = ""
        
        # Reset measurements
        for key in self.measurements:
            self.measurements[key] = 0.0
        self.update_measurement_display()
    
    def save_data(self):
        """Save the raw data to a file"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.raw_data_display.toPlainText())
                self.raw_data_display.append(f"Data saved to {file_name}")
            except IOError as e:
                self.raw_data_display.append(f"Error saving file: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.close_serial_connection()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = SerialMonitor()
    monitor.show()
    sys.exit(app.exec_())
