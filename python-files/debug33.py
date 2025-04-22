import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import math
import socket
import collections


class PositionReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AZ/EL Position Reader")
        self.root.geometry("900x800")  # Increased window size to accommodate graphs

        self.comm_type = tk.StringVar(value="Serial")  # Default to Serial
        self.is_slave_rate_mode = False  # Track if we're in slave rate mode
        self.active_mode = None  # Track which mode is currently active

        self.serial_port = serial.Serial()
        self.socket_client = None

        self.polling = False
        self.sinusoidal_running = False

        self.last_az = ""
        self.last_el = ""

        # For slider auto-return
        self.az_slider_pressed = False
        self.el_slider_pressed = False

        # For position command buttons
        self.button_press_active = False
        self.current_button = None
        self.continuous_sending = False

        # Define mode colors
        self.mode_colors = {
            "Standby": "#838B8B",  # Light salmon
            "Point": "#FF4040",  # Light green
            "Search": "#76EE00",  # Light blue
            "Slave Pos": "#EE7621",  # Light yellow
            "Slave Rate": "#BF3EFF"  # Thistle (light purple)
        }

        # Create a style for the highlighted button
        self.style = ttk.Style()
        self.style.configure("Active.TButton", background="red")

        # Data storage for graphs
        self.max_data_points = 100  # Store up to 100 data points
        self.az_commanded = collections.deque(maxlen=self.max_data_points)
        self.az_actual = collections.deque(maxlen=self.max_data_points)
        self.el_commanded = collections.deque(maxlen=self.max_data_points)
        self.el_actual = collections.deque(maxlen=self.max_data_points)
        self.az_error = collections.deque(maxlen=self.max_data_points)
        self.el_error = collections.deque(maxlen=self.max_data_points)
        self.timestamps = collections.deque(maxlen=self.max_data_points)
        self.start_time = time.time()

        # Last commanded values
        self.last_commanded_az = 0.0
        self.last_commanded_el = 0.0

        self.create_widgets()

    def create_widgets(self):
        # Create a main frame for all controls
        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Communication Type Selection
        ttk.Label(self.controls_frame, text="Communication Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.comm_type_frame = ttk.Frame(self.controls_frame)
        self.comm_type_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Radiobutton(self.comm_type_frame, text="Serial", variable=self.comm_type, value="Serial",
                        command=self.update_connection_settings).pack(side="left")
        ttk.Radiobutton(self.comm_type_frame, text="Socket", variable=self.comm_type, value="Socket",
                        command=self.update_connection_settings).pack(side="left")

        # Serial Port Settings Frame
        self.serial_settings_frame = ttk.LabelFrame(self.controls_frame, text="Serial Port Settings")
        self.serial_settings_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(self.serial_settings_frame, text="Port:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.port_combo = ttk.Combobox(self.serial_settings_frame, values=self.get_serial_ports(), width=15)
        self.port_combo.set("Select")
        self.port_combo.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(self.serial_settings_frame, text="Baudrate:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.baud_combo = ttk.Combobox(self.serial_settings_frame, values=[9600, 19200, 38400, 57600, 115200], width=15)
        self.baud_combo.set("115200")
        self.baud_combo.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(self.serial_settings_frame, text="Parity:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.parity_combo = ttk.Combobox(self.serial_settings_frame, values=['None', 'Even', 'Odd', 'Mark', 'Space'],
                                         width=15)
        self.parity_combo.set("None")
        self.parity_combo.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # Socket Settings Frame
        self.socket_settings_frame = ttk.LabelFrame(self.controls_frame, text="Socket Settings")
        self.socket_settings_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(self.socket_settings_frame, text="Socket IP:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.socket_ip_entry = ttk.Entry(self.socket_settings_frame, width=15)
        self.socket_ip_entry.insert(0, "10.0.0.100")
        self.socket_ip_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(self.socket_settings_frame, text="Port:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.socket_port_entry = ttk.Entry(self.socket_settings_frame, width=7)
        self.socket_port_entry.insert(0, "5003")
        self.socket_port_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Connect Button (under communication settings)
        self.connect_button = ttk.Button(self.controls_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        # TX Log Window
        ttk.Label(self.controls_frame, text="TX ASCII Log:").grid(row=4, column=0, sticky="nw")
        self.tx_log = tk.Text(self.controls_frame, width=30, height=2)
        self.tx_log.grid(row=4, column=1, columnspan=5, padx=10)

        # Command Buttons (under TX log)
        commands = [("Standby", "P2W0"), ("Point", "P2W7"), ("Search", "P2W6"),
                    ("Slave Pos", "P2W3"), ("Slave Rate", "P2W18")]

        self.command_buttons = {}  # Store references to buttons
        self.command_labels_frame = ttk.Frame(self.controls_frame)
        self.command_labels_frame.grid(row=12, column=0, columnspan=5, padx=5, pady=2)
        ttk.Label(self.command_labels_frame, text="Mode:", font=('Helvetica', 9, 'bold')).pack(side=tk.LEFT, padx=5)

        # Mode indicator label
        self.mode_indicator = ttk.Label(self.command_labels_frame, text="None", font=('Helvetica', 9, 'italic'))
        self.mode_indicator.pack(side=tk.LEFT, padx=5)

        for i, (label, cmd) in enumerate(commands):
            # Create a themed button with custom style for each command
            btn = ttk.Button(self.controls_frame, text=label,
                             command=lambda c=cmd, l=label: self.send_command_and_update(c, l))
            btn.grid(row=11, column=i)
            self.command_buttons[label] = btn

            # Create a special style just for this button
            style_name = f"{label}.TButton"
            self.style.configure(style_name, background=self.mode_colors[label])

        # RX Log Window
        ttk.Label(self.controls_frame, text="RX ASCII Log:").grid(row=6, column=0, sticky="nw")
        self.rx_log = tk.Text(self.controls_frame, width=30, height=3)
        self.rx_log.grid(row=6, column=1, columnspan=5, padx=10)

        # AZ/EL Position Display
        ttk.Label(self.controls_frame, text="AZ Position (P7):").grid(row=7, column=0)
        self.az_entry = ttk.Entry(self.controls_frame, width=15)
        self.az_entry.grid(row=7, column=1)

        ttk.Label(self.controls_frame, text="EL Position (P8):").grid(row=8, column=0)
        self.el_entry = ttk.Entry(self.controls_frame, width=15)
        self.el_entry.grid(row=8, column=1)

        # AZ/EL Position or Slave Rate Inputs
        self.az_pos_slave_rate = ttk.Entry(self.controls_frame, width=15)
        self.az_pos_slave_rate.grid(row=9, column=1)
        ttk.Label(self.controls_frame, text="AZ Position / Slave Rate:").grid(row=9, column=0)
        self.el_pos_slave_rate = ttk.Entry(self.controls_frame, width=15)
        self.el_pos_slave_rate.grid(row=10, column=1)
        ttk.Label(self.controls_frame, text="EL Position / Slave Rate:").grid(row=10, column=0)

        self.send_az_button = ttk.Button(self.controls_frame, text="Send AZ Position/Rate",
                                         command=self.send_az_pos_slave_rate)
        self.send_az_button.grid(row=9, column=2)

        self.send_el_button = ttk.Button(self.controls_frame, text="Send EL Position/Rate",
                                         command=self.send_el_pos_slave_rate)
        self.send_el_button.grid(row=10, column=2)

        # Add AZ/EL rate sliders
        self.create_rate_sliders()

        # Add CW/CCW and UP/DOWN buttons
        self.create_position_buttons()

        # Amplitude, Period, Crossing Inputs
        labels = ["AZ Amplitude (°)", "EL Amplitude (°)", "AZ Period (s)", "EL Period (s)",
                  "AZ Crossing Point (°)", "EL Crossing Point (°)"]
        defaults = [30.0, 30.0, 10.0, 10.0, 90.0, 90.0]
        self.entries = []
        for i, (label, default) in enumerate(zip(labels, defaults), start=22):  # Start after sliders
            ttk.Label(self.controls_frame, text=label).grid(row=i, column=0)
            entry = ttk.Entry(self.controls_frame, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1)
            self.entries.append(entry)

        self.start_stop_button = ttk.Button(self.controls_frame, text="Start Sinusoidal Motion",
                                            command=self.toggle_sinusoidal_motion)
        self.start_stop_button.grid(row=28, column=0, columnspan=2)  # Moved down

        # Create graph canvases
        self.create_graphs()

        self.update_connection_settings()

    def create_graphs(self):
        # Frame for graphs
        self.graphs_frame = ttk.LabelFrame(self.root, text="Position Graphs")
        self.graphs_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure grid for 2x1 layout
        self.graphs_frame.columnconfigure(0, weight=1)
        self.graphs_frame.columnconfigure(1, weight=1)
        self.graphs_frame.rowconfigure(0, weight=1)

        # 1. Position Canvas (Commanded vs Actual)
        self.position_frame = ttk.LabelFrame(self.graphs_frame, text="AZ/EL Position - Commanded vs Actual")
        self.position_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.position_canvas = tk.Canvas(self.position_frame, bg="white", width=400, height=300)
        self.position_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Legend for position graph
        legend_frame = ttk.Frame(self.position_frame)
        legend_frame.pack(side=tk.TOP, fill=tk.X)

        # AZ Legend
        az_commanded_color = "blue"
        az_actual_color = "cyan"
        ttk.Label(legend_frame, text="AZ Commanded:", font=('Helvetica', 8)).pack(side=tk.LEFT, padx=2)
        canvas_az_cmd = tk.Canvas(legend_frame, width=20, height=10, bg=az_commanded_color)
        canvas_az_cmd.pack(side=tk.LEFT, padx=2)

        ttk.Label(legend_frame, text="AZ Actual:", font=('Helvetica', 8)).pack(side=tk.LEFT, padx=2)
        canvas_az_act = tk.Canvas(legend_frame, width=20, height=10, bg=az_actual_color)
        canvas_az_act.pack(side=tk.LEFT, padx=2)

        # EL Legend
        el_commanded_color = "red"
        el_actual_color = "orange"
        ttk.Label(legend_frame, text="EL Commanded:", font=('Helvetica', 8)).pack(side=tk.LEFT, padx=2)
        canvas_el_cmd = tk.Canvas(legend_frame, width=20, height=10, bg=el_commanded_color)
        canvas_el_cmd.pack(side=tk.LEFT, padx=2)

        ttk.Label(legend_frame, text="EL Actual:", font=('Helvetica', 8)).pack(side=tk.LEFT, padx=2)
        canvas_el_act = tk.Canvas(legend_frame, width=20, height=10, bg=el_actual_color)
        canvas_el_act.pack(side=tk.LEFT, padx=2)

        # 2. Error Canvas
        self.error_frame = ttk.LabelFrame(self.graphs_frame, text="AZ/EL Position Error")
        self.error_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.error_canvas = tk.Canvas(self.error_frame, bg="white", width=400, height=300)
        self.error_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Legend for error graph
        error_legend_frame = ttk.Frame(self.error_frame)
        error_legend_frame.pack(side=tk.TOP, fill=tk.X)

        # AZ Error Legend
        az_error_color = "purple"
        ttk.Label(error_legend_frame, text="AZ Error:", font=('Helvetica', 8)).pack(side=tk.LEFT, padx=2)
        canvas_az_err = tk.Canvas(error_legend_frame, width=20, height=10, bg=az_error_color)
        canvas_az_err.pack(side=tk.LEFT, padx=2)

        # EL Error Legend
        el_error_color = "green"
        ttk.Label(error_legend_frame, text="EL Error:", font=('Helvetica', 8)).pack(side=tk.LEFT, padx=2)
        canvas_el_err = tk.Canvas(error_legend_frame, width=20, height=10, bg=el_error_color)
        canvas_el_err.pack(side=tk.LEFT, padx=2)

        # Store color settings for graphs
        self.graph_colors = {
            "az_commanded": az_commanded_color,
            "az_actual": az_actual_color,
            "el_commanded": el_commanded_color,
            "el_actual": el_actual_color,
            "az_error": az_error_color,
            "el_error": el_error_color
        }

        # Start graph update
        self.update_graphs()

    def update_graphs(self):
        """Update both graph canvases"""
        if self.polling:  # Only update graphs when connected
            self.draw_position_graph()
            self.draw_error_graph()

        # Schedule next update (every 200ms)
        self.root.after(200, self.update_graphs)

    def draw_position_graph(self):
        """Draw the commanded vs actual position graph"""
        canvas = self.position_canvas
        canvas.delete("all")  # Clear canvas

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 50 or height < 50:  # Skip if canvas is too small
            return

        # Draw axes
        padding = 30  # Space for labels
        canvas.create_line(padding, height - padding, width - padding, height - padding, width=2)  # X-axis
        canvas.create_line(padding, padding, padding, height - padding, width=2)  # Y-axis

        # X-axis label (Time in seconds)
        canvas.create_text(width // 2, height - 5, text="Time (s)")

        # Y-axis label (Degrees)
        canvas.create_text(10, height // 2, text="Position (°)", angle=90)

        # Calculate scale
        if len(self.timestamps) < 2:
            return

        time_range = max(10, self.timestamps[-1] - self.timestamps[0])  # At least 10 seconds

        # Find min/max position values
        all_positions = []
        for pos in (self.az_commanded, self.az_actual, self.el_commanded, self.el_actual):
            if pos:
                all_positions.extend(pos)

        y_min = min(all_positions) if all_positions else -10
        y_max = max(all_positions) if all_positions else 10

        # Ensure some margin
        margin = max(5, (y_max - y_min) * 0.1)
        y_min -= margin
        y_max += margin

        # Ensure there's always some range even if values are constant
        if abs(y_max - y_min) < 1:
            y_min -= 5
            y_max += 5

        # Draw time axis ticks and labels
        t_start = self.timestamps[0]
        for t in range(0, int(time_range) + 1, max(1, int(time_range // 10))):
            x_pos = padding + (t / time_range) * (width - 2 * padding)
            canvas.create_line(x_pos, height - padding, x_pos, height - padding + 5)
            canvas.create_text(x_pos, height - padding + 15, text=str(t))

        # Draw position axis ticks and labels
        y_range = y_max - y_min
        for y in range(int(y_min), int(y_max) + 1, max(1, int(y_range // 10))):
            y_pos = height - padding - ((y - y_min) / y_range) * (height - 2 * padding)
            canvas.create_line(padding - 5, y_pos, padding, y_pos)
            canvas.create_text(padding - 15, y_pos, text=str(y))

        # Function to convert data point to canvas coordinates
        def to_canvas_coords(t, y):
            x = padding + ((t - t_start) / time_range) * (width - 2 * padding)
            y = height - padding - ((y - y_min) / y_range) * (height - 2 * padding)
            return x, y

        # Draw AZ commanded line
        if len(self.az_commanded) > 1:
            points = []
            for i, val in enumerate(self.az_commanded):
                if i < len(self.timestamps):
                    points.extend(to_canvas_coords(self.timestamps[i], val))
            canvas.create_line(points, fill=self.graph_colors["az_commanded"], width=2)

        # Draw AZ actual line
        if len(self.az_actual) > 1:
            points = []
            for i, val in enumerate(self.az_actual):
                if i < len(self.timestamps):
                    points.extend(to_canvas_coords(self.timestamps[i], val))
            canvas.create_line(points, fill=self.graph_colors["az_actual"], width=2)

        # Draw EL commanded line
        if len(self.el_commanded) > 1:
            points = []
            for i, val in enumerate(self.el_commanded):
                if i < len(self.timestamps):
                    points.extend(to_canvas_coords(self.timestamps[i], val))
            canvas.create_line(points, fill=self.graph_colors["el_commanded"], width=2)

        # Draw EL actual line
        if len(self.el_actual) > 1:
            points = []
            for i, val in enumerate(self.el_actual):
                if i < len(self.timestamps):
                    points.extend(to_canvas_coords(self.timestamps[i], val))
            canvas.create_line(points, fill=self.graph_colors["el_actual"], width=2)

    def draw_error_graph(self):
        """Draw the position error graph"""
        canvas = self.error_canvas
        canvas.delete("all")  # Clear canvas

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 50 or height < 50:  # Skip if canvas is too small
            return

        # Draw axes
        padding = 30  # Space for labels
        canvas.create_line(padding, height - padding, width - padding, height - padding, width=2)  # X-axis
        canvas.create_line(padding, height // 2, width - padding, height // 2, width=1, dash=(4, 2))  # Zero line
        canvas.create_line(padding, padding, padding, height - padding, width=2)  # Y-axis

        # X-axis label (Time in seconds)
        canvas.create_text(width // 2, height - 5, text="Time (s)")

        # Y-axis label (Degrees)
        canvas.create_text(10, height // 2, text="Error (°)", angle=90)

        # Calculate scale
        if len(self.timestamps) < 2:
            return

        time_range = max(10, self.timestamps[-1] - self.timestamps[0])  # At least 10 seconds

        # Find min/max error values
        all_errors = []
        for err in (self.az_error, self.el_error):
            if err:
                all_errors.extend(err)

        if not all_errors:
            y_min, y_max = -5, 5
        else:
            y_min = min(all_errors)
            y_max = max(all_errors)

        # Ensure some margin and symmetry around zero
        margin = max(1, max(abs(y_min), abs(y_max)) * 0.2)
        abs_max = max(abs(y_min), abs(y_max)) + margin
        y_min = -abs_max
        y_max = abs_max

        # Draw time axis ticks and labels
        t_start = self.timestamps[0]
        for t in range(0, int(time_range) + 1, max(1, int(time_range // 10))):
            x_pos = padding + (t / time_range) * (width - 2 * padding)
            canvas.create_line(x_pos, height - padding, x_pos, height - padding + 5)
            canvas.create_text(x_pos, height - padding + 15, text=str(t))

        # Draw error axis ticks and labels
        y_range = y_max - y_min
        for y in range(int(y_min), int(y_max) + 1, max(1, int(y_range // 10))):
            y_pos = height / 2 - ((y - 0) / (y_max)) * (height / 2 - padding)
            canvas.create_line(padding - 5, y_pos, padding, y_pos)
            canvas.create_text(padding - 15, y_pos, text=str(y))

        # Function to convert data point to canvas coordinates
        def to_canvas_coords(t, y):
            x = padding + ((t - t_start) / time_range) * (width - 2 * padding)
            y = height / 2 - ((y - 0) / (y_max)) * (height / 2 - padding)
            return x, y

        # Draw AZ error line
        if len(self.az_error) > 1:
            points = []
            for i, val in enumerate(self.az_error):
                if i < len(self.timestamps):
                    points.extend(to_canvas_coords(self.timestamps[i], val))
            canvas.create_line(points, fill=self.graph_colors["az_error"], width=2)

        # Draw EL error line
        if len(self.el_error) > 1:
            points = []
            for i, val in enumerate(self.el_error):
                if i < len(self.timestamps):
                    points.extend(to_canvas_coords(self.timestamps[i], val))
            canvas.create_line(points, fill=self.graph_colors["el_error"], width=2)

    def create_position_buttons(self):
        # Create a frame for position control buttons
        self.position_buttons_frame = ttk.LabelFrame(self.controls_frame, text="Position Control")
        self.position_buttons_frame.grid(row=19, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

        # AZ Control Buttons
        ttk.Label(self.position_buttons_frame, text="AZ Control:").grid(row=0, column=0, padx=5, pady=5)

        # CW Button (Right)
        self.cw_button = ttk.Button(self.position_buttons_frame, text="CW →")
        self.cw_button.grid(row=0, column=2, padx=5, pady=5)
        self.cw_button.bind("<ButtonPress-1>", lambda event: self.start_position_command("CW"))
        self.cw_button.bind("<ButtonRelease-1>", self.stop_position_command)

        # CCW Button (Left)
        self.ccw_button = ttk.Button(self.position_buttons_frame, text="← CCW")
        self.ccw_button.grid(row=0, column=1, padx=5, pady=5)
        self.ccw_button.bind("<ButtonPress-1>", lambda event: self.start_position_command("CCW"))
        self.ccw_button.bind("<ButtonRelease-1>", self.stop_position_command)

        # EL Control Buttons
        ttk.Label(self.position_buttons_frame, text="EL Control:").grid(row=1, column=0, padx=5, pady=5)

        # UP Button
        self.up_button = ttk.Button(self.position_buttons_frame, text="UP ↑")
        self.up_button.grid(row=1, column=1, padx=5, pady=5)
        self.up_button.bind("<ButtonPress-1>", lambda event: self.start_position_command("UP"))
        self.up_button.bind("<ButtonRelease-1>", self.stop_position_command)

        # DOWN Button
        self.down_button = ttk.Button(self.position_buttons_frame, text="↓ DOWN")
        self.down_button.grid(row=1, column=2, padx=5, pady=5)
        self.down_button.bind("<ButtonPress-1>", lambda event: self.start_position_command("DOWN"))
        self.down_button.bind("<ButtonRelease-1>", self.stop_position_command)

        # Instructions label
        ttk.Label(self.position_buttons_frame,
                  text="Click: 0.3° increment  |  Hold: 1.0° continuous increments",
                  font=('Helvetica', 9, 'italic')).grid(row=2, column=0, columnspan=3, padx=5, pady=2)

    def create_rate_sliders(self):
        # Create a frame for sliders
        self.sliders_frame = ttk.LabelFrame(self.controls_frame, text="Rate Control Sliders (Auto-Return)")
        self.sliders_frame.grid(row=20, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

        # AZ Slider
        ttk.Label(self.sliders_frame, text="AZ Rate (±30°):").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.az_slider = ttk.Scale(self.sliders_frame, from_=-30, to=30, orient=tk.HORIZONTAL, length=300,
                                   value=0, command=self.on_az_slider_change)
        self.az_slider.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.az_slider_value = ttk.Label(self.sliders_frame, text="0.0°")
        self.az_slider_value = ttk.Label(self.sliders_frame, text="0.0°")
        self.az_slider_value.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # EL Slider
        ttk.Label(self.sliders_frame, text="EL Rate (±30°):").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.el_slider = ttk.Scale(self.sliders_frame, from_=-30, to=30, orient=tk.HORIZONTAL, length=300,
                                   value=0, command=self.on_el_slider_change)
        self.el_slider.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.el_slider_value = ttk.Label(self.sliders_frame, text="0.0°")
        self.el_slider_value.grid(row=1, column=2, padx=5, pady=2, sticky="w")

        # Instructions label
        ttk.Label(self.sliders_frame, text="Hold to adjust rate - Release to return to zero",
                  font=('Helvetica', 9, 'italic')).grid(row=2, column=1, padx=5, pady=2)

        # Attach mouse events to sliders
        self.az_slider.bind("<ButtonPress-1>", self.on_az_slider_press)
        self.az_slider.bind("<ButtonRelease-1>", self.on_az_slider_release)
        self.el_slider.bind("<ButtonPress-1>", self.on_el_slider_press)
        self.el_slider.bind("<ButtonRelease-1>", self.on_el_slider_release)

        # Disable sliders initially (until slave rate mode is activated)
        self.az_slider.state(['disabled'])
        self.el_slider.state(['disabled'])

    def on_az_slider_press(self, event):
        self.az_slider_pressed = True

    def on_az_slider_release(self, event):
        self.az_slider_pressed = False
        # Return to zero and send zero rate command
        self.az_slider.set(0)
        self.on_az_slider_change(0)

    def on_el_slider_press(self, event):
        self.el_slider_pressed = True

    def on_el_slider_release(self, event):
        self.el_slider_pressed = False
        # Return to zero and send zero rate command
        self.el_slider.set(0)
        self.on_el_slider_change(0)

    def on_az_slider_change(self, value):
        value = float(value)
        self.az_slider_value.config(text=f"{value:.1f}°")

        # Only send the command if in slave rate mode
        if self.is_slave_rate_mode and self.polling:
            self.send_and_log(f"P290W{value:+09.3f}")

    def on_el_slider_change(self, value):
        value = float(value)
        self.el_slider_value.config(text=f"{value:.1f}°")

        # Only send the command if in slave rate mode
        if self.is_slave_rate_mode and self.polling:
            self.send_and_log(f"P291W{value:+09.3f}")

    def start_position_command(self, command_type):
        if not self.polling:
            return  # Don't do anything if not connected

        self.current_button = command_type
        self.button_press_active = True

        # First click: Single 0.3° increment
        self.send_position_increment(command_type, 0.3)

        # Start timer for continuous sending after 300ms hold
        self.root.after(300, self.check_continuous_sending)

    def check_continuous_sending(self):
        if self.button_press_active:
            self.continuous_sending = True
            # Start continuous sending thread
            threading.Thread(target=self.send_continuous_commands, daemon=True).start()

    def send_continuous_commands(self):
        while self.continuous_sending and self.button_press_active:
            self.send_position_increment(self.current_button, 1.0)
            time.sleep(0.2)  # Send about 5 commands per second

    def stop_position_command(self, event):
        self.button_press_active = False
        self.continuous_sending = False

    def send_position_increment(self, command_type, increment):
        try:
            # Get current positions
            current_az = float(self.az_entry.get()) if self.az_entry.get() else 0.0
            current_el = float(self.el_entry.get()) if self.el_entry.get() else 0.0

            # Calculate new position based on command type
            if command_type == "CW":
                new_az = current_az + increment
                self.send_and_log(f"P0W{new_az:+09.3f}")
                # Store commanded position for graph
                self.last_commanded_az = new_az
            elif command_type == "CCW":
                new_az = current_az - increment
                self.send_and_log(f"P0W{new_az:+09.3f}")
                # Store commanded position for graph
                self.last_commanded_az = new_az
            elif command_type == "UP":
                new_el = current_el + increment
                self.send_and_log(f"P1W{new_el:+09.3f}")
                # Store commanded position for graph
                self.last_commanded_el = new_el
            elif command_type == "DOWN":
                new_el = current_el - increment
                self.send_and_log(f"P1W{new_el:+09.3f}")
                # Store commanded position for graph
                self.last_commanded_el = new_el

        except ValueError:
            # If current position can't be parsed, don't do anything
            pass

    def reset_button_colors(self):
        """Reset all mode buttons to their default appearance"""
        for button_label in self.command_buttons:
            button = self.command_buttons[button_label]
            button.configure(style="TButton")  # Reset to default style

    def highlight_active_button(self, label):
        """Highlight the active mode button with its designated color"""
        if label in self.command_buttons:
            # Set active mode label
            self.active_mode = label
            self.mode_indicator.configure(text=label, foreground=self.mode_colors[label])

            # Use a colored frame behind the button to highlight it
            button = self.command_buttons[label]
            # Apply the specific style for this button
            button.configure(style=f"{label}.TButton")

    def send_command_and_update(self, cmd, label):
        # Send the command
        self.send_and_log(cmd)

        # Reset all button colors first
        self.reset_button_colors()

        # Highlight the active button
        self.highlight_active_button(label)

        # Update slider states based on command
        if label == "Slave Rate":
            self.is_slave_rate_mode = True
            self.az_slider.state(['!disabled'])
            self.el_slider.state(['!disabled'])
        else:
            self.is_slave_rate_mode = False
            self.az_slider.state(['disabled'])
            self.el_slider.state(['disabled'])
            # Reset sliders when exiting slave rate mode
            self.az_slider.set(0)
            self.el_slider.set(0)
            self.az_slider_value.config(text="0.0°")
            self.el_slider_value.config(text="0.0°")

    def update_connection_settings(self):
        comm_type = self.comm_type.get()
        if comm_type == "Serial":
            self.serial_settings_frame.grid()
            self.socket_settings_frame.grid_remove()
        else:
            self.serial_settings_frame.grid_remove()
            self.socket_settings_frame.grid()

    def get_serial_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def toggle_connection(self):
        if self.polling:
            self.stop_communication()
            self.connect_button.config(text="Connect")

            # Reset mode indicator when disconnecting
            self.active_mode = None
            self.mode_indicator.configure(text="None", foreground="black")
            self.reset_button_colors()
            return

        if self.comm_type.get() == "Serial":
            self.start_serial()
        elif self.comm_type.get() == "Socket":
            self.start_socket()
        else:
            messagebox.showerror("Error", "Invalid communication type selected.")
            return

        if self.polling:
            self.connect_button.config(text="Disconnect")

            # Reset graph data when starting a new connection
            self.az_commanded.clear()
            self.az_actual.clear()
            self.el_commanded.clear()
            self.el_actual.clear()
            self.az_error.clear()
            self.el_error.clear()
            self.timestamps.clear()
            self.start_time = time.time()

    def start_serial(self):
        try:
            self.serial_port.port = self.port_combo.get()
            self.serial_port.baudrate = int(self.baud_combo.get())
            parity_str = self.parity_combo.get()
            if parity_str == 'Even':
                self.serial_port.parity = serial.PARITY_EVEN
            elif parity_str == 'Odd':
                self.serial_port.parity = serial.PARITY_ODD
            elif parity_str == 'Mark':
                self.serial_port.parity = serial.PARITY_MARK
            elif parity_str == 'Space':
                self.serial_port.parity = serial.PARITY_SPACE
            else:
                self.serial_port.parity = serial.PARITY_NONE
            self.serial_port.timeout = 0.01
            self.serial_port.open()
            self.start_polling(0.01)
        except Exception as e:
            messagebox.showerror("Serial Error", f"Could not open port: {e}")

    def start_socket(self):
        try:
            ip = self.socket_ip_entry.get()
            port = int(self.socket_port_entry.get())
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.connect((ip, port))
            self.start_polling()
        except Exception as e:
            messagebox.showerror("Socket Error", f"Could not connect: {e}")

    def stop_communication(self):
        self.polling = False
        if hasattr(self, 'serial_port') and self.serial_port.is_open:
            self.serial_port.close()
        if self.socket_client:
            self.socket_client.close()
            self.socket_client = None

    def start_polling(self):
        if not self.polling:
            self.polling = True
            threading.Thread(target=self.poll_loop, daemon=True).start()

    def poll_loop(self):
        retry_count = 0
        max_retries = 3
        while self.polling:
            try:
                # Send commands with pause between them
                az = self.send_and_receive("P7R1")
                time.sleep(0.1)  # Brief pause between commands
                el = self.send_and_receive("P8R1")

                # Validate responses before updating
                if self.is_valid_position(az) and self.is_valid_position(el):
                    self.root.after(0, self.update_positions, az, el)
                    retry_count = 0  # Reset retry counter on success
                else:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"Warning: Multiple failed position readings")
                        retry_count = 0  # Reset and continue

                time.sleep(0.01)
            except Exception as e:
                print(f"Poll loop error: {e}")
                time.sleep(0.01)  # Brief pause on error

    def is_valid_position(self, value):
        """Check if response contains a valid position value"""
        try:
            # Check if string can be converted to float and is reasonable
            if value and value.strip():
                float_val = float(value)
                # Add range check if appropriate (e.g., -180 to +180 for AZ)
                return True
            return False
        except (ValueError, TypeError):
            return False

    def send_and_receive(self, cmd):
        try:
            full_cmd = cmd + '\r\n'
            # Log TX command
            self.tx_log.insert(tk.END, full_cmd)
            self.tx_log.see(tk.END)

            if self.comm_type.get() == "Socket" and self.socket_client:
                self.socket_client.sendall(full_cmd.encode())
                data = self.socket_client.recv(64).decode(errors='ignore').strip()
            elif self.comm_type.get() == "Serial" and self.serial_port.is_open:
                self.serial_port.write(full_cmd.encode())
                data = self.serial_port.readline().decode(errors='ignore').strip()
            else:
                return ""

            # Remove non-printable characters
            data = ''.join(filter(lambda x: x.isprintable(), data))

            # Log RX data
            if data:
                self.rx_log.insert(tk.END, data + '\n')
                self.rx_log.see(tk.END)

            return data
        except Exception:
            return ""

    def update_positions(self, az, el):
        try:
            # Update current positions display
            if az != self.last_az:
                self.az_entry.delete(0, tk.END)
                self.az_entry.insert(0, az)
                self.last_az = az
            if el != self.last_el:
                self.el_entry.delete(0, tk.END)
                self.el_entry.insert(0, el)
                self.last_el = el

            # Record data for graphs
            current_time = time.time() - self.start_time

            # Convert string values to float for graphing
            try:
                az_float = float(az) if az else 0.0
                el_float = float(el) if el else 0.0

                # Add data points
                self.timestamps.append(current_time)
                self.az_commanded.append(self.last_commanded_az)
                self.az_actual.append(az_float)
                self.el_commanded.append(self.last_commanded_el)
                self.el_actual.append(el_float)

                # Calculate error
                az_error = self.last_commanded_az - az_float
                el_error = self.last_commanded_el - el_float
                self.az_error.append(az_error)
                self.el_error.append(el_error)
            except ValueError:
                pass  # Ignore if conversion fails

        except Exception as e:
            print(f"Error updating positions: {e}")

    def send_and_log(self, cmd):
        response = self.send_and_receive(cmd)
        # response already logged in send_and_receive

        # Update commanded positions for graphs when sending a position command
        if cmd.startswith("P0W"):  # AZ position command
            try:
                self.last_commanded_az = float(cmd[3:])
            except ValueError:
                pass
        elif cmd.startswith("P1W"):  # EL position command
            try:
                self.last_commanded_el = float(cmd[3:])
            except ValueError:
                pass

    def send_az_pos_slave_rate(self):
        try:
            val = float(self.az_pos_slave_rate.get())
            self.send_and_log(f"P0W{val:+09.3f}")
            self.send_and_log(f"P290W{val:+09.3f}")
            # Update commanded position for graph
            self.last_commanded_az = val
        except ValueError:
            messagebox.showerror("Input Error", "Invalid AZ value")

    def send_el_pos_slave_rate(self):
        try:
            val = float(self.el_pos_slave_rate.get())
            self.send_and_log(f"P1W{val:+09.3f}")
            self.send_and_log(f"P291W{val:+09.3f}")
            # Update commanded position for graph
            self.last_commanded_el = val
        except ValueError:
            messagebox.showerror("Input Error", "Invalid EL value")

    def toggle_sinusoidal_motion(self):
        if self.sinusoidal_running:
            # Stop sinusoidal motion and send standby command
            self.sinusoidal_running = False
            self.start_stop_button.config(text="Start Sinusoidal Motion")

            # Send standby command (same as clicking the Standby button)
            self.send_command_and_update("P2W0", "Standby")
        else:
            self.sinusoidal_running = True
            self.start_stop_button.config(text="Stop Sinusoidal Motion")
            self.start_sinusoidal_motion()

    def start_sinusoidal_motion(self):
        try:
            az_crossing = float(self.entries[4].get())
            el_crossing = float(self.entries[5].get())
            az_amp = float(self.entries[0].get())
            el_amp = float(self.entries[1].get())
            az_period = float(self.entries[2].get())
            el_period = float(self.entries[3].get())

            threading.Thread(target=self.sinusoidal_motion,
                             args=(az_crossing, el_crossing, az_amp, el_amp, az_period, el_period),
                             daemon=True).start()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid parameters")

    def sinusoidal_motion(self, az_crossing, el_crossing, az_amp, el_amp, az_period, el_period):
        start_time = time.time()
        while self.sinusoidal_running:
            t = time.time() - start_time
            az_angle = az_crossing + az_amp * math.sin(2 * math.pi * t / az_period)
            el_angle = el_crossing + el_amp * math.sin(2 * math.pi * t / el_period)

            # Update commanded positions for graphs
            self.last_commanded_az = az_angle
            self.last_commanded_el = el_angle

            # Send commands
            self.send_and_log(f"P0W{az_angle:+09.3f}")
            self.send_and_log(f"P1W{el_angle:+09.3f}")
            time.sleep(0.03)


if __name__ == "__main__":
    root = tk.Tk()
    app = PositionReaderApp(root)
    root.mainloop()