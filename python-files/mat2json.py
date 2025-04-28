import os
import json
import time
import scipy.io
import h5py
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

chemin_courant = os.path.dirname(__file__)
DATA_FOLDER = "C:/NFS_Server/Usr/data/QCOut/"
OUTPUT_FOLDER = os.path.join(chemin_courant, "json_data")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# Récupérer page html : 
# scp -r -P 2929 alex@89.88.111.9:/var/www/html/S3/WebsiteVIB/index.html /Users/alex/Documents/Travail/S3/websiteVibro.html

# Upload page html : 
# scp -r -P 2929 /Users/alex/Documents/Travail/S3/websiteVibro.html alex@89.88.111.9:/var/www/html/S3/WebsiteVIB/index.html

def mat_struct_to_dict(matobj):
    """Recursively convert a MATLAB struct to a Python dictionary."""
    d = {}
    for field in matobj._fieldnames:
        elem = getattr(matobj, field)
        if hasattr(elem, "_fieldnames"):
            d[field] = mat_struct_to_dict(elem)
        elif isinstance(elem, np.ndarray):
            if elem.dtype.names is not None:
                d[field] = [mat_struct_to_dict(e) for e in elem]
            else:
                d[field] = elem.tolist()
        else:
            d[field] = elem
    return d

def process_mat_file(file_path):
    """Convert a .mat file to a structured JSON file,
    supporting classic MATLAB files and HDF5 (MATLAB 7.3+) formats."""
    try:
        structured_data = {}
        
        if h5py.is_hdf5(file_path):
            with h5py.File(file_path, "r") as f:
                structured_data = {key: np.array(f[key]).tolist() for key in f.keys()}
        else:
            data = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)
            
            data.pop('__header__', None)
            data.pop('__version__', None)
            data.pop('__globals__', None)
            
            if "v" in data:
                v_struct = data["v"]
                if hasattr(v_struct, "_fieldnames"):
                    structured_data = mat_struct_to_dict(v_struct)
                else:
                    structured_data = v_struct
            else:
                structured_data = data
        
        json_file = os.path.join(OUTPUT_FOLDER, os.path.basename(file_path).replace(".mat", ".json"))
        with open(json_file, "w") as f:
            json.dump(structured_data, f, indent=4)

        print(f"Converted and structured: {file_path} -> {json_file}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

class MatFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".mat"):
            process_mat_file(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".mat"):
            process_mat_file(event.src_path)

if __name__ == "__main__":
    print(f"Initial processing of .mat files in {DATA_FOLDER}")
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".mat"):
            file_path = os.path.join(DATA_FOLDER, filename)
            process_mat_file(file_path)
    
    print(f"Watching folder: {DATA_FOLDER}")
    event_handler = MatFileHandler()
    observer = Observer()
    observer.schedule(event_handler, DATA_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
