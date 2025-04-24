#Fix 1.2 + 1.3 +1.4
#Lightmap Fix for some characters
#Jianxin Shapekey Sum Fix
#Verina Remap, ChangLi Remap
# Author Gustav0

#Modified by Nooble to accomodate versions 2.1 and 2.2

import os
import struct
import argparse
import shutil
import re
import time
import zipfile
from pathlib import Path
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class HashMap:
    old_vs_new: Dict[str, Dict[str, str]]
    old_vs_new13: Dict[str, Dict[str, str]]
    old_vs_new14: Dict[str, Dict[str, str]]
    old_vs_new21: Dict[str, Dict[str, str]]
    old_vs_new22: Dict[str, Dict[str, str]]

@dataclass
class RemapData:
    character: str
    indices: List[int] | Dict[int, int]
    
old_vs_new = {
    "Verina": {
        "83ced9f7": "82aa82e1"
    },
    "ChangLi": {
        "d8decbca": "1ccb8008",
        "fd9483ca": "060f5303",
        "8f067708": "f23483e3",
        "c79a4ccb": "225aad5a",
        "77975500": "5f8aac45"
    },
    "Rover (Female)": {
        "be84b775": "e8b5a730"
    },
    "Rover (Male)": {
        "d53c2cc7": "c9db8418",
        "f8375eb4": "3ab7c4d1",
        "6e2f48ba": "a4be44e5"
    },
    "Baizhi": {
        "37bed36b": "718456ac",
        "52c9b804": "d7756134",
        "1a09bbb5": "43ae1deb",
        "d755a4a9": "fe4e4afe"
    },
    "Calcharo": {
        "8b43ad38": "f3e04a65",
        "cb23f0b5": "52197a16",
        "f657b0b8": "8a7d6de5"
    },
    "Jiyan": {
        "b05fac63": "9631335c",
        "1b3a68de": "7741698a"
    }
}

old_vs_new13 = {
    "YangYan": {
        "77fe24ce": "d25b9648",
        "edf438d9": "3bd37212",
        "95caeb9c": "250c59b6",
        "123bcc8e": "fba3de34",
        "bd8fff82": "c3b2a42e",
        "f42c4870": "8e27c9a2",
        "69c48be0": "1a9b9391",
        "92d4ad47": "49b790e0",
        "16f9802d": "ae886086",
        "fc40048f": "250c59b6",
        "b487d389": "6905a9bd",
        "1607589b": "02e9009d"
    },
    "Chixia": {
        "eee73787": "ab72381e",
        "435d999a": "aeb47e33",
        "45e0cedb": "7988637b",
        "489b5f2a": "94afca13",
        "cb974015": "94d10f56",
        "ba246036": "873ca04e",
        "4a2657d7": "a7141c04"
    },
    "Jianxin": {
        "80f8caf9": "e9f8341f",
        "affc2fc3": "82d39ecb",
        "ead048c8": "068dd115"
    },
    "Rover (Female)": {
        "2d5b41f6": "372bd73a",
    },
    "Verina": {
        "fd892e3c": "953daba7",
        "5981e400": "40f3c4ea",
        "63d590db": "c0ca0958"
    },
    "Encore": {
        "a347d2bc": "47c515ac",
        "6ff2b9f1": "b6021f06"
    },
    "Sanhua": {
        "2584190a": "cef6494f",
        "28708ab8": "0bd3b5ab",
        "5efe7892": "89ba19a1",
        "11b9cadd": "f0713dc7"
    },
    "Rover (Male)": {
        "f16d5dae": "a1c0d97c"
    },
    "Yinlin": {
        "00120eee": "86b95122",
        "584b7755": "750390fa",
        "87bbb0c1": "30053482",
        "9ea4dc96": "76967821",
        "58b06268": "1f0f6dc8",
        "71525c2a": "7d1b007a",
        "e50849e0": "e56f82b1",
        "3271530d": "5f0fbdb9"
    }
}

old_vs_new14 = {
    "Rover(Female)": {
        "c446a221": "99d33a32",
        "aeb47e33": "e04dea55"
    },
    "ChangLi": {
        "5f8aac45": "d14bed8b",
        "1ccb8008": "59f24b66",
        "060f5303": "277e18c9",
    },
    "Jianxin": {
        "e9f8341f": "9b60ec42",
        "82d39ecb": "29ba85c5",
        "068dd115": "bc9677ff"
    },
    "Lingyang": {
        "587edf05": "9925d10e"
    }
}

old_vs_new21 = {
    "Phoebe": {
        "3a4bf877": "8ee2fb7c",
        "a284a970": "00b2a919",
        "baea13f2": "ecac2cc5"
    },
    "Rover(Male)": {
        "d53c2cc7": "c9db8418",
        "f8375eb4": "3ab7c4d1",
        "6e2f48ba": "a4be44e5"
    },
    "Chixia": {
        "489b5f2a": "94afca13"
    },
    "YangYan": {
        "8ac49d65": "249200ff"
    }
}

old_vs_new22 = {
    "Phoebe": {
        "8ee2fb7c": "026f7616",
        "00b2a919": "8ba3d365",
        "ecac2cc5": "2c8f9580",
        "9772a12f": "83bc4e8a",  # If you have texture issues
        "3a4bf877": "8ee2fb7c",
        "a284a970": "00b2a919",
        "baea13f2": "ecac2cc5",
        "4a30f1df": "83bc4e8a",
        "83bc4e8a.dds": "4a30f1df.dds"
    },
    "Rover(Male)": {
        "c9db8418": "e18ca2cc",
        "3ab7c4d1": "f8375eb4",
        "a4be44e5": "6e2f48ba",
        "a1c0d97c": "f16d5dae",
        "7931ea8a": "fedfec0e",
        "f16d5dae.dds": "a1c0d97c.dds",
        "fedfec0e.dds": "7931ea8a"
    },
    "Rover(Female)": {
        "e8b5a730": "3533a957"
    },
    "Zhezhi": {
        "c8b08afd": "b4525ff8",
        "4cdc5987": "a7ff2cab",
        "7ebe61e9": "2208a16a"
    },
    "Lingyang": {
        "8b3c13f9": "9925d10e",
        "b239a59d": "d02c1cb1",
        "497106c3": "2e3de562"
    },
    "Jinhsi (Costume)": {
        "493ff3b9": "35f167aa",
        "2ebd42ac": "5c9d8190",
        "1f3fe8c7": "cbe0b3ad"
    },
    "Chixia": {
        "489b5f2a": "94afca13",
        "7988637b": "45e0cedb",
        "873ca04e": "ba246036",
        "ba246036.dds": "873ca04e.dds",
        "94afca13": "489b5f2a",
        "489b5f2a.dds": "94afca13.dds"
    },
    "Cantarella": {
        "35c01267": "b6deb6c2",
        "0fce3633": "0480d129",
        "63bd0a5e": "14cb399b",
        "0c65e7d2": "03af6ae8",
        "354e8743": "801b4344",
        "01c122b3": "e3127902",
        "28105b41": "884dc2c3"
    }
}


hash_maps = HashMap(old_vs_new, old_vs_new13, old_vs_new14, old_vs_new21, old_vs_new22)
    
remaps = {
    "83ced9f7": RemapData("Verina", [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
        39, 41, 40, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
        57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
        75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,
        94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108,
        109, 110, 111, 77, 112, 113, 115, 114, 116, 117, 118, 119, 120, 121,
        122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
        136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
        150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163,
        164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 178, 177, 174, 175,
        176, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
        192, 193, 194]),
    "fd9483ca": RemapData("ChangLi", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65,
                66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
                90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
                112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133,
                134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157,
                158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181,
                182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
                208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234,
                235, 236, 237, 252, 238, 257, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 258, 259, 260,
                261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 277, 278, 279, 280]),


    "060f5303": RemapData("Changli_1.4", {
        # Default Changli 1.4 remapping
        135: 137,
        137: 135,
        123: 124,
        124: 125,
        125: 126,
        126: 123,
        # Component remap data for unnamed mod
        "component_remap": {
            "vertex_offset": 16935,
            "indices": {
                64: 65,
                65: 66,
                66: 67,
                67: 64,
                76: 78,
                78: 76
            }
        }
    })
}


def log_message(log, message):
    log.append(message)
    print(message)  

def create_backup(file_path, ini_file=False):
    backup_name = ('DISABLED ' if ini_file else '') + os.path.basename(file_path) + '.bak'
    backup_path = os.path.join(os.path.dirname(file_path), backup_name)
    shutil.copy2(file_path, backup_path)
    return backup_path

def collect_ini_files(folder_path: str) -> List[str]:
    print("\nCollecting ini files, please wait...")
    ini_files = []
    exclude_keywords = {'desktop', 'ntuser', 'disabled_backup', "disabled"}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.ini'):
                if not any(keyword in file.lower() for keyword in exclude_keywords):
                    file_path = os.path.join(root, file)
                    ini_files.append(file_path)
    
    print(f"Found {len(ini_files)} ini files.")
    return ini_files

def extract_texture_from_zip(textures_folder, texture_name):
    try:
        root_path = Path(sys._MEIPASS).resolve()
    except Exception:
        root_path = Path().resolve()
    
    zip_path = root_path / 'FixTexture.zip'
    
    extracted_path = None
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extract(texture_name, textures_folder)
        extracted_path = os.path.join(textures_folder, texture_name)
    
    return extracted_path

def apply_lightmap_fix(file_path):
    log = []
    file_modified = False
    match_found = False
    texture_to_extract = None
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith("[TextureOverride"):
                texture_name = line.strip()[16:-1]
                resource_section = f"[Resource{texture_name}]"

                for j in range(i + 1, min(i + 5, len(lines))):
                    if "435d999a" in lines[j] or "aeb47e33" in lines[j]:
                        match_found = True
                        texture_to_extract = process_resource_section(
                            lines, resource_section, 
                            "Textures/FaceLightMap t=e04dea55.dds"
                        )
                        file_modified = True if texture_to_extract else file_modified
                        break
                    elif "28708ab8" in lines[j]:
                        match_found = True
                        texture_to_extract = process_resource_section(
                            lines, resource_section, 
                            "Textures/FixFaceLightMapSanhua t=0bd3b5ab.dds"
                        )
                        file_modified = True if texture_to_extract else file_modified
                        break

        # Secondary search for filename entries in [ResourceTextureX] sections
        for i, line in enumerate(lines):
            if line.strip().startswith("[Resource") and "Texture" in line:
                if i + 1 < len(lines):
                    current_filename = lines[i + 1].strip()
                    if "filename = Textures/FaceLightMap t=e04dea55.dds" in current_filename:
                        match_found = True
                        texture_to_extract = "FaceLightMap t=e04dea55.dds"
                    elif "filename = Textures/FixFaceLightMapSanhua t=0bd3b5ab.dds" in current_filename:
                        match_found = True
                        texture_to_extract = "FixFaceLightMapSanhua t=0bd3b5ab.dds"

        # Check if Textures folder exists
        textures_folder = os.path.join(os.path.dirname(file_path), 'Textures')
        if match_found and texture_to_extract:
            if os.path.isdir(textures_folder):
                texture_file = os.path.join(textures_folder, os.path.basename(texture_to_extract))
                if not os.path.isfile(texture_file):
                    extracted_path = extract_texture_from_zip(textures_folder, texture_to_extract)
                    if extracted_path:
                        if file_modified:  # Filename was updated during this run
                            log_message(log, f"Extracted texture to complete update: {os.path.basename(extracted_path)}")
                        else:  # Filename was already correct, but texture was missing
                            log_message(log, f"Extracted missing texture: {os.path.basename(extracted_path)}")
                    else:
                        log_message(log, f"Failed to extract texture: {texture_to_extract}")
                else:
                    log_message(log, f"Texture {os.path.basename(texture_file)} already exists.")
            else:
                log_message(log, f"Skipped texture check: Folder 'Textures' not found.")

        if file_modified:
            with open(file_path, 'w', encoding="utf-8") as f:
                f.writelines(lines)
            log_message(log, f'Applied lightmap fix to: {os.path.basename(file_path)}')
        elif not match_found:
            log_message(log, f'No matches for lightmap fix in: {os.path.basename(file_path)}')

    except Exception as e:
        log_message(log, f'Error processing file: {os.path.basename(file_path)}')
        log_message(log, str(e))

    return log, file_modified


def process_resource_section(lines, resource_section, target_filename):
    for k, line in enumerate(lines):
        if line.strip() == resource_section:
            if k + 1 < len(lines) and lines[k + 1].strip().startswith("filename ="):
                current_filename = lines[k + 1].strip()
                if current_filename != f"filename = {target_filename}":
                    lines[k + 1] = f"filename = {target_filename}\n"
                    print(f"Updated: {current_filename} -> filename = {target_filename}")
                    return target_filename
                else:
                    print(f"Skipped: {current_filename} (already updated)")
    return None

def ReverseCBHotFix(ini_files):
    log = []
    files_modified = 0
    
    try:
        for file_path in ini_files:
            with open(file_path, 'r', encoding="utf-8") as f:
                lines = f.readlines()
                
            file_modified = False
            for i in range(len(lines)-1):
                if "[TextureOverrideMarkBoneDataCB]" in lines[i]:
                    if "d14bed8b" in lines[i+1]:
                        lines[i+1] = lines[i+1].replace("d14bed8b", "f02baf77")
                        file_modified = True
                        
            if file_modified:
                with open(file_path, 'w', encoding="utf-8") as f:
                    f.writelines(lines)
                log_message(log, f'Applied CB hotfix to: {os.path.basename(file_path)}')
                files_modified += 1
            else:
                log_message(log, f'No CB hotfix needed for: {os.path.basename(file_path)}')
                
    except Exception as e:
        log_message(log, f'Error processing files')
        log_message(log, str(e))
        
    return log, files_modified > 0

def apply_hash_fix(folder_path):
    log = []
    processed_files_count = 0
    ini_files = collect_ini_files(folder_path)
    
    if not ini_files:
        log_message(log, "No .ini files found. Make sure you're in the correct directory.")
        return log, processed_files_count, 0
    
    # Apply CB hotfix first
    cb_log, cb_modified = ReverseCBHotFix(ini_files)
    log.extend(cb_log)
    
    # Check ini files for [ResourceMergedSkeleton] for ChangLi 1.4 hashes
    use_default_remap = False
    for ini_file in ini_files:
        try:
            with open(ini_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '[ResourceMergedSkeleton]' in content and ('060f5303' or 'fd9483ca' in content):
                    use_default_remap = True
                    break
        except Exception as e:
            log_message(log, f"Error reading {ini_file}: {str(e)}")
            continue
    
    for file_path in ini_files:
        try:
            log_message(log, f"Processing INI file: {file_path}")
        
            lightmap_log, lightmap_modified = apply_lightmap_fix(file_path)
            log.extend(lightmap_log)
            
            with open(file_path, 'r', encoding="utf-8") as f:
                s = f.read()
            meshes_folder = os.path.join(os.path.dirname(file_path), 'Meshes')
            if not os.path.exists(meshes_folder):
                log_message(log, f'Meshes folder not found in directory: {os.path.dirname(file_path)}')
                continue

            blend_files = [blend_file for blend_file in os.listdir(meshes_folder)
                           if os.path.isfile(os.path.join(meshes_folder, blend_file)) and
                           "blend" in blend_file.lower() and ".buf" in blend_file.lower() and
                           not blend_file.lower().endswith('.bak')]
            
            file_modified = lightmap_modified
            for remap_key, vg_remap in remaps.items():
                if remap_key in s:
                    if not blend_files:
                        log_message(log, f'No blend file found for {vg_remap.character} in folder: {meshes_folder}')
                        continue

                    if remap_key == "fd9483ca":
                        # Apply first remap with fd9483ca
                        log_message(log, f'Found blend files for {vg_remap.character}. Applying first remap...')
                        for blend_file in blend_files:
                            blend_file_path = os.path.join(meshes_folder, blend_file)
                            try:
                                # Create backup before modifying
                                backup_path = blend_file_path + '.bak'
                                import shutil
                                shutil.copy2(blend_file_path, backup_path)
                                log_message(log, f"Created backup: {os.path.basename(backup_path)}")

                                with open(blend_file_path, "rb") as g:
                                    blend_data = g.read()
                                    remap_data = remap(blend_data, vg_remap.indices, use_default_remap=use_default_remap)
                                with open(blend_file_path, "wb") as g:
                                    g.write(remap_data)
                                    log_message(log, f"File: {blend_file} VGs remapped successfully with fd9483ca!")
                                file_modified = True

                                # Apply second remap with 060f5303
                                log_message(log, f'Applying second remap with 060f5303...')
                                with open(blend_file_path, "rb") as g:
                                    blend_data = g.read()
                                    remap_data = remap(blend_data, remaps["060f5303"].indices, use_default_remap=use_default_remap)
                                with open(blend_file_path, "wb") as g:
                                    g.write(remap_data)
                                    log_message(log, f"File: {blend_file} VGs remapped successfully with 060f5303!")
                            except Exception as e:
                                log_message(log, f'Error remapping file: {blend_file}')
                                log_message(log, str(e))
                                continue
                    else:  
                        log_message(log, f'Found blend files for {vg_remap.character}. Applying remap...')
                        for blend_file in blend_files:
                            blend_file_path = os.path.join(meshes_folder, blend_file)
                            try:
                                # Create backup before modifying
                                backup_path = blend_file_path + '.bak'
                                import shutil
                                shutil.copy2(blend_file_path, backup_path)
                                log_message(log, f"Created backup: {os.path.basename(backup_path)}")

                                # Check if ChangLi 1.4 remap
                                if use_default_remap == True:
                                    log_message(log, f"Applying Merged Skeleton Remap for ChangLi 1.4")
                                else:
                                    log_message(log, f"Applying Component Remap for {vg_remap.character}")

                                with open(blend_file_path, "rb") as g:
                                    blend_data = g.read()
                                    remap_data = remap(blend_data, vg_remap.indices, use_default_remap=use_default_remap)
                                with open(blend_file_path, "wb") as g:
                                    g.write(remap_data)
                                    log_message(log, f"File: {blend_file} VGs remapped successfully!")
                                file_modified = True
                            except Exception as e:
                                log_message(log, f'Error remapping file: {blend_file}')
                                log_message(log, str(e))
                                continue

            jianxin_hashes_found = False
            changli_hash_found = False
            for version, hash_map in [("1.2", hash_maps.old_vs_new), 
                                      ("1.3", hash_maps.old_vs_new13), 
                                      ("1.4", hash_maps.old_vs_new14), 
                                      ("2.1", hash_maps.old_vs_new21), 
                                      ("2.2", hash_maps.old_vs_new22)]:
                version_modified = False
                for character, mappings in hash_map.items():
                    for old, new in mappings.items():
                        # Skip Cantarella hash changes under sections starting with [Resource
                        if character == "Cantarella":
                            lines = s.split('\n')
                            in_resource_section = False
                            for line in lines:
                                if line.strip().startswith("[Resource"):
                                    in_resource_section = True
                                elif line.strip().startswith("[") and not line.strip().startswith("[Resource"):
                                    in_resource_section = False

                                if in_resource_section and re.search(rf'^hash\s*=\s*{re.escape(old.lower())}', line, re.IGNORECASE):
                                    log_message(log, f"Skipped Cantarella hash change ({old} -> {new}) in [Resource] section.")
                                    break
                            else:
                                # Apply Cantarella hash change if not in a [Resource] section
                                pattern = rf'^hash\s*=\s*{re.escape(old.lower())}'
                                matches = re.findall(pattern, s, re.MULTILINE | re.IGNORECASE)
                                occurrences = len(matches)
                                if occurrences > 0:
                                    s = re.sub(pattern, f'hash = {new.lower()}', s, flags=re.MULTILINE | re.IGNORECASE)
                                    log_message(log, f'[Fix {version}] Found {old} ({occurrences} valid occurrences) ------> Match! to {new} for {character}!')
                                    file_modified = True
                                    version_modified = True
                                continue

                        # Apply hash changes for other characters
                        pattern = rf'^hash\s*=\s*{re.escape(old.lower())}'
                        matches = re.findall(pattern, s, re.MULTILINE | re.IGNORECASE)
                        occurrences = len(matches)
                        if occurrences > 0:
                            s = re.sub(pattern, f'hash = {new.lower()}', s, flags=re.MULTILINE | re.IGNORECASE)
                            log_message(log, f'[Fix {version}] Found {old} ({occurrences} valid occurrences) ------> Match! to {new} for {character}!')
                            file_modified = True
                            version_modified = True
                            if character == "Jianxin" and old in ["affc2fc3", "ead048c8"]:
                                jianxin_hashes_found = True
                            if character == "ChangLi" and (old in ["5f8aac45", "060f5303"] or new in ["d14bed8b", "277e18c9"]):
                                changli_hash_found = True
                        elif re.search(rf'^hash\s*=\s*{re.escape(new.lower())}', s, re.MULTILINE | re.IGNORECASE):
                            new_occurrences = len(re.findall(rf'^hash\s*=\s*{re.escape(new.lower())}', s, re.MULTILINE | re.IGNORECASE))
                            if old == "435d999a" or old == "aeb47e33":
                                log_message(log, f'[Fix {version}] Found {new} ({new_occurrences} valid occurrences) ------> Already remapped for Yinlin, YangYan, Chixia, JianXin and More!')
                            else:
                                log_message(log, f'[Fix {version}] Found {new} ({new_occurrences} valid occurrences) ------> Already remapped for {character}!')
                            if character == "Jianxin" and old in ["affc2fc3", "ead048c8"]:
                                jianxin_hashes_found = True
                            if character == "ChangLi" and (old in ["5f8aac45", "060f5303"] or new in ["d14bed8b", "277e18c9"]):
                                changli_hash_found = True
                
            # Special handling for Jianxin Shapekey sum, thank you Spectrum :3
            if jianxin_hashes_found:
                lines = s.split('\n')
                shapekey_line_found = False
                for i, line in enumerate(lines):
                    if line.strip().startswith("$\\WWMIv1\\shapekey_checksum"):
                        lines[i] = "$\\WWMIv1\\shapekey_checksum = 1876"
                        log_message(log, f'Updated shapekey_checksum for Jianxin')
                        file_modified = True
                        shapekey_line_found = True
                        break
                if not shapekey_line_found:
                    log_message(log, f'Warning: shapekey_checksum line not found for Jianxin')
                s = '\n'.join(lines)

            # Special handling for Changli indices
            if changli_hash_found:
                log_message(log, "Starting match fixes for Changli")
                lines = s.split('\n')
                modified_lines = []
                indices_modified = False
                for line in lines:
                    if line.strip().startswith("match_index_count") and "81513" in line:
                        modified_line = line.replace("81513", "82533")
                        log_message(log, f'Changed match_index_count from 81513 to 82533')
                        modified_lines.append(modified_line)
                        indices_modified = True
                    elif line.strip().startswith("match_first_index"):
                        if "152343" in line:
                            modified_line = line.replace("152343", "153363")
                            log_message(log, f'Changed match_first_index from 152343 to 153363')
                            modified_lines.append(modified_line)
                            indices_modified = True
                        elif "198855" in line:
                            modified_line = line.replace("198855", "199875")
                            log_message(log, f'Changed match_first_index from 198855 to 199875')
                            modified_lines.append(modified_line)
                            indices_modified = True
                        elif "283461" in line:
                            modified_line = line.replace("283461", "284481")
                            log_message(log, f'Changed match_first_index from 283461 to 284481')
                            modified_lines.append(modified_line)
                            indices_modified = True
                        elif "285489" in line:
                            modified_line = line.replace("285489", "286509")
                            log_message(log, f'Changed match_first_index from 285489 to 286509')
                            modified_lines.append(modified_line)
                            indices_modified = True
                        else:
                            modified_lines.append(line)
                    else:
                        modified_lines.append(line)
                s = '\n'.join(modified_lines)
                if indices_modified:
                    log_message(log, f'Updated indices for Changli')
                    file_modified = True

            if file_modified:
                backup_ini = create_backup(file_path, ini_file=True)
                log_message(log, f"Backup created: {backup_ini}")
                with open(file_path, 'w', encoding="utf-8") as f:
                    f.write(s)
                log_message(log, f'File: {os.path.basename(file_path)} has been modified!')
                processed_files_count += 1
            else:
                log_message(log, f'File: {os.path.basename(file_path)} had no matches. Skipping')

        except Exception as e:
            log_message(log, f'Error processing file: {os.path.basename(file_path)}')
            log_message(log, str(e))
            continue
        log_message(log, "=" * 70)
    
    return log, processed_files_count, len(ini_files)

def remap_verina(folder_path):
    return apply_hash_fix(folder_path)

def remap(blend_data, new_order, stride=8, use_default_remap=False):
    if len(blend_data) % stride != 0:
        raise ValueError("Invalid blend file length")

    remapped_blend = bytearray()

    if isinstance(new_order, dict):
        if use_default_remap:
            # Use default Changli 1.4 remapping
            for i in range(0, len(blend_data), stride):
                blendindices = struct.unpack_from("<BBBB", blend_data, i)
                blendweights = blend_data[i + 4:i + 8]

                outputindices = bytearray()
                for index in blendindices:
                    # Only use the top-level remapping indices
                    remapped_index = new_order.get(index, index) if not isinstance(new_order.get(index), dict) else index
                    outputindices.append(remapped_index)

                remapped_blend += outputindices + blendweights
        else:
            # Use component remap
            comp_remap = new_order["component_remap"]
            offset = comp_remap["vertex_offset"] * stride
            indices_map = comp_remap["indices"]

            # Copy data before component unchanged
            remapped_blend += blend_data[:offset]

            # Remap the component
            for i in range(offset, len(blend_data), stride):
                blendindices = struct.unpack_from("<BBBB", blend_data, i)
                blendweights = blend_data[i + 4:i + 8]

                outputindices = bytearray()
                for index in blendindices:
                    remapped_index = indices_map.get(index, index)
                    outputindices.append(remapped_index)

                remapped_blend += outputindices + blendweights
    else:
        # Handle list-based remapping
        for i in range(0, len(blend_data), stride):
            blendindices = struct.unpack_from("<BBBB", blend_data, i)
            blendweights = blend_data[i + 4:i + 8]

            outputindices = bytearray()
            for index in blendindices:
                remapped_index = new_order[index] if index < len(new_order) else index
                outputindices.append(remapped_index)

            remapped_blend += outputindices + blendweights

    if len(remapped_blend) != len(blend_data):
        raise ValueError("Remapped blend file is invalid")
    
    return remapped_blend

def force_remap(folder):
    '''Force remap a character based on the remap options.'''
    log = []
    processed_files_count = 0
    log_message(log, 'Remap options:')
    for i, (k, v) in enumerate(remaps.items()):
        log_message(log, f'{i+1}: {v.character}')

    while True:
        try:
            option = int(input('Select a character to remap: ')) - 1
            if 0 <= option < len(remaps):
                break
            print('Invalid option')
        except ValueError:
            print('Invalid option')

    option_key = list(remaps.keys())[option]
    
   
    use_default_remap = False
    if remaps[option_key].character == "Changli_1.4":
        log_message(log, "\nSelect remap type for Changli 1.4:")
        log_message(log, "1: Merged")
        log_message(log, "2: Component")
        while True:
            try:
                remap_type = int(input('Select remap type (1 or 2): '))
                if remap_type in [1, 2]:
                    use_default_remap = (remap_type == 1)
                    break
                print('Invalid option')
            except ValueError:
                print('Invalid option')

    
    files = os.listdir(folder)
    blend_files = [os.path.join(folder, file) for file in files if file.lower().endswith('blend.buf')]
    
    
    if len(blend_files) > 1:
        log_message(log, "Multiple blend.buf files found. Aborting to prevent unsafe modifications.")
        return log, processed_files_count, len(blend_files)
    
    if blend_files:
        bak_files = [f for f in files if f.endswith('.bak')]
        if not bak_files:
            for blend_file in blend_files:
                try:
                    
                    backup_file = blend_file + '.bak'
                    shutil.copy2(blend_file, backup_file)
                    log_message(log, f"Backup created: {backup_file}")

                    
                    with open(blend_file, "rb") as g:
                        blend_data = g.read()
                        remap_data = remap(blend_data, remaps[option_key].indices, use_default_remap=use_default_remap)

                    
                    with open(blend_file, "wb") as g:
                        g.write(remap_data)
                    log_message(log, f"File: {os.path.basename(blend_file)} VGs remapped successfully!")
                    processed_files_count += 1

                except Exception as e:
                    log_message(log, f'Error processing file: {os.path.basename(blend_file)}')
                    log_message(log, str(e))
        else:
            log_message(log, f'Found .bak files in {folder}. Skipping remapping for this folder.')
    else:
        log_message(log, f"No blend files found in folder: {folder}")

    return log, processed_files_count, len(blend_files)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--force_remap', action='store_true', default=False)
    args = parser.parse_args()
    folder_path = os.getcwd()
    start_time = time.time()
    if args.force_remap:
        log, processed_files_count, total_files = force_remap(folder_path)
    else:
        log, processed_files_count, total_files = remap_verina(folder_path)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nProcessing took {elapsed_time:.2f} seconds")
    print(f"Total files found: {total_files}")
    print(f"Processed {processed_files_count} files")

    # Only log modified files
    # modified_log = []
    # for line in log:
    #     if any(keyword in line for keyword in ['Applied', 'Updated', 'Modified', 'Changed', 'Backup created']):
    #         modified_log.append(line)

    # # Save log to file
    # log_file = "wwmi_fix_log.txt"
    # with open(log_file, "w", encoding="utf-8") as f:
    #     f.write(f"Processing took {elapsed_time:.2f} seconds\n")
    #     f.write(f"Total files found: {total_files}\n")
    #     f.write(f"Processed {processed_files_count} files\n\n")
    #     f.write("\n".join(modified_log))
    # print(f"\nLog saved to {log_file}")

    input('Press Enter to exit...')
