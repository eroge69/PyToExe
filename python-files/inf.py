
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial
import struct
import threading
import time
import serial.tools.list_ports

class SRNE_Monitor:
    def __init__(self, master):
        self.master = master
        master.title("SRNE Modbus Monitor")

        # --- Serial Port Configuration ---
        self.port_label = ttk.Label(master, text="COM Port:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_var = tk.StringVar()
        self.port_combobox = ttk.Combobox(master, textvariable=self.port_var, values=self.get_available_ports())
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        if self.get_available_ports():
            self.port_combobox.current(0)
        else:
            messagebox.showerror("Error", "No COM ports found!")

        self.baudrate_label = ttk.Label(master, text="Baud Rate:")
        self.baudrate_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.baudrate_var = tk.StringVar(value="9600")
        self.baudrate_entry = ttk.Entry(master, textvariable=self.baudrate_var)
        self.baudrate_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # --- Device Address ---
        self.address_label = ttk.Label(master, text="Device Address (1-247):")
        self.address_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.address_var = tk.StringVar(value="1")
        self.address_entry = ttk.Entry(master, textvariable=self.address_var)
        self.address_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # --- Connect Button ---
        self.connect_button = ttk.Button(master, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W + tk.E)

        # --- Load Control Buttons ---
        self.on_button = ttk.Button(master, text="Turn Load ON", command=self.turn_load_on)
        self.on_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W + tk.E)

        self.off_button = ttk.Button(master, text="Turn Load OFF", command=self.turn_load_off)
        self.off_button.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        # --- Data Display ---
        self.data_frame = ttk.Frame(master)
        self.data_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W + tk.E)

        self.data_labels = {}
        self.data_values = {}
        self.create_data_display()

        # --- Status Label ---
        self.status_label = ttk.Label(master, text="Status: Not Connected")
        self.status_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # --- Serial Port ---
        self.ser = None
        self.connected = False
        self.stop_event = threading.Event()  # For stopping the data update thread
        self.data_thread = None

    def get_available_ports(self):
        """Lists serial port names."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_serial(self):
        """Connects to the serial port."""
        try:
            port = self.port_var.get()
            baudrate = int(self.baudrate_var.get())

            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.status_label.config(text=f"Status: Connected to {port}")
            self.connected = True

            # Start the data update thread
            self.stop_event.clear()
            self.data_thread = threading.Thread(target=self.update_data_loop)
            self.data_thread.daemon = True  # Thread exits when main program exits
            self.data_thread.start()

        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Could not open serial port: {e}")
            self.status_label.config(text="Status: Not Connected")
            self.connected = False
            self.ser = None
        except ValueError:
            messagebox.showerror("Value Error", "Invalid baud rate. Please enter a number.")
            self.status_label.config(text="Status: Not Connected")
            self.connected = False
            self.ser = None

    def disconnect_serial(self):
        """Disconnects from the serial port."""
        if self.ser:
            self.stop_event.set()  # Stop the data update thread
            self.ser.close()
            self.ser = None
            self.connected = False
            self.status_label.config(text="Status: Disconnected")

    def calculate_crc(self, data):
        """Calculates the Modbus RTU CRC."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def send_modbus_command(self, device_address, function_code, register_address, value=None, num_registers=1):
        """Sends a Modbus command and returns the response."""
        try:
            device_address = int(device_address)
            register_address = int(register_address)
            if value is not None:
                value = int(value)
        except ValueError:
            messagebox.showerror("Value Error", "Invalid device address, register address, or value. Please enter numbers.")
            return None

        if not self.connected:
            messagebox.showerror("Serial Error", "Not connected to serial port.")
            return None

        # Build the Modbus RTU message
        message = bytearray()
        message.append(device_address)  # Device address
        message.append(function_code)  # Function code
        message.extend(register_address.to_bytes(2, 'big'))  # Register address (2 bytes, big-endian)

        if function_code in [0x06, 0x10]:  # Write functions
            message.extend(value.to_bytes(2, 'big'))  # Value (2 bytes, big-endian)
        else:
            message.extend(num_registers.to_bytes(2, 'big')) # Number of registers (2 bytes, big-endian)

        # Calculate CRC
        crc = self.calculate_crc(message)
        message.extend(crc.to_bytes(2, 'little'))  # CRC (2 bytes, little-endian)

        try:
            self.ser.write(bytes(message))
            if function_code in [0x06, 0x10]:
                response = self.ser.read(8)  # Expecting 8 bytes back for write functions
            else:
                response = self.ser.read(5 + (num_registers * 2))  # Adjust based on expected response length
            return response
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Serial communication error: {e}")
            return None

    def read_holding_registers(self, device_address, start_address, num_registers):
        """Reads holding registers and returns the data."""
        response = self.send_modbus_command(device_address, 0x03, start_address, num_registers=num_registers)

        if response:
            try:
                # Validate response
                if response[0] != int(device_address) or response[1] != 3:
                    raise ValueError(f"Invalid response: {response.hex()}")

                byte_count = response[2]
                if byte_count != num_registers * 2:
                    raise ValueError(f"Invalid byte count: {byte_count}")

                # Extract data
                data = []
                for i in range(num_registers):
                    register_value = struct.unpack(">H", response[3 + (i * 2):5 + (i * 2)])[0]  # Big-endian
                    data.append(register_value)
                return data

            except ValueError as e:
                messagebox.showerror("Error", f"Error processing response: {e}")
                return None
        else:
            messagebox.showerror("Error", "No response received.")
            return None

    def turn_load_on(self):
        self.control_load(1)  # 1 for ON

    def turn_load_off(self):
        self.control_load(0)  # 0 for OFF

    def control_load(self, on_off):
        """Controls the load (ON/OFF)."""
        device_address = self.address_var.get()
        register_address = "010A"  # Load On/Off command register (from the PDF)
        value = str(on_off)  # 0 or 1

        response = self.send_modbus_command(device_address, 0x06, int(register_address, 16), int(value))

        if response:
            # Basic response check (adjust based on the SRNE protocol)
            if response[0] == int(device_address) and response[1] == 6:
                messagebox.showinfo("Success", f"Load turned {'ON' if on_off else 'OFF'}")
            else:
                messagebox.showerror("Error", f"Command failed. Response: {response.hex()}")
        else:
            messagebox.showerror("Error", "No response received.")

    def update_data(self):
        """Reads data from the SRNE device and updates the GUI."""
        if not self.connected:
            return

        device_address = self.address_var.get()

        # --- Read System Information (Example) ---
        system_voltage = self.read_system_voltage(device_address)
        if system_voltage is not None:
            self.update_data_value("System Voltage", system_voltage)

        battery_voltage = self.read_battery_voltage(device_address)
        if battery_voltage is not None:
            self.update_data_value("Battery Voltage", battery_voltage)

        load_voltage = self.read_load_voltage(device_address)
        if load_voltage is not None:
            self.update_data_value("Load Voltage", load_voltage)

        load_current = self.read_load_current(device_address)
        if load_current is not None:
            self.update_data_value("Load Current", load_current)

        load_power = self.read_load_power(device_address)
        if load_power is not None:
            self.update_data_value("Load Power", load_power)

        solar_panel_voltage = self.read_solar_panel_voltage(device_address)
        if solar_panel_voltage is not None:
            self.update_data_value("Solar Panel Voltage", solar_panel_voltage)

        solar_panel_current = self.read_solar_panel_current(device_address)
        if solar_panel_current is not None:
            self.update_data_value("Solar Panel Current", solar_panel_current)

        solar_panel_power = self.read_solar_panel_power(device_address)
        if solar_panel_power is not None:
            self.update_data_value("Solar Panel Power", solar_panel_power)

        battery_soc = self.read_battery_soc(device_address)
        if battery_soc is not None:
            self.update_data_value("Battery SOC", battery_soc)

        # --- Read Faults and Warnings ---
        faults = self.read_faults(device_address)
        if faults is not None:
            self.update_data_value("Faults", faults)

    def update_data_loop(self):
        """Updates data periodically in a loop."""
        while not self.stop_event.is_set():
            self.update_data()
            time.sleep(2)  # Update every 2 seconds

    def update_data_value(self, label, value):
        """Updates the value of a data label in the GUI."""
        if label in self.data_values:
            self.data_values[label].set(str(value))

    def create_data_display(self):
        """Creates the labels and value displays in the GUI."""
        row = 0
        # --- System Information ---
        self.create_data_row(row, "System Voltage", "V")
        row += 1
        self.create_data_row(row, "Battery Voltage", "V")
        row += 1
        self.create_data_row(row, "Load Voltage", "V")
        row += 1
        self.create_data_row(row, "Load Current", "A")
        row += 1
        self.create_data_row(row, "Load Power", "W")
        row += 1
        self.create_data_row(row, "Solar Panel Voltage", "V")
        row += 1
        self.create_data_row(row, "Solar Panel Current", "A")
        row += 1
        self.create_data_row(row, "Solar Panel Power", "W")
        row += 1
        self.create_data_row(row, "Battery SOC", "%")
        row += 1
        self.create_data_row(row, "Faults", "")
        row += 1

    def create_data_row(self, row, label_text, unit):
        """Creates a row in the data display."""
        label = ttk.Label(self.data_frame, text=label_text + ":")
        label.grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
        self.data_labels[label_text] = label

        value_var = tk.StringVar(value="N/A")
        value_label = ttk.Label(self.data_frame, textvariable=value_var)
        value_label.grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
        self.data_values[label_text] = value_var

        unit_label = ttk.Label(self.data_frame, text=unit)
        unit_label.grid(row=row, column=2, padx=5, pady=2, sticky=tk.W)

    # --- Data Reading Functions (Example) ---
    def read_system_voltage(self, device_address):
        """Reads the system voltage."""
        data = self.read_holding_registers(device_address, 0x000A, 1)
        if data:
            system_voltage_code = data[0]
            if system_voltage_code == 12:
                return "12V"
            elif system_voltage_code == 24:
                return "24V"
            elif system_voltage_code == 36:
                return "36V"
            elif system_voltage_code == 48:
                return "48V"
            elif system_voltage_code == 96:
                return "96V"
            elif system_voltage_code == 255:
                return "Automatic Recognition"
            else:
                return "Unknown"
        return None

    def read_battery_voltage(self, device_address):
        """Reads the battery voltage."""
        data = self.read_holding_registers(device_address, 0x0101, 1)
        if data:
            return data[0] * 0.1  # Battery voltage * 0.1
        return None

    def read_load_voltage(self, device_address):
        """Reads the load voltage."""
        data = self.read_holding_registers(device_address, 0x0104, 1)
        if data:
            return data[0] * 0.1  # Load voltage * 0.1
        return None

    def read_load_current(self, device_address):
        """Reads the load current."""
        data = self.read_holding_registers(device_address, 0x0105, 1)
        if data:
            return data[0] * 0.01  # Load current * 0.01
        return None

    def read_load_power(self, device_address):
        """Reads the load power."""
        data = self.read_holding_registers(device_address, 0x0106, 1)
        if data:
            return data[0]  # Load power
        return None

    def read_solar_panel_voltage(self, device_address):
        """Reads the solar panel voltage."""
        data = self.read_holding_registers(device_address, 0x0107, 1)
        if data:
            return data[0] * 0.1  # Solar panel voltage * 0.1
        return None

    def read_solar_panel_current(self, device_address):
        """Reads the solar panel current."""
        data = self.read_holding_registers(device_address, 0x0108, 1)
        if data:
            return data[0] * 0.01  # Solar panel current * 0.01
        return None

    def read_solar_panel_power(self, device_address):
        """Reads the solar panel power."""
        data = self.read_holding_registers(device_address, 0x0109, 1)
        if data:
            return data[0]  # Solar panel power
        return None

    def read_battery_soc(self, device_address):
        """Reads the battery SOC."""
        data = self.read_holding_registers(device_address, 0x0100, 1)
        if data:
            return data[0]  # Battery SOC
        return None

    def read_faults(self, device_address):
        """Reads the faults."""
        data_high = self.read_holding_registers(device_address, 0x0121, 1)
        data_low = self.read_holding_registers(device_address, 0x0122, 1)
        if data_high and data_low:
            fault_high = data_high[0]
            fault_low = data_low[0]
            return f"High: 0x{fault_high:04X}, Low: 0x{fault_low:04X}"
        return None

    def on_closing(self):
        """Handles the window closing event."""
        self.disconnect_serial()
        self.master.destroy()

root = tk.Tk()
app = SRNE_Monitor(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Handle window closing
root.mainloop()
