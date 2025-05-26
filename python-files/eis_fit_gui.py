import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from impedance.models.circuits import CustomCircuit
from impedance.visualization import plot_nyquist
from impedance.preprocessing import ignoreBelowX
from tkinter import Tk, filedialog, messagebox

# Hide main tkinter window
Tk().withdraw()

# Ask user to select Excel file
file_path = filedialog.askopenfilename(
    title="Select EIS Excel File",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

if not file_path:
    messagebox.showinfo("No file selected", "Operation cancelled.")
    exit()

# Load the Excel file
try:
    df = pd.read_excel(file_path, sheet_name="Sheet1")
    Z_real = df['Re(Z)/Ohm'].values
    Z_imag = df['-Im(Z)/Ohm'].values
    Z = Z_real + 1j * Z_imag
except Exception as e:
    messagebox.showerror("Error", f"Could not read file:\n{str(e)}")
    exit()

# Generate dummy frequency values
frequencies = np.logspace(5, 1, num=len(Z))
frequencies, Z = ignoreBelowX(frequencies, Z, x=10)

# Define candidate circuits
circuits = {
    'Randles': 'R0-p(R1,C1)',
    'Randles + CPE': 'R0-p(R1,CPE1)',
    'R-C-R-C': 'R0-p(R1,C1)-p(R2,C2)',
    'R-CPE-R-CPE': 'R0-p(R1,CPE1)-p(R2,CPE2)'
}

fit_results = {}

# Fit each circuit and calculate error
for name, circuit_str in circuits.items():
    initial_guess = [1.0] * (circuit_str.count(',') + 1)
    circuit = CustomCircuit(circuit_str, initial_guess=initial_guess)
    try:
        circuit.fit(frequencies, Z)
        Z_fit = circuit.predict(frequencies)
        error = np.linalg.norm(Z - Z_fit)
        fit_results[name] = {'circuit': circuit, 'error': error}
    except Exception as e:
        fit_results[name] = {'error': np.inf, 'message': str(e)}

# Get best fitting circuit
best_fit = min(fit_results.items(), key=lambda x: x[1]['error'])
best_name, best_info = best_fit
best_circuit = best_info['circuit']

# Show result
param_str = "\n".join(f"{name} = {val:.4f}" for name, val in zip(best_circuit.param_names, best_circuit.parameters_))
messagebox.showinfo("Best Fit Found", f"Best Model: {best_name}\n\nParameters:\n{param_str}")

# Plot Nyquist
plot_nyquist(Z, fmt='o', label='Data')
plot_nyquist(best_circuit.predict(frequencies), fmt='-', label=f'Fit: {best_name}')
plt.legend()
plt.title(f'Nyquist Plot - Best Fit: {best_name}')
plt.grid(True)
plt.show()
