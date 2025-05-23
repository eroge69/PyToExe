from tkinter import *
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import laspy
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from sklearn.linear_model import RANSACRegressor
from tqdm import tqdm
import hdbscan
import subprocess
from tkinter import ttk

def select_las_folder():
    folder_path = filedialog.askdirectory(title="Select a Folder")
    if folder_path:
        entry.delete(0, tk.END)
        entry.insert(0, folder_path)

def select_lasboundary_path():
    file_path = filedialog.askopenfilename(
        title="Select lasboundary EXE",
        filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
    )
    if file_path:
        exe_path.delete(0, tk.END)
        exe_path.insert(0, file_path)    

def run_process():
    # Get input values
    LAS_PATH = entry.get().replace('/', '\\')
    ground_class_number = int(entry_01.get())
    noise_class_number = int(entry_02.get())
    epsg_code = entry_03.get()
    buffer_value = float(combobox.get())
    lasboundary_path = exe_path.get().replace('/', '\\')
    
    # Setup paths
    GROUND_CLEANED_LAS_PATH = os.path.join(LAS_PATH, "Ground_Cleaned_LAS_v2")
    noise_cluster_dir = os.path.join(GROUND_CLEANED_LAS_PATH, "Noise_Clusters")
    noise_polygon_dir = os.path.join(GROUND_CLEANED_LAS_PATH, "Noise_Polygons")
    log_file_path = os.path.join(GROUND_CLEANED_LAS_PATH, "Catalonia_Noise_Removal_Log.txt")
    
    # Create directories if they don't exist
    os.makedirs(noise_cluster_dir, exist_ok=True)
    os.makedirs(noise_polygon_dir, exist_ok=True)
    os.makedirs(GROUND_CLEANED_LAS_PATH, exist_ok=True)
    
    # Logging function
    def log_message(message):
        print(message)
        with open(log_file_path, "a") as log_file:
            log_file.write(message + "\n")
    
    # Get LAS files
    las_files = [f for f in os.listdir(LAS_PATH) if f.endswith(".las")]
    total_files = len(las_files)
    log_message(f"Number of LAS files found: {len(las_files)}\n")
    
    start_time = time.time()
    
    for i, las_file in enumerate(tqdm(las_files, desc="Processing files")):
        # Update progress
        progress = (i + 1) / total_files * 100
        progress_bar['value'] = progress
        progress_label_01.config(text=f"Progress: {int(progress)}%")
        root.update_idletasks()
        
        log_message(f"Processing: {las_file}")
        las_file_path = os.path.join(LAS_PATH, las_file)
        
        # Skip if already processed
        if os.path.exists(os.path.join(GROUND_CLEANED_LAS_PATH, las_file)):
            log_message(f"{las_file} - File already processed")
            continue
        
        # Skip large files
        if os.path.getsize(las_file_path) > 4 * 1024 * 1024 * 1024:
            log_message(f"{las_file} - File size more than 4GB")
            continue
        
        # Process LAS file
        with laspy.file.File(las_file_path, mode='r') as las:
            points = np.vstack((las.x, las.y, las.z)).T
            original_classifications = las.classification
            noise_mask = original_classifications == noise_class_number
            noise_points = points[noise_mask]
            
            if len(noise_points) > 0:
                # Cluster noise points
                clusterer = hdbscan.HDBSCAN(min_samples=50, cluster_selection_epsilon=1.0)
                labels = clusterer.fit_predict(noise_points[:, :2])
                valid_clusters_mask = labels != -1
                valid_noise_points = noise_points[valid_clusters_mask]
                valid_labels = labels[valid_clusters_mask]
                
                if len(np.unique(valid_labels)) > 0:
                    # Process each cluster
                    for cluster_id in set(valid_labels):
                        if cluster_id == -1:
                            continue
                            
                        cluster_mask = labels == cluster_id
                        final_mask = noise_mask.nonzero()[0][cluster_mask]
                        
                        # Save cluster LAS
                        cluster_file_name = las_file.split(".las")[0]
                        cluster_dir = os.path.join(noise_cluster_dir, cluster_file_name)
                        os.makedirs(cluster_dir, exist_ok=True)
                        cluster_las_path = os.path.join(cluster_dir, f"{cluster_file_name}_cluster_{cluster_id}.las")
                        
                        with laspy.file.File(cluster_las_path, mode="w", header=las.header) as out_las:
                            for attr in las.point_format.lookup:
                                if hasattr(las, attr):
                                    setattr(out_las, attr, getattr(las, attr)[final_mask])
                        
                        # Generate boundary
                        command = f'"{lasboundary_path}" -i "{cluster_las_path}" -oshp -epsg {epsg_code} -concavity 1.0'
                        subprocess.run(command, shell=True, check=True)
                    
                    # Process shapefiles
                    simplified_gdfs = []
                    for filename in os.listdir(cluster_dir):
                        if filename.lower().endswith(".shp"):
                            try:
                                gdf = gpd.read_file(os.path.join(cluster_dir, filename))
                                gdf["geometry"] = gdf["geometry"].buffer(0)  # Fix geometries
                                cluster_id = int(filename.split("cluster_")[1].split(".")[0])
                                gdf["cluster_id"] = cluster_id
                                simplified_gdfs.append(gdf)
                            except Exception as e:
                                log_message(f"{las_file} - Failed to process shapefile: {str(e)}")
                    
                    if simplified_gdfs:
                        # Merge and process polygons
                        merged_gdf = gpd.GeoDataFrame(pd.concat(simplified_gdfs, ignore_index=True), crs=simplified_gdfs[0].crs)
                        merged_gdf["geometry"] = merged_gdf.geometry.buffer(buffer_value)
                        merged_output_path = os.path.join(noise_polygon_dir, f"{las_file.split('.las')[0]}.shp")
                        merged_gdf.to_file(merged_output_path)
                        
                        # Spatial join with points
                        point_geoms = [Point(x, y) for x, y in zip(las.x, las.y)]
                        point_gdf = gpd.GeoDataFrame({'classification': original_classifications}, 
                                                   geometry=point_geoms, crs=merged_gdf.crs)
                        
                        joined = gpd.sjoin(point_gdf, merged_gdf[['cluster_id', 'geometry']], 
                                         how="inner", predicate="within")
                        
                        # Identify valid polygons
                        grouped_counts = joined.groupby(['cluster_id', 'classification']).size().unstack(fill_value=0)
                        valid_polygon_ids = grouped_counts[
                            (grouped_counts.get(ground_class_number, 0) >= 50) &
                            (grouped_counts.get(noise_class_number, 0) >= 50)
                        ].index.tolist()
                        
                        # Update classifications
                        updated_classifications = original_classifications.copy()
                        for poly_id in valid_polygon_ids:
                            idxs = joined[joined['cluster_id'] == poly_id].index
                            if len(idxs) < 30:
                                continue
                                
                            sub_points = points[idxs]
                            sub_classes = updated_classifications[idxs]
                            ground_mask = sub_classes == ground_class_number
                            ground_points = sub_points[ground_mask]
                            
                            if len(ground_points) < 15:
                                continue
                            
                            # RANSAC filtering
                            model = RANSACRegressor(residual_threshold=0.025)
                            model.fit(ground_points[:, :2], ground_points[:, 2])
                            
                            Z_pred_all = model.predict(sub_points[:, :2])
                            Z_actual_all = sub_points[:, 2]
                            
                            is_noise = (Z_actual_all - Z_pred_all) > 0.02
                            eligible_mask = np.isin(sub_classes, [ground_class_number, noise_class_number])
                            final_update_mask = is_noise & eligible_mask
                            
                            updated_classifications[idxs[final_update_mask]] = noise_class_number
                        
                        # Save updated LAS
                        output_las_path = os.path.join(GROUND_CLEANED_LAS_PATH, las_file)
                        with laspy.file.File(output_las_path, mode='w', header=las.header) as las_copy:
                            las_copy.points = las.points.copy()
                            las_copy.classification = updated_classifications
    
    # Finalize
    end_time = time.time()
    total_time = end_time - start_time
    hours, rem = divmod(total_time, 3600)
    minutes, seconds = divmod(rem, 60)
    
    label_05.config(text=f"Result LAS path: {GROUND_CLEANED_LAS_PATH}")
    label_06.config(text=f"Total Time Taken: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    label_07.config(text=f"Log file: {log_file_path}")
    
    progress_bar['value'] = 100
    progress_label_01.config(text="Progress: 100%")
    
    log_message("=" * 60)
    log_message(f"Processing Completed.\nOutput directory: {GROUND_CLEANED_LAS_PATH}")
    log_message(f"Total Time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    log_message("=" * 60)
    
    messagebox.showinfo("Information", "Process Completed Successfully")

# UI Setup
root = tk.Tk()
root.title("Catalonia Vehicle Noise Removal for MLS Data")
root.geometry('890x280')

# Input Fields
tk.Label(root, text="Catalonia Vehicle Noise Removal V1.0", font=('Times New Roman',10, 'bold')).place(x=10, y=10)

tk.Label(root, text="Input LAS Path", font=('Times New Roman',10, 'bold')).place(x=10, y=40)
entry = tk.Entry(root, font=('Times New Roman',10,'normal'), width=115)
entry.place(x=140, y=40)
tk.Button(root, text="...", command=select_las_folder).place(x=850, y=40)

tk.Label(root, text="lasboundary Path", font=('Times New Roman',10, 'bold')).place(x=10, y=70)
exe_path = tk.Entry(root, font=('Times New Roman',10,'normal'), width=115)
exe_path.place(x=140, y=70)
tk.Button(root, text="...", command=select_lasboundary_path).place(x=850, y=70)

# Parameters
tk.Label(root, text="Ground Class", font=('Times New Roman',10, 'bold')).place(x=10, y=100)
entry_01 = tk.Entry(root, font=('Times New Roman',10,'normal'), width=10)
entry_01.place(x=140, y=100)

tk.Label(root, text="Noise Class", font=('Times New Roman',10, 'bold')).place(x=250, y=100)
entry_02 = tk.Entry(root, font=('Times New Roman',10,'normal'), width=10)
entry_02.place(x=370, y=100)

tk.Label(root, text="EPSG Code", font=('Times New Roman',10, 'bold')).place(x=480, y=100)
entry_03 = tk.Entry(root, font=('Times New Roman',10,'normal'), width=10)
entry_03.place(x=550, y=100)

tk.Label(root, text="Buffer Value", font=('Times New Roman',10, 'bold')).place(x=10, y=130)
combobox = ttk.Combobox(root, values=['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], state="normal")
combobox.place(x=140, y=130)

# Progress
tk.Label(root, text="Progress", font=('Times New Roman',10, 'bold')).place(x=10, y=160)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=650, mode="determinate")
progress_bar.place(x=140, y=160)
progress_label_01 = tk.Label(root, text="Progress: 0%", font=('Times New Roman',10, 'bold'))
progress_label_01.place(x=790, y=160)

# Results
tk.Label(root, text="Result LAS path", font=('Times New Roman',10, 'bold')).place(x=10, y=190)
label_05 = tk.Label(root, text="", font=('Times New Roman',10))
label_05.place(x=140, y=190)

tk.Label(root, text="Total Time Taken", font=('Times New Roman',10, 'bold')).place(x=10, y=220)
label_06 = tk.Label(root, text="", font=('Times New Roman',10))
label_06.place(x=140, y=220)

tk.Label(root, text="Log File", font=('Times New Roman',10, 'bold')).place(x=10, y=250)
label_07 = tk.Label(root, text="", font=('Times New Roman',10))
label_07.place(x=140, y=250)

# Run Button
tk.Button(root, text="RUN", command=run_process, width=10, font=('Times New Roman',10, 'bold')).place(x=800, y=250)

root.mainloop()