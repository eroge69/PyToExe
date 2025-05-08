import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tensorflow as tf

import joblib

forecast_done = False

# Load your trained TensorFlow models
model_weight = tf.keras.models.load_model('Weight/model_seq2seq_final.keras')
scaler_weight_x = joblib.load('Weight/scaler_x.pkl')
scaler_weight_y = joblib.load('Weight/scaler_y.pkl')

model_mortality = tf.keras.models.load_model('Mortalities/model_seq2seq_final.keras')
scaler_mortalities_x = joblib.load('Mortalities/scaler_x.pkl')
scaler_mortalities_y = joblib.load('Mortalities/scaler_y.pkl')


def clean_exit():
    print("Cleaning up...")	
    root.destroy()
    sys.exit()
    

def extract_year_cycle_day(df):
    # Split the 'Year_Cycle_Age_Days' column by '.' and extract Year, Cycle, and Day
    df['Year'] = df['Year_Cycle_Age_Days'].str.split('.').str[0].astype(int)
    df['Cycle'] = df['Year_Cycle_Age_Days'].str.split('.').str[1].astype(int)
    df['Day'] = df['Year_Cycle_Age_Days'].str.split('.').str[2].astype(int)
    return df


def reshape_to_3d(X, expected_days):
    X = X.copy()
    X['Day'] = X['Day'].astype(int)

    #feature_cols = X.columns.difference(['Year', 'Cycle', 'Day'])
    feature_cols = [col for col in X.columns if col not in ['Year', 'Cycle', 'Day']]

    X_features = X[['Year', 'Cycle', 'Day'] + list(feature_cols)]

    # Set MultiIndex
    X_features.set_index(['Year', 'Cycle', 'Day'], inplace=True)

    # Create a complete MultiIndex with all expected Day values
    all_groups = X_features.groupby(level=['Year', 'Cycle'])

    sequences = []
    for (year, cycle), group in all_groups:
        # Reindex group to include all expected Days
        full_index = pd.MultiIndex.from_product(
            [[year], [cycle], expected_days],
            names=['Year', 'Cycle', 'Day']
        )
        group = group.reindex(full_index)  # Missing days will be filled with NaN

        # Ensure group is sorted by Day
        group = group.sort_index(level='Day')

        # Convert to NumPy array and append
        sequences.append(group.to_numpy())

    # Stack into (samples, time_steps, features)
    X_reshaped = np.stack(sequences)

    return X_reshaped
    


def predict_remaining_mortalities(new_sample_X_raw, n_days_available, model, scaler_x, scaler_y):
    """
    Predict mortalities for days (n_days_available+1 to 30) using a trained LSTM model.

    Parameters:
    ----------
    new_sample_X_raw : ndarray, shape (1, n_days_available, 7)
        Raw input data for the available days.
    n_days_available : int
        Number of available days (e.g., 3, 6, 13, etc.).
    model : keras.Model
        Trained LSTM model.
    scaler_x : StandardScaler or MinMaxScaler
        Fitted scaler for input X (first 6 features).
    scaler_y : StandardScaler or MinMaxScaler
        Fitted scaler for output y (last feature: mortalities).

    Returns:
    -------
    predicted_mortalities_original : ndarray, shape (30 - n_days_available,)
        Predicted mortalities in original scale for the remaining days.
    """

    if n_days_available < 3 or n_days_available > 27:
        raise ValueError("n_days_available must be between 3 and 27")

    # Step 1: Remove batch dimension → shape (n_days_available, 7)
    new_sample_X_raw = new_sample_X_raw[0]

    # Step 2: Split input into X (first 6 features) and y (mortalities column)
    
    #print("SIZE:",new_sample_X_raw.shape)
    
    X_features_raw = new_sample_X_raw[:, :-1]  # shape (n_days_available, 6)
    y_mortalities_raw = new_sample_X_raw[:, -1].reshape(-1, 1)  # shape (n_days_available, 1)

    # Step 3: Scale inputs
    X_features_scaled = scaler_x.transform(X_features_raw)
    y_mortalities_scaled = scaler_y.transform(y_mortalities_raw)

    # Step 4: Recombine scaled input
    scaled_input = np.hstack([X_features_scaled, y_mortalities_scaled])  # shape (n_days_available, 7)

    # Step 5: Pad to 27 time steps
    padded_input = np.zeros((27, scaled_input.shape[1]))
    padded_input[:n_days_available, :] = scaled_input

    # Step 6: Add back batch dimension → shape (1, 27, 7)
    model_input = np.expand_dims(padded_input, axis=0)

    # Step 7: Predict scaled mortalities
    predicted_scaled = model.predict([model_input, model_input])  # shape (1, 27, 1)

    # Step 8: Remove batch and feature dimensions
    predicted_scaled_flat = predicted_scaled[0, :, 0]  # shape (27,)

    # Step 9: Select only the remaining days
    start_idx = n_days_available - 3
    remaining_pred_scaled = predicted_scaled_flat[start_idx:27]

    # Step 10: Inverse-transform to original scale
    remaining_pred_scaled = remaining_pred_scaled.reshape(-1, 1)
    predicted_mortalities_original = scaler_y.inverse_transform(remaining_pred_scaled).flatten()

    return predicted_mortalities_original
    
    

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_path:
        return
    global df, forecast_done
    df = pd.read_excel(file_path)
    
    df = extract_year_cycle_day(df)
    
    forecast_done = False  # reset when new file is loaded
    display_data(df)
    
    # Clear previous plots in 'Plot' and 'Feature Importance' tabs
    for widget in frame_plot_container.winfo_children():
        widget.destroy()
    for widget in frame_importance_container.winfo_children():
        widget.destroy()


def display_data(df_display):
    for widget in frame_table.winfo_children():
        widget.destroy()

    # Add Scrollbars
    tree_scroll_y = tk.Scrollbar(frame_table, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")

    tree_scroll_x = tk.Scrollbar(frame_table, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    # Treeview widget
    tree = ttk.Treeview(frame_table, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    tree["columns"] = list(df_display.columns)
    tree["show"] = "headings"

    # Configure scrollbars
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # Set column headings
    for col in df_display.columns:
    	tree.heading(col, text=col)
    
    	# Find the max length between header and any cell
    	max_len = len(col)
    	for val in df_display[col]:
    		val_str = str(val)
    		if len(val_str) > max_len:
            		max_len = len(val_str)
    
    	# Set column width (multiply by pixel-per-character factor)
    	tree.column(col, width=(max_len * 7))  # 7 pixels per char approx


    # Insert rows
    for i, row in df_display.iterrows():
        #values = list(row)
        values = [("" if pd.isna(v) or (isinstance(v, float) and np.isnan(v)) else v) for v in row]
        tag = "forecast" if 'Forecast' in str(row.get('Tag', '')) else ""
        tree.insert("", "end", values=values, tags=(tag,))

    tree.tag_configure("forecast", foreground="red")
    tree.pack(fill="both", expand=True)


def forecast():
    global df, forecast_done
    if df is None:
        messagebox.showerror("Error", "Please load an Excel file first.")
        return
    if forecast_done:
        messagebox.showinfo("Info", "Forecast already done for this file.")
        return

    available_days = df.shape[0]
    total_days = 30
    forecast_days = total_days - available_days
    if forecast_days <= 0:
        messagebox.showinfo("Info", "All 30 days are already provided.")
        return

    features = ['Year', 'Cycle', 'Day', 'Temperature_Aveage', 'Humidity_Aveage', 'CO2_Aveage', 'Per Bird_Water',
                'Per Bird_Feed', 'grams_Live Weight', 'Mortalities_#']
    input_data = df[features]
    
    num_days = input_data.shape[0] 
    
    
    input_reshaped_1 = np.empty((0, 0, 0))
    input_reshaped_2 = np.empty((0, 0, 0))
    input_reshaped_3 = np.empty((0, 0, 0))
    input_reshaped_4 = np.empty((0, 0, 0))
    input_reshaped_5 = np.empty((0, 0, 0))

    
    if num_days >= 3: 
        input_data_1 = input_data[(input_data['Day'] >= 0) & (input_data['Day'] <= 3)]
        input_reshaped_1 = reshape_to_3d(input_data_1, list(range(1,3+1)))    
    
    if num_days >=6:
    	input_data_2 = input_data[(input_data['Day'] >= 4) & (input_data['Day'] <= 6)]    
    	input_reshaped_3 = reshape_to_3d(input_data_2, list(range(4,6+1)))
    
    
    if num_days >=13:
        input_data_3 = input_data[(input_data['Day'] >= 7) & (input_data['Day'] <= 13)]
        input_reshaped_3 = reshape_to_3d(input_data_3, list(range(7,13+1)))
    
    
    if num_days >=20: 
        input_data_4 = input_data[(input_data['Day'] >= 14) & (input_data['Day'] <= 20)]
        input_reshaped_4 = reshape_to_3d(input_data_4, list(range(14,20+1)))	
    
    
    if num_days >=27:
        input_data_5 = input_data[(input_data['Day'] >= 21) & (input_data['Day'] <= 27)] 
        input_reshaped_5 = reshape_to_3d(input_data_5, list(range(21,27+1)))
    	
    #if num_days < 3 or num_days > 27: 	
    #    root = tk.Tk()
    #    root.withdraw()
    #    messagebox.showwarning()
    #    exit()
        # messagebox.showerror()
    
    if num_days < 3 or num_days > 27: 	
        messagebox.showwarning("Warning", "Number of days must be between 3 and 27 to perform forecast.")
        return
    
        
    #input_data_full = np.concatenate([input_reshaped_1, input_reshaped_2, input_reshaped_3, input_reshaped_4, input_reshaped_5], axis=1)	
    
    input_arrays = [input_reshaped_1, input_reshaped_2, input_reshaped_3, input_reshaped_4, input_reshaped_5]
    valid_arrays = [arr for arr in input_arrays if arr.size > 0]

    if valid_arrays:
        input_data_full = np.concatenate(valid_arrays, axis=1)
    else:
        raise ValueError("No valid input arrays to concatenate.")

    
    weight_forecast = predict_remaining_mortalities(input_data_full[:,:,:6], num_days, model_weight, scaler_weight_x, scaler_weight_y)
    mortality_forecast = predict_remaining_mortalities(input_data_full, num_days, model_mortality, scaler_mortalities_x, scaler_mortalities_y)    

    forecast_rows = []
    for i in range(available_days + 1, total_days + 1):
        weight_value = weight_forecast[i - available_days - 1]
        mortality_value = mortality_forecast[i - available_days - 1]
        
        # Round weight to 2 decimal places, mortalities to nearest integer
        if np.isnan(weight_value):
            weight_value_clean = ""
        else:
            weight_value_clean = round(float(weight_value), 2)  # round to 2 decimals
            #weight_value_clean = "{:.2f}".format(float(weight_value))

        if np.isnan(mortality_value):
            mortality_value_clean = ""
        else:
            mortality_value_clean = int(round(float(mortality_value)))  # round to nearest int
            #mortality_value_clean = str(int(round(float(mortality_value))))
        
        forecast_rows.append({
            'Year': df.iloc[0]['Year'],
            'Cycle': df.iloc[0]['Cycle'],
            'Day': i,
            'Temperature_Aveage': '', #np.nan,
            'Humidity_Aveage': '', #np.nan,
            'CO2_Aveage': '', #np.nan,
            'Per Bird_Water': '', #np.nan,
            'Per Bird_Feed': '', #np.nan,
            'grams_Live Weight': weight_value_clean, #weight_forecast[i - available_days - 1],
            'Mortalities_#': mortality_value_clean, #mortality_forecast[i - available_days - 1],
            'Tag': 'Forecast'
        })

    forecast_df = pd.DataFrame(forecast_rows)
    df = pd.concat([df, forecast_df], ignore_index=True)  # ✅ update global df

    forecast_done = True
    display_data(df)


def show_plot():
    if df is None or not forecast_done:
        messagebox.showerror("Error", "Please load and forecast data first.")
        return

    # Combine actual + forecast
    combined_df = df.copy()
    if 'Tag' not in combined_df.columns:
        combined_df['Tag'] = 'Actual'

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # Plot grams_Live Weight
    axs[0].plot(combined_df['Day'], combined_df['grams_Live Weight'], marker='o', label='Weight', color='blue')
    axs[0].set_title('grams_Live Weight Forecast')
    axs[0].set_xlabel('Day')
    axs[0].set_ylabel('Weight (grams)')
    axs[0].tick_params(axis='x', rotation=45)

    # Highlight forecast points
    forecast_part = combined_df[combined_df['Tag'] == 'Forecast']
    axs[0].plot(forecast_part['Day'], forecast_part['grams_Live Weight'], marker='o', linestyle='--', color='red', label='Forecast')

    # Plot Mortalities_#
    axs[1].plot(combined_df['Day'], combined_df['Mortalities_#'], marker='s', label='Mortalities', color='green')
    axs[1].set_title('Mortalities Forecast')
    axs[1].set_xlabel('Day')
    axs[1].set_ylabel('Number of Mortalities')
    axs[1].tick_params(axis='x', rotation=45)

    axs[1].plot(forecast_part['Day'], forecast_part['Mortalities_#'], marker='s', linestyle='--', color='red', label='Forecast')

    axs[0].legend()
    axs[1].legend()
    plt.tight_layout()

    for widget in frame_plot_container.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_plot_container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def show_feature_importance():
    features = ['Temperature_Aveage', 'Humidity_Aveage', 'CO2_Aveage', 'Per Bird_Water',
                'Per Bird_Feed', 'grams_Live Weight', 'Mortalities_#']
    importance = [0.2, 0.2, 0.1, 0.15, 0.15, 0.1, 0.1]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(features, importance, color='skyblue')
    ax.set_title('Feature Importance')
    ax.set_ylabel('Importance')
    plt.xticks(rotation=45)

    for widget in frame_importance_container.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_importance_container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# Main window
root = tk.Tk()
root.title("Weight and Mortality Forecast")

# Bind X button (window close) to clean_exit
root.protocol("WM_DELETE_WINDOW", clean_exit)


df = None

# Notebook (tabs)
notebook = ttk.Notebook(root)
frame_main = ttk.Frame(notebook)
frame_plot = ttk.Frame(notebook)
frame_importance = ttk.Frame(notebook)
notebook.add(frame_main, text="Main")
notebook.add(frame_plot, text="Plot")
notebook.add(frame_importance, text="Feature Importance")
notebook.pack(fill="both", expand=True)

# Main frame (Main tab)
frame_buttons = ttk.Frame(frame_main)
frame_buttons.pack(pady=10)
btn_load = ttk.Button(frame_buttons, text="Browse Excel", command=load_file)
btn_load.pack(side="left", padx=5)
btn_forecast = ttk.Button(frame_buttons, text="Forecast", command=forecast)
btn_forecast.pack(side="left", padx=5)
btn_show_plot = ttk.Button(frame_buttons, text="Show Plot", command=show_plot)
btn_show_plot.pack(side="left", padx=5)
btn_show_importance = ttk.Button(frame_buttons, text="Show Importance", command=show_feature_importance)
btn_show_importance.pack(side="left", padx=5)
#btn_exit = ttk.Button(frame_buttons, text="Exit", command=root.destroy)
btn_exit = ttk.Button(frame_buttons, text="Exit", command=clean_exit)
btn_exit.pack(side="left", padx=5)

frame_table = ttk.Frame(frame_main)
frame_table.pack(fill="both", expand=True, padx=10, pady=10)

frame_plot_container = ttk.Frame(frame_plot)
frame_plot_container.pack(fill="both", expand=True, padx=10, pady=10)

frame_importance_container = ttk.Frame(frame_importance)
frame_importance_container.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()

