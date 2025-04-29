# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 15:00:46 2025

@author: Vipin VELAYUDHAN
"""

import os
import numpy as np
import math as mt
import skrf as rf
import cmath
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Function to browse and select a file
def browse_file(entry):
    filename = filedialog.askopenfilename(
        title="Select file",
        initialdir=current_directory,
        filetypes=[("S2P files", "*.s2p"), ("All files", "*.*")]
    )
    entry.delete(0, tk.END)
    entry.insert(0, filename)

# Function to calculate and save network parameters
def calculate_and_save():
    try:
        # File path retrieval
        measure_S_path = measure_entry.get()
        thru_S_path = thru_entry.get()
        reflect_S_path = reflect_entry.get()
        line_S_path = line_entry.get()

        # Check if all files are selected
        if not all([measure_S_path, thru_S_path, reflect_S_path, line_S_path]):
            messagebox.showerror("Error", "Please select all files.")
            return
        
        # Load S2P files into skrf.Network objects
        measure_S = rf.Network(measure_S_path)
        thru_S = rf.Network(thru_S_path)
        reflect_S = rf.Network(reflect_S_path)
        line_S = rf.Network(line_S_path)
        
        # Set characteristic impedance and frequency
        measure_S.z0 = 50 + 0j
        freq = measure_S.frequency.f
        Z0 = measure_S.z0
        v = 300000000         # Speed of light in vacuum (m/s)

        #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        [n, k, m] = thru_S.s.shape         # Get the shape of the S-parameter matrices
        
        # Initialize matrices for T-parameters
        thru_T = np.zeros((n, k, m), dtype=complex)
        line_T = np.zeros((n, k, m), dtype=complex)
        measure_T = np.zeros((n, k, m), dtype=complex)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        # Convert S-parameters to T-parameters
        
        for i in range(0, n):
            thru_T[i, 0, 0] = -(((thru_S.s[i, 0, 0] * thru_S.s[i, 1, 1]) - (thru_S.s[i, 0, 1] * thru_S.s[i, 1, 0]))) / thru_S.s[i, 1, 0]
            thru_T[i, 0, 1] = thru_S.s[i, 0, 0] / thru_S.s[i, 1, 0]
            thru_T[i, 1, 0] = -thru_S.s[i, 1, 1] / thru_S.s[i, 1, 0]
            thru_T[i, 1, 1] = 1 / thru_S.s[i, 1, 0]

            line_T[i, 0, 0] = -(((line_S.s[i, 0, 0] * line_S.s[i, 1, 1]) - (line_S.s[i, 0, 1] * line_S.s[i, 1, 0]))) / line_S.s[i, 1, 0]
            line_T[i, 0, 1] = line_S.s[i, 0, 0] / line_S.s[i, 1, 0]
            line_T[i, 1, 0] = -line_S.s[i, 1, 1] / line_S.s[i, 1, 0]
            line_T[i, 1, 1] = 1 / line_S.s[i, 1, 0]

            measure_T[i, 0, 0] = -(((measure_S.s[i, 0, 0] * measure_S.s[i, 1, 1]) - (measure_S.s[i, 0, 1] * measure_S.s[i, 1, 0]))) / measure_S.s[i, 1, 0]
            measure_T[i, 0, 1] = measure_S.s[i, 0, 0] / measure_S.s[i, 1, 0]
            measure_T[i, 1, 0] = -measure_S.s[i, 1, 1] / measure_S.s[i, 1, 0]
            measure_T[i, 1, 1] = 1 / measure_S.s[i, 1, 0]
            
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        # Initialize matrices for error calculations
        
        asm = np.array(m)

        R1 = np.zeros((n, k, m), dtype=complex)
        r22p22 = np.zeros((n, k, m), dtype=complex)

        IRa = np.zeros((n, k, m), dtype=complex)
        IRb = np.zeros((n, k, m), dtype=complex)

        Ra = np.zeros((n, k, m), dtype=complex)
        Rb = np.zeros((n, k, m), dtype=complex)

        Rx = np.zeros((n, k, m), dtype=complex)
        Sx_TRL = np.zeros((n, k, m), dtype=complex)

        adj = np.zeros((n, k, m), dtype=complex)
        det = np.zeros((n, k, m), dtype=complex)
        inv_thru_T = np.zeros((n, k, m), dtype=complex)

        a1 = np.zeros((n, k, m), dtype=complex)
        a2 = np.zeros((n, k, m), dtype=complex)

        a3 = np.zeros((n, k, m), dtype=complex)
        a4 = np.zeros((n, k, m), dtype=complex)

        Thru_Reconstructed = np.zeros((n, k, m), dtype=complex)
        Thru_Reconstructed_S = np.zeros((n, k, m), dtype=complex)

        ErrorA_HalfScalar = np.zeros((n, k, m), dtype=complex)
        ErrorB_HalfScalar = np.zeros((n, k, m), dtype=complex)

        ErrorA_HalfScalar_S = np.zeros((n, k, m), dtype=complex)
        ErrorB_HalfScalar_S = np.zeros((n, k, m), dtype=complex)

        Thru_Recon_ErrorHalf = np.zeros((n, k, m), dtype=complex)
        Thru_Recon_ErrorHalf_S = np.zeros((n, k, m), dtype=complex)

        ErrorA_Scal = np.zeros((n, k, m), dtype=complex)
        ErrorB_Scal = np.zeros((n, k, m), dtype=complex)

        ErrB_From_Tthru = np.zeros((n, k, m), dtype=complex)
        ErrB_ScHalf_From_Tthru = np.zeros((n, k, m), dtype=complex)

        ErrA_From_Tthru = np.zeros((n, k, m), dtype=complex)
        ErrA_ScHalf_From_Tthru = np.zeros((n, k, m), dtype=complex)

        ErrA_Sc = np.zeros((n, k, m), dtype=complex)
        ErrB_Sc = np.zeros((n, k, m), dtype=complex)

        ErrorA_Scal_S = np.zeros((n, k, m), dtype=complex)
        ErrorB_Scal_S = np.zeros((n, k, m), dtype=complex)

        ErrB_From_Tthru_S = np.zeros((n, k, m), dtype=complex)
        ErrB_ScHalf_From_Tthru_S = np.zeros((n, k, m), dtype=complex)

        ErrA_From_Tthru_S = np.zeros((n, k, m), dtype=complex)
        ErrA_ScHalf_From_Tthru_S = np.zeros((n, k, m), dtype=complex)

        ErrA_Sc_S = np.zeros((n, k, m), dtype=complex)
        ErrB_Sc_S = np.zeros((n, k, m), dtype=complex)

        Thru_3 = np.zeros((n, k, m), dtype=complex)
        Thru_3_S = np.zeros((n, k, m), dtype=complex)

        ErrorA_HalfScalar_INV = np.zeros((n, k, m), dtype=complex)
        ErrorB_HalfScalar_INV = np.zeros((n, k, m), dtype=complex)

        Ra_Scal = np.zeros((n, k, m), dtype=complex)
        Rb_Scal = np.zeros((n, k, m), dtype=complex)

        ErrorB_HalfScalar_S21dB = np.zeros((n, k, m), dtype=float)
        ErrorB_HalfScalar_S21dB = np.zeros((n, k, m), dtype=float)
        
        ErrorA_T = np.zeros((n, k, m), dtype=complex)
        ErrorB_T = np.zeros((n, k, m), dtype=complex)
        
        Thru_EAEB_T = np.zeros((n, k, m), dtype=complex)
        Thru_EAEB_S = np.zeros((n, k, m), dtype=complex)
                
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ca = 0
        b = 0

        for i in range(0, n):
            T = line_T[i, :, :] @ np.linalg.inv(thru_T[i, :, :])

            A = T[1, 0]
            B = T[1, 1] - T[0, 0]
            C = -T[0, 1]

            K1 = (-B + np.sqrt(B**2 - 4*A*C)) / (2*A)
            K2 = (-B - np.sqrt((B**2) - 4*A*C)) / (2*A)

            if abs(K1) < abs(K2):
                b = K1
                ca = 1/K2
            if abs(K2) < abs(K1):
                b = K2
                ca = 1/K1

            w1 = reflect_S.s[i, 0, 0]
            w2 = reflect_S.s[i, 1, 1]

            g = 1/thru_S.s[i, 1, 0]
            d = -((thru_S.s[i, 0, 0] * thru_S.s[i, 1, 1]) - (thru_S.s[i, 0, 1] * thru_S.s[i, 1, 0]))
            e = thru_S.s[i, 0, 0]
            f = -thru_S.s[i, 1, 1]

            gamma = (f - d * ca) / (1 - e * ca)
            beta_alfa = (e - b) / (d - b * f)

            a = np.sqrt(((w1 - b) * (1 + w2 * beta_alfa) * (d - b * f)) / ((w2 + gamma) * (1 - w1 * ca) * (1 - e * ca)))

            R1a = (w1 - b) / (a - w1 * a * ca)
            R1b = (w1 - b) / (w1 * a * ca - a)

            if abs(np.angle(R1a) * 180 / np.pi) < 90:
                a = a
                asm = a
                c = ca * a

            if abs(np.angle(R1b) * 180 / np.pi) < 90:
                a = -a
                asm = a
                c = ca * a

            R1[i, :, :] = (w1 - b) / (a - c * w1)

            alfa = (d - b * f) / (a * (1 - e * ca))
            beta = beta_alfa * alfa

            r22p22[i, :, :] = thru_T[i, 0, 0] / (a * alfa + b * gamma)

            IRa[i, 0, 0] = 1
            IRa[i, 0, 1] = -b
            IRa[i, 1, 0] = -c
            IRa[i, 1, 1] = a

            IRb[i, 0, 0] = 1
            IRb[i, 0, 1] = -beta
            IRb[i, 1, 0] = -gamma
            IRb[i, 1, 1] = alfa

            scalar_part = r22p22[i, 0, 0] * ((alfa - gamma * beta) * (a - b * c))

            if scalar_part == 0:
                raise ValueError("Division by zero encountered in the scalar part.")

            matrix_part = IRa[i, :, :] @ measure_T[i, :, :] @ IRb[i, :, :]

            Rx[i, :, :] = (1 / scalar_part) * matrix_part

            Thru_Reconstructed_MatrixPart = IRa[i, :, :] @ IRb[i, :, :]
            Thru_Reconstructed[i, :, :] = -(1 / scalar_part) * Thru_Reconstructed_MatrixPart

            Ra[i, 0, 0] = a
            Ra[i, 0, 1] = -b
            Ra[i, 1, 0] = -c
            Ra[i, 1, 1] = 1

            scalar_part2 = (a - b * c)

            Ra_Scal[i, :, :] = (1 / scalar_part2) * IRa[i, :, :]

            ErrorA_HalfScalar[i, :, :] = np.linalg.inv(Ra_Scal[i, :, :])

            Rb[i, 0, 0] = a
            Rb[i, 0, 1] = b
            Rb[i, 1, 0] = c
            Rb[i, 1, 1] = 1

            scalar_part3 = ((alfa - gamma * beta))

            Rb_Scal[i, :, :] = (1 / scalar_part3) * IRb[i, :, :]    
            
            ErrorB_HalfScalar[i, :, :] = np.linalg.inv(Rb_Scal[i, :, :])
            
            Thru_Recon_ErrorHalf[i, :, :] = (1 / r22p22[i, 0, 0]) * (ErrorA_HalfScalar[i, :, :] @ ErrorB_HalfScalar[i, :, :])
            
            
            ErrorB_HalfScalar_S[i, 1, 1] = ErrorB_HalfScalar[i, 0, 1] / ErrorB_HalfScalar[i, 1, 1]
            ErrorB_HalfScalar_S[i, 0, 0] = -ErrorB_HalfScalar[i, 1, 0] / ErrorB_HalfScalar[i, 1, 1]
            
            ErrorA_HalfScalar_S[i, 1, 1] = ErrorA_HalfScalar[i, 0, 1] / ErrorA_HalfScalar[i, 1, 1]
            ErrorA_HalfScalar_S[i, 0, 1] = np.sqrt((ErrorA_HalfScalar[i, 0, 0] / ErrorA_HalfScalar[i, 1, 1]) - ((ErrorA_HalfScalar[i, 0, 0] / ErrorA_HalfScalar[i, 1, 1]) * (ErrorA_HalfScalar[i, 1, 0] / ErrorA_HalfScalar[i, 1, 1]) * (ErrorA_HalfScalar[i, 0, 1] / ErrorA_HalfScalar[i, 0, 0])))
            ErrorA_HalfScalar_S[i, 1, 0] = ErrorA_HalfScalar_S[i, 0, 1]
            ErrorA_HalfScalar_S[i, 0, 0] = -ErrorA_HalfScalar[i, 1, 0] / ErrorA_HalfScalar[i, 1, 1]
            
            ErrorB_HalfScalar_S[i, 0, 1] = ErrorA_HalfScalar_S[i, 1, 0]
            ErrorB_HalfScalar_S[i, 1, 0] = ErrorA_HalfScalar_S[i, 1, 0]
            
            ErrorA_T[i, 0, 0] = -(((ErrorA_HalfScalar_S[i, 0, 0] * ErrorA_HalfScalar_S[i, 1, 1]) - (ErrorA_HalfScalar_S[i, 0, 1] * ErrorA_HalfScalar_S[i, 1, 0]))) / ErrorA_HalfScalar_S[i, 1, 0]
            ErrorA_T[i, 0, 1] = ErrorA_HalfScalar_S[i, 0, 0] / ErrorA_HalfScalar_S[i, 1, 0]
            ErrorA_T[i, 1, 0] = -ErrorA_HalfScalar_S[i, 1, 1] / ErrorA_HalfScalar_S[i, 1, 0]
            ErrorA_T[i, 1, 1] = 1 / ErrorA_HalfScalar_S[i, 1, 0]
            
            ErrorB_T[i, 0, 0] = -(((ErrorB_HalfScalar_S[i, 0, 0] * ErrorB_HalfScalar_S[i, 1, 1]) - (ErrorB_HalfScalar_S[i, 0, 1] * ErrorB_HalfScalar_S[i, 1, 0]))) / ErrorB_HalfScalar_S[i, 1, 0]
            ErrorB_T[i, 0, 1] = ErrorB_HalfScalar_S[i, 0, 0] / ErrorB_HalfScalar_S[i, 1, 0]
            ErrorB_T[i, 1, 0] = -ErrorB_HalfScalar_S[i, 1, 1] / ErrorB_HalfScalar_S[i, 1, 0]
            ErrorB_T[i, 1, 1] = 1 / ErrorB_HalfScalar_S[i, 1, 0]
            
            # # Thru reconstructed from Error A and Error B
            Thru_EAEB_T[i, :, :] = ErrorB_T[i, :, :] @ ErrorA_T[i, :, :]
                        
            Thru_EAEB_S[i, 1, 1] = Thru_EAEB_T[i, 0, 1] / Thru_EAEB_T[i, 1, 1]
            Thru_EAEB_S[i, 0, 1] = Thru_EAEB_T[i, 0, 0] - (Thru_EAEB_T[i, 0, 1] * Thru_EAEB_T[i, 1, 0] / Thru_EAEB_T[i, 1, 1])
            Thru_EAEB_S[i, 1, 0] = 1 / Thru_EAEB_T[i, 1, 1]
            Thru_EAEB_S[i, 0, 0] = -Thru_EAEB_T[i, 1, 0] / Thru_EAEB_T[i, 1, 1]
            
            # De-embedding of DUT
            Sx_TRL[i, 0, 0] = Rx[i, 0, 1] / Rx[i, 1, 1]
            Sx_TRL[i, 0, 1] = Rx[i, 0, 0] - (Rx[i, 0, 1] * Rx[i, 1, 0] / Rx[i, 1, 1])
            Sx_TRL[i, 1, 0] = 1 / Rx[i, 1, 1]
            Sx_TRL[i, 1, 1] = -Rx[i, 1, 0] / Rx[i, 1, 1]

        DUT_S_deemb_TRL = rf.Network(frequency=freq, s=Sx_TRL, z0=Z0)
        ErrorA = rf.Network(frequency=freq, s=IRa, z0=Z0)
        ErrorB = rf.Network(frequency=freq, s=IRb, z0=Z0)
        Thru_S_Matrix = rf.Network(frequency=freq, s=Thru_Reconstructed_S, z0=Z0)
        Thru_Recon_ErrorHalf_S_Matrix = rf.Network(frequency=freq, s=Thru_Recon_ErrorHalf_S, z0=Z0)
        ErrorA_HalfScalar_S_Matrix = rf.Network(frequency=freq, s=ErrorA_HalfScalar_S, z0=Z0)
        ErrorB_HalfScalar_S_Matrix = rf.Network(frequency=freq, s=ErrorB_HalfScalar_S, z0=Z0)
        Thru_EAEB_S_Matrix = rf.Network(frequency=freq, s=Thru_EAEB_S, z0=Z0)         

        # Prompt for save directory
        save_directory = filedialog.askdirectory(
            title="Select Save Directory",
            initialdir=current_directory
        )
        # Prompt for file extension
        extension = simpledialog.askstring("File Extension", "Enter file extension (e.g., 'calibrated'): ")

        if save_directory and extension is not None:
            ErrorA_HalfScalar_S_Matrix.write_touchstone(os.path.join(save_directory, f"ErrorA_Matrix_{extension}.s2p"))
            ErrorB_HalfScalar_S_Matrix.write_touchstone(os.path.join(save_directory, f"ErrorB_Matrix_{extension}.s2p"))
            Thru_EAEB_S_Matrix.write_touchstone(os.path.join(save_directory, f"Thru_ErrorAErrorB_Matrix_{extension}.s2p"))
            DUT_S_deemb_TRL.write_touchstone(os.path.join(save_directory, f"DUT_S_deemb_TRL_{extension}.s2p"))
            messagebox.showinfo("Success", f"Files saved successfully in: {save_directory}")
            root.destroy()  # Close the main Tkinter window after saving
        else:
            messagebox.showwarning("Warning", "Save operation cancelled.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Initialize the Tkinter root widget
root = tk.Tk()
root.title("TRL Calibration")

current_directory = os.getcwd()

# Create and place labels and entries for file paths
measure_label = tk.Label(root, text="Measure S2P File:")
measure_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
measure_entry = tk.Entry(root, width=50)
measure_entry.grid(row=0, column=1, padx=10, pady=5)
measure_button = tk.Button(root, text="Browse...", command=lambda: browse_file(measure_entry))
measure_button.grid(row=0, column=2, padx=10, pady=5)

thru_label = tk.Label(root, text="Thru S2P File:")
thru_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
thru_entry = tk.Entry(root, width=50)
thru_entry.grid(row=1, column=1, padx=10, pady=5)
thru_button = tk.Button(root, text="Browse...", command=lambda: browse_file(thru_entry))
thru_button.grid(row=1, column=2, padx=10, pady=5)

reflect_label = tk.Label(root, text="Reflect S2P File:")
reflect_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
reflect_entry = tk.Entry(root, width=50)
reflect_entry.grid(row=2, column=1, padx=10, pady=5)
reflect_button = tk.Button(root, text="Browse...", command=lambda: browse_file(reflect_entry))
reflect_button.grid(row=2, column=2, padx=10, pady=5)

line_label = tk.Label(root, text="Line S2P File:")
line_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
line_entry = tk.Entry(root, width=50)
line_entry.grid(row=3, column=1, padx=10, pady=5)
line_button = tk.Button(root, text="Browse...", command=lambda: browse_file(line_entry))
line_button.grid(row=3, column=2, padx=10, pady=5)

# Create and place the calculate and save button
calculate_button = tk.Button(root, text="Calculate and Save", command=calculate_and_save)
calculate_button.grid(row=4, column=0, columnspan=3, padx=10, pady=20)

root.mainloop()



