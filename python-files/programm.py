import tkinter as tk
from tkinter import messagebox

class NutritionalDeficitCalculator:
    def __init__(self, patient_data):
        self.patient_data = patient_data

    def calculate_base_metabolism(self):
        weight = self.patient_data['weight']
        height = self.patient_data['height']
        age = self.patient_data['age']
        base_metabolism = 10 * weight + 6.25 * height - 5 * age - 161
        return base_metabolism

    def calculate_metabolic_stress_coefficient(self, stage):
        coefficients = {
            'preoperative': self._calculate_k1(),
            'postoperative': 1.2,
            'chemotherapy': 1.3,
            'radiotherapy': 1.4
        }
        return coefficients.get(stage, 1.0)

    def _calculate_k1(self):
        il6 = self.patient_data.get('il6', 0)
        albumin = self.patient_data.get('albumin', 40)
        total_protein = self.patient_data.get('total_protein', 80)
        k1 = 1 + 0.01 * il6 + 0.2 * (40 - albumin) / 40 + 0.1 * (80 - total_protein) / 80
        return k1

    def calculate_nutrient_deficit(self):
        base_metabolism = self.calculate_base_metabolism()
        metabolic_stress_k = self.calculate_metabolic_stress_coefficient(self.patient_data['treatment_stage'])
        total_energy = base_metabolism * metabolic_stress_k

        protein_deficit = 0.2 * total_energy / 4
        fat_deficit = 0.3 * total_energy / 9
        carb_deficit = 0.5 * total_energy / 4

        return {
            'base_metabolism': base_metabolism,
            'total_energy_deficit': total_energy,
            'protein_deficit': protein_deficit,
            'fat_deficit': fat_deficit,
            'carb_deficit': carb_deficit
        }

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Nutritional Deficit Calculator")
        self.root.geometry("500x600")

        # Entry fields
        self.entries = {}
        fields = ['Weight (kg)', 'Height (cm)', 'Age (years)', 'IL-6 (optional)', 'Albumin (optional)', 'Total Protein (optional)']
        for idx, field in enumerate(fields):
            label = tk.Label(root, text=field)
            label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(root)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            self.entries[field] = entry

        # Treatment stage
        tk.Label(root, text="Treatment Stage").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        self.stage_var = tk.StringVar()
        self.stage_var.set('preoperative')
        stages = ['preoperative', 'postoperative', 'chemotherapy', 'radiotherapy']
        self.stage_menu = tk.OptionMenu(root, self.stage_var, *stages)
        self.stage_menu.grid(row=6, column=1, padx=10, pady=5)

        # Buttons
        calc_button = tk.Button(root, text="Calculate Deficit", command=self.calculate_deficit)
        calc_button.grid(row=7, column=0, columnspan=2, pady=20)

        # Result display
        self.result_text = tk.Text(root, height=15, width=55)
        self.result_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def calculate_deficit(self):
        try:
            patient_data = {
                'weight': float(self.entries['Weight (kg)'].get()),
                'height': float(self.entries['Height (cm)'].get()),
                'age': int(self.entries['Age (years)'].get()),
                'il6': float(self.entries['IL-6 (optional)'].get() or 0),
                'albumin': float(self.entries['Albumin (optional)'].get() or 40),
                'total_protein': float(self.entries['Total Protein (optional)'].get() or 80),
                'treatment_stage': self.stage_var.get()
            }

            calculator = NutritionalDeficitCalculator(patient_data)
            deficit_data = calculator.calculate_nutrient_deficit()
            

            # Show results
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, f"Base Metabolism: {deficit_data['base_metabolism']:.2f} kcal/day\n")
            self.result_text.insert(tk.END, f"Total Energy Deficit: {deficit_data['total_energy_deficit']:.2f} kcal/day\n")
            self.result_text.insert(tk.END, f"Protein Deficit: {deficit_data['protein_deficit']:.2f} g/day\n")
            self.result_text.insert(tk.END, f"Fat Deficit: {deficit_data['fat_deficit']:.2f} g/day\n")
            self.result_text.insert(tk.END, f"Carb Deficit: {deficit_data['carb_deficit']:.2f} g/day\n")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values!")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

