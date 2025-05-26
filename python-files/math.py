import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class DiseaseSimulator:
    def __init__(self, disease_name, population, initial_infected, initial_recovered, beta, gamma):
        self.disease_name = disease_name
        self.N = population
        self.I0 = initial_infected
        self.R0 = initial_recovered
        self.S0 = population - initial_infected - initial_recovered
        self.beta = beta
        self.gamma = gamma

        if self.S0 < 0:
            raise ValueError("Initial susceptible population cannot be negative.")
        if self.beta < 0 or self.gamma < 0:
            raise ValueError("Beta and Gamma must be non-negative.")

    def simulate(self, days):
        t = np.arange(days + 1)
        S = np.zeros(days + 1)
        I = np.zeros(days + 1)
        R = np.zeros(days + 1)
        S[0], I[0], R[0] = self.S0, self.I0, self.R0

        for i in range(days):
            new_infected = (self.beta * S[i] * I[i]) / self.N
            new_recovered = self.gamma * I[i]
            S[i + 1] = S[i] - new_infected
            I[i + 1] = I[i] + new_infected - new_recovered
            R[i + 1] = R[i] + new_recovered

        return t, S, I, R

class DiseaseSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Disease Spread Simulator - Zambia")
        self.root.geometry("1000x700")

        self.disease_data = {
            "influenza": {"beta": 0.5, "gamma": 0.33},
            "measles": {"beta": 0.9, "gamma": 0.1},
            "ebola": {"beta": 0.2, "gamma": 0.05},
            "common cold": {"beta": 0.4, "gamma": 0.2},
            "cholera": {"beta": 0.3, "gamma": 0.15},
            "typhoid": {"beta": 0.25, "gamma": 0.1},
            "malaria": {"beta": 0.6, "gamma": 0.14},
            "custom": {"beta": 0.3, "gamma": 0.1}
        }

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Disease Spread Simulator", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Copyright
        copyright_label = ttk.Label(main_frame, text="© 2025 Siwale Wanjivwa", font=("Arial", 10, "italic"))
        copyright_label.grid(row=1, column=0, columnspan=2, sticky=tk.E, padx=10)

        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Simulation Parameters", padding="10")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Disease:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.disease_var = tk.StringVar(value="malaria")
        disease_combo = ttk.Combobox(input_frame, textvariable=self.disease_var, values=list(self.disease_data.keys()))
        disease_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        disease_combo.bind('<<ComboboxSelected>>', self.on_disease_change)

        ttk.Label(input_frame, text="Population:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.population_var = tk.StringVar(value="20723965")
        ttk.Entry(input_frame, textvariable=self.population_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0))

        ttk.Label(input_frame, text="Initial Infected:").grid(row=2, column=0, sticky=tk.W)
        self.infected_var = tk.StringVar(value="100")
        ttk.Entry(input_frame, textvariable=self.infected_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0))

        ttk.Label(input_frame, text="Initial Recovered:").grid(row=3, column=0, sticky=tk.W)
        self.recovered_var = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.recovered_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0))

        ttk.Label(input_frame, text="Days to Simulate:").grid(row=4, column=0, sticky=tk.W)
        self.days_var = tk.StringVar(value="160")
        ttk.Entry(input_frame, textvariable=self.days_var).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0))

        # Advanced parameters
        advanced_frame = ttk.LabelFrame(input_frame, text="Advanced Parameters (Auto-filled)", padding="5")
        advanced_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        advanced_frame.columnconfigure(1, weight=1)
        advanced_frame.columnconfigure(3, weight=1)

        ttk.Label(advanced_frame, text="Beta (transmission rate):").grid(row=0, column=0, sticky=tk.W)
        self.beta_var = tk.StringVar(value="0.6")
        ttk.Entry(advanced_frame, textvariable=self.beta_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        ttk.Label(advanced_frame, text="Gamma (recovery rate):").grid(row=0, column=2, sticky=tk.W)
        self.gamma_var = tk.StringVar(value="0.14")
        ttk.Entry(advanced_frame, textvariable=self.gamma_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=(5, 0))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        self.simulate_btn = ttk.Button(button_frame, text="Run Simulation", command=self.run_simulation_threaded)
        self.simulate_btn.pack(side=tk.LEFT, padx=(0, 10))
        clear_btn = ttk.Button(button_frame, text="Clear Plot", command=self.clear_plot)
        clear_btn.pack(side=tk.LEFT)

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Simulation Results", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        plt.style.use('fast')
        self.fig, self.ax = plt.subplots(figsize=(8, 4), dpi=75)
        self.canvas = FigureCanvasTkAgg(self.fig, master=results_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.on_disease_change(None)

    def on_disease_change(self, event):
        disease = self.disease_var.get().lower()
        if disease in self.disease_data:
            params = self.disease_data[disease]
            self.beta_var.set(str(params['beta']))
            self.gamma_var.set(str(params['gamma']))

    def validate_inputs(self):
        try:
            population = int(self.population_var.get())
            initial_infected = int(self.infected_var.get())
            initial_recovered = int(self.recovered_var.get())
            days = int(self.days_var.get())
            beta = float(self.beta_var.get())
            gamma = float(self.gamma_var.get())

            if population <= 0 or initial_infected < 0 or initial_recovered < 0 or days <= 0:
                raise ValueError("Values must be positive.")
            if initial_infected + initial_recovered >= population:
                raise ValueError("Infected + recovered must be less than population.")
            return population, initial_infected, initial_recovered, days, beta, gamma

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Error in input parameters:\n{str(e)}")
            return None

    def run_simulation_threaded(self):
        self.simulate_btn.config(text="Running...", state="disabled")
        thread = threading.Thread(target=self.run_simulation)
        thread.daemon = True
        thread.start()

    def run_simulation(self):
        inputs = self.validate_inputs()
        if inputs is None:
            self.simulate_btn.config(text="Run Simulation", state="normal")
            return

        population, initial_infected, initial_recovered, days, beta, gamma = inputs
        disease_name = self.disease_var.get().capitalize()

        try:
            sim = DiseaseSimulator(disease_name, population, initial_infected, initial_recovered, beta, gamma)
            t, S, I, R = sim.simulate(days)
            self.root.after(0, self.update_plot, t, S, I, R, disease_name)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Simulation Error", str(e)))
        finally:
            self.root.after(0, lambda: self.simulate_btn.config(text="Run Simulation", state="normal"))

    def update_plot(self, t, S, I, R, disease_name):
        self.ax.clear()
        step = max(1, len(t) // 200)
        self.ax.plot(t[::step], S[::step], label="Susceptible", color='blue')
        self.ax.plot(t[::step], I[::step], label="Infected", color='red')
        self.ax.plot(t[::step], R[::step], label="Recovered", color='green')
        self.ax.set_title(f"{disease_name} Simulation")
        self.ax.set_xlabel("Days")
        self.ax.set_ylabel("Population")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        if max(S[0], I.max(), R[-1]) > 1000000:
            self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        self.canvas.draw_idle()

        peak_infected = I.max()
        peak_day = np.argmax(I)
        messagebox.showinfo("Simulation Complete", f"Peak infected: {int(peak_infected):,} on day {peak_day}")

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_title("Simulation Results")
        self.ax.set_xlabel("Days")
        self.ax.set_ylabel("Population")
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = DiseaseSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
