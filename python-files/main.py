#!/usr/bin/env python3
"""
Enhanced Transformer Fault Detection System
Fixed version with proper Python syntax and error handling
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import csv
import json
import os
import random
import threading
import time

# === Configuration ===
DEFAULT_CONFIG = {
    "cooling_limits": {
        'ONAN': {'oil_temp': 90, 'winding_temp': 105},
        'ONAF': {'oil_temp': 95, 'winding_temp': 115},
        'OFAF': {'oil_temp': 100, 'winding_temp': 120},
        'ODAF': {'oil_temp': 105, 'winding_temp': 125},
    },
    "fault_thresholds": {
        "critical": 70,
        "warning": 30
    },
    "aging_factor": 0.4,
    "load_rating": 1000
}

class FaultDiagnostics:
    def __init__(self, config):
        self.config = config
        self.fault_history = []

    def calculate_fault_score(self, inputs):
        """Calculate comprehensive fault score"""
        cooling_type = inputs['cooling_type']
        age = inputs['age']
        limits = self.config['cooling_limits'].get(cooling_type, 
                                                  self.config['cooling_limits']['ONAN'])

        # Age-adjusted limits
        oil_limit = limits['oil_temp'] - (self.config['aging_factor'] * age)
        winding_limit = limits['winding_temp'] - (self.config['aging_factor'] * age)

        score = 0
        faults = []

        # Temperature faults
        if inputs['oil_temp'] > oil_limit:
            excess = inputs['oil_temp'] - oil_limit
            fault_score = min(30, excess * 2)
            score += fault_score
            faults.append(f"🌡️ Oil overheating: {inputs['oil_temp']:.1f}°C (limit: {oil_limit:.1f}°C)")

        if inputs['winding_temp'] > winding_limit:
            excess = inputs['winding_temp'] - winding_limit
            fault_score = min(35, excess * 2.5)
            score += fault_score
            faults.append(f"🌡️ Winding overheating: {inputs['winding_temp']:.1f}°C (limit: {winding_limit:.1f}°C)")

        # Load faults
        load_pct = (inputs['load_current'] / self.config['load_rating']) * 100
        if load_pct > 120:
            score += 25
            faults.append(f"⚡ Severe overload: {load_pct:.1f}% (>120%)")
        elif load_pct > 100:
            score += 15
            faults.append(f"⚠️ Overload: {load_pct:.1f}% (>100%)")

        # Thermal gradient
        gradient = inputs['winding_temp'] - inputs['oil_temp']
        if gradient < 5:
            score += 20
            faults.append(f"❄️ Poor heat transfer: gradient {gradient:.1f}°C (too low)")
        elif gradient > 40:
            score += 15
            faults.append(f"🔥 Excessive thermal gradient: {gradient:.1f}°C")

        # Environmental
        if inputs['ambient_temp'] > 40:
            score += 10
            faults.append(f"🌡️ High ambient temperature: {inputs['ambient_temp']:.1f}°C")

        # Age factors
        if age > 30:
            score += 15
            faults.append(f"🧓 Very old equipment: {age} years")
        elif age > 25:
            score += 8
            faults.append(f"📅 Aging equipment: {age} years")

        # Determine severity
        health_score = max(0, 100 - score)
        if score >= self.config['fault_thresholds']['critical']:
            severity = "critical"
            color = "#FF6B6B"
        elif score >= self.config['fault_thresholds']['warning']:
            severity = "warning"
            color = "#FFD700"
        else:
            severity = "normal"
            color = "#90EE90"

        # Generate recommendations
        recommendations = self._get_recommendations(severity, faults)

        result = {
            'health_score': health_score,
            'raw_score': score,
            'severity': severity,
            'color': color,
            'faults': faults,
            'recommendations': recommendations,
            'timestamp': datetime.now()
        }

        self.fault_history.append(result)
        return result

    def _get_recommendations(self, severity, faults):
        """Generate recommendations based on faults"""
        recommendations = []

        if severity == "critical":
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED")
            recommendations.append("• Consider taking transformer offline")
            recommendations.append("• Contact maintenance team immediately")

        if any("overheating" in fault for fault in faults):
            recommendations.append("🌡️ Check cooling system operation")
            recommendations.append("• Verify fan/pump functionality")

        if any("overload" in fault for fault in faults):
            recommendations.append("⚡ Reduce electrical load if possible")
            recommendations.append("• Check load distribution")

        if any("gradient" in fault for fault in faults):
            recommendations.append("❄️ Inspect oil circulation system")
            recommendations.append("• Check oil level and quality")

        if any("age" in fault or "old" in fault for fault in faults):
            recommendations.append("📅 Schedule comprehensive inspection")
            recommendations.append("• Consider insulation testing")

        if not recommendations:
            recommendations.append("✅ System operating normally")
            recommendations.append("• Continue routine monitoring")

        return recommendations

class DataLogger:
    def __init__(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transformer_log_{timestamp}.csv"

        self.filename = filename
        self._initialize_file()

    def _initialize_file(self):
        """Initialize CSV file with headers"""
        try:
            with open(self.filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'oil_temp', 'winding_temp', 'ambient_temp',
                    'load_current', 'age', 'cooling_type', 'health_score',
                    'severity', 'fault_count'
                ])
        except Exception as e:
            print(f"Error initializing log file: {e}")

    def log_data(self, inputs, diagnosis):
        """Log data to CSV file"""
        try:
            with open(self.filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    diagnosis['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                    inputs['oil_temp'],
                    inputs['winding_temp'],
                    inputs['ambient_temp'],
                    inputs['load_current'],
                    inputs['age'],
                    inputs['cooling_type'],
                    diagnosis['health_score'],
                    diagnosis['severity'],
                    len(diagnosis['faults'])
                ])
        except Exception as e:
            print(f"Error logging data: {e}")

class LivePlotter:
    def __init__(self, parent):
        self.fig = Figure(figsize=(12, 6))
        self.fig.suptitle("Real-time Transformer Monitoring")

        # Create subplots
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)

        self.fig.tight_layout(pad=3.0)

        # Data storage
        self.max_points = 50
        self.times = []
        self.oil_temps = []
        self.winding_temps = []
        self.loads = []
        self.health_scores = []

        self._setup_plots()

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.start_time = datetime.now()

    def _setup_plots(self):
        """Setup plot configurations"""
        # Temperature plot
        self.ax1.set_title("Temperature")
        self.ax1.set_ylabel("°C")
        self.ax1.grid(True, alpha=0.3)

        # Load plot
        self.ax2.set_title("Load Current")
        self.ax2.set_ylabel("Amperes")
        self.ax2.grid(True, alpha=0.3)

        # Health score plot
        self.ax3.set_title("Health Score")
        self.ax3.set_ylabel("Score (0-100)")
        self.ax3.set_ylim(0, 100)
        self.ax3.grid(True, alpha=0.3)

        # Gradient plot
        self.ax4.set_title("Thermal Gradient")
        self.ax4.set_ylabel("°C")
        self.ax4.grid(True, alpha=0.3)

    def update(self, inputs, diagnosis):
        """Update plots with new data"""
        current_time = (datetime.now() - self.start_time).total_seconds() / 60

        # Add new data
        self.times.append(current_time)
        self.oil_temps.append(inputs['oil_temp'])
        self.winding_temps.append(inputs['winding_temp'])
        self.loads.append(inputs['load_current'])
        self.health_scores.append(diagnosis['health_score'])

        # Keep only recent data
        if len(self.times) > self.max_points:
            self.times = self.times[-self.max_points:]
            self.oil_temps = self.oil_temps[-self.max_points:]
            self.winding_temps = self.winding_temps[-self.max_points:]
            self.loads = self.loads[-self.max_points:]
            self.health_scores = self.health_scores[-self.max_points:]

        # Clear and redraw plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        # Temperature plot
        self.ax1.plot(self.times, self.oil_temps, 'r-', label='Oil', linewidth=2)
        self.ax1.plot(self.times, self.winding_temps, 'b-', label='Winding', linewidth=2)
        self.ax1.set_title("Temperature")
        self.ax1.set_ylabel("°C")
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)

        # Load plot
        self.ax2.plot(self.times, self.loads, 'm-', linewidth=2)
        self.ax2.set_title("Load Current")
        self.ax2.set_ylabel("Amperes")
        self.ax2.grid(True, alpha=0.3)

        # Health score plot
        self.ax3.plot(self.times, self.health_scores, 'orange', linewidth=2)
        self.ax3.set_title("Health Score")
        self.ax3.set_ylabel("Score (0-100)")
        self.ax3.set_ylim(0, 100)
        self.ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7)
        self.ax3.axhline(y=30, color='yellow', linestyle='--', alpha=0.7)
        self.ax3.grid(True, alpha=0.3)

        # Gradient plot
        gradients = [w - o for w, o in zip(self.winding_temps, self.oil_temps)]
        self.ax4.plot(self.times, gradients, 'purple', linewidth=2)
        self.ax4.set_title("Thermal Gradient")
        self.ax4.set_ylabel("°C")
        self.ax4.grid(True, alpha=0.3)

        # Set x-axis labels
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_xlabel("Time (minutes)")

        self.canvas.draw()

class TransformerFaultDetectorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Transformer Fault Detection System by Alsiddig Ahmed")
        self.root.geometry("1400x900")

        # Initialize components
        self.config = DEFAULT_CONFIG.copy()
        self.diagnostics = FaultDiagnostics(self.config)
        self.logger = DataLogger()

        # Simulation control
        self.simulation_running = False

        self.setup_gui()

    def setup_gui(self):
        """Setup main GUI"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Main monitoring tab
        self.monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_frame, text="Monitoring")

        self.setup_monitoring_tab()

    def setup_monitoring_tab(self):
        """Setup monitoring interface"""
        # Left panel for controls
        control_frame = ttk.LabelFrame(self.monitoring_frame, text="Parameters", padding=10)
        control_frame.pack(side='left', fill='y', padx=5, pady=5)

        # Parameter controls
        self.sliders = {}
        self.values = {}

        self.add_parameter("Oil Temperature", 0, 150, "°C", 0, 75)
        self.add_parameter("Winding Temperature", 0, 180, "°C", 1, 85)
        self.add_parameter("Ambient Temperature", -10, 60, "°C", 2, 25)
        self.add_parameter("Load Current", 0, 1500, "A", 3, 800)
        self.add_parameter("Age", 0, 50, "years", 4, 15)

        # Cooling type
        ttk.Label(control_frame, text="Cooling Type:").grid(row=5, column=0, sticky="w", pady=5)
        self.cooling_var = tk.StringVar(value='ONAN')
        cooling_combo = ttk.Combobox(control_frame, textvariable=self.cooling_var,
                                   values=list(self.config['cooling_limits'].keys()),
                                   state='readonly', width=15)
        cooling_combo.grid(row=5, column=1, columnspan=2, sticky="ew", padx=5)

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10, sticky="ew")

        ttk.Button(button_frame, text="Run Diagnosis", 
                  command=self.run_diagnosis).pack(fill='x', pady=2)

        self.sim_button = ttk.Button(button_frame, text="Start Simulation", 
                                   command=self.toggle_simulation)
        self.sim_button.pack(fill='x', pady=2)

        ttk.Button(button_frame, text="Export Data", 
                  command=self.export_data).pack(fill='x', pady=2)

        ttk.Button(button_frame, text="Reset", 
                  command=self.reset_parameters).pack(fill='x', pady=2)

        # Right panel for results and plots
        right_panel = ttk.Frame(self.monitoring_frame)
        right_panel.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        # Results display
        results_frame = ttk.LabelFrame(right_panel, text="Diagnostic Results", padding=5)
        results_frame.pack(fill='x', pady=5)

        self.result_text = tk.Text(results_frame, height=12, width=70,
                                 font=("Consolas", 9), wrap=tk.WORD)
        result_scroll = ttk.Scrollbar(results_frame, orient="vertical", 
                                    command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scroll.set)

        self.result_text.pack(side='left', fill='both', expand=True)
        result_scroll.pack(side='right', fill='y')

        # Plots
        plot_frame = ttk.LabelFrame(right_panel, text="Live Charts", padding=5)
        plot_frame.pack(fill='both', expand=True, pady=5)

        self.live_plotter = LivePlotter(plot_frame)

    def add_parameter(self, label, min_val, max_val, unit, row, default):
        """Add parameter control"""
        ttk.Label(self.monitoring_frame.children['!labelframe'], 
                 text=f"{label}:").grid(row=row, column=0, sticky="w", pady=2)

        var = tk.DoubleVar(value=default)
        slider = ttk.Scale(self.monitoring_frame.children['!labelframe'], 
                          from_=min_val, to=max_val, orient="horizontal", 
                          variable=var, length=200)
        slider.grid(row=row, column=1, sticky="ew", padx=5)

        # Value display
        value_label = ttk.Label(self.monitoring_frame.children['!labelframe'], 
                               text=f"{default} {unit}")
        value_label.grid(row=row, column=2, sticky="w", padx=5)

        # Update display when slider moves
        def update_display(*args):
            value_label.config(text=f"{var.get():.1f} {unit}")

        var.trace('w', update_display)

        self.sliders[label] = slider
        self.values[label] = var

    def get_current_inputs(self):
        """Get current parameter values"""
        return {
            'oil_temp': self.values["Oil Temperature"].get(),
            'winding_temp': self.values["Winding Temperature"].get(),
            'ambient_temp': self.values["Ambient Temperature"].get(),
            'load_current': self.values["Load Current"].get(),
            'age': self.values["Age"].get(),
            'cooling_type': self.cooling_var.get()
        }

    def run_diagnosis(self):
        """Run diagnostic analysis"""
        try:
            inputs = self.get_current_inputs()
            diagnosis = self.diagnostics.calculate_fault_score(inputs)

            self.display_results(diagnosis)
            self.live_plotter.update(inputs, diagnosis)
            self.logger.log_data(inputs, diagnosis)

            # Show alerts for critical conditions
            if diagnosis['severity'] == 'critical':
                messagebox.showerror("Critical Alert", 
                                   "Transformer in critical condition!\nImmediate attention required.")
            elif diagnosis['severity'] == 'warning':
                messagebox.showwarning("Warning", 
                                     "Transformer showing warning signs.\nSchedule maintenance.")

        except Exception as e:
            messagebox.showerror("Error", f"Diagnosis failed: {str(e)}")

    def display_results(self, diagnosis):
        """Display diagnosis results"""
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(bg=diagnosis['color'])

        # Header
        status_text = f"TRANSFORMER STATUS: {diagnosis['severity'].upper()}\n"
        status_text += f"Health Score: {diagnosis['health_score']}/100\n"
        status_text += f"Time: {diagnosis['timestamp'].strftime('%H:%M:%S')}\n"
        status_text += "=" * 50 + "\n\n"

        self.result_text.insert(tk.END, status_text)

        # Faults
        if diagnosis['faults']:
            self.result_text.insert(tk.END, "DETECTED ISSUES:\n")
            for fault in diagnosis['faults']:
                self.result_text.insert(tk.END, f"• {fault}\n")
            self.result_text.insert(tk.END, "\n")
        else:
            self.result_text.insert(tk.END, "✅ NO ISSUES DETECTED\n\n")

        # Recommendations
        self.result_text.insert(tk.END, "RECOMMENDATIONS:\n")
        for rec in diagnosis['recommendations']:
            self.result_text.insert(tk.END, f"{rec}\n")

    def toggle_simulation(self):
        """Toggle simulation mode"""
        if not self.simulation_running:
            self.start_simulation()
        else:
            self.stop_simulation()

    def start_simulation(self):
        """Start simulation"""
        self.simulation_running = True
        self.sim_button.config(text="Stop Simulation")

        def simulate():
            while self.simulation_running:
                try:
                    # Generate random data
                    self.values["Oil Temperature"].set(random.uniform(70, 95))
                    self.values["Winding Temperature"].set(random.uniform(80, 110))
                    self.values["Ambient Temperature"].set(random.uniform(20, 35))
                    self.values["Load Current"].set(random.uniform(600, 1200))

                    self.run_diagnosis()
                    time.sleep(2)
                except:
                    break

        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()

    def stop_simulation(self):
        """Stop simulation"""
        self.simulation_running = False
        self.sim_button.config(text="Start Simulation")

    def reset_parameters(self):
        """Reset all parameters"""
        defaults = {
            "Oil Temperature": 75,
            "Winding Temperature": 85,
            "Ambient Temperature": 25,
            "Load Current": 800,
            "Age": 15
        }

        for param, value in defaults.items():
            self.values[param].set(value)

        self.cooling_var.set('ONAN')
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(bg='white')

    def export_data(self):
        """Export data to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Export Data"
            )

            if filename:
                import shutil
                shutil.copy2(self.logger.filename, filename)
                messagebox.showinfo("Success", f"Data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = TransformerFaultDetectorGUI()
    app.run()

if __name__ == "__main__":
    main()