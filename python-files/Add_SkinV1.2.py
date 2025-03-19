import os
import glob
import shutil

def create_backup(file_path):
    try:
        # Generate the backup file path with "DISABLED" at the start of the filename
        base_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)
        backup_file_name = f"DISABLED_{base_name}"
        backup_file_path = os.path.join(dir_name, backup_file_name)

        if os.path.exists(backup_file_path):
            return backup_file_path
        
        # Make a backup of the original file
        shutil.copy(file_path, backup_file_path)
        return backup_file_path
    except Exception as e:
        print(f"Error in create_backup: {e}")
        raise

def get_master_ini_file():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ini_files = glob.glob(os.path.join(script_dir, "*.ini"))
        
        ini_files = [file for file in ini_files if os.path.basename(file).lower() != "desktop.ini" and ('disabled' not in os.path.basename(file).lower() and 'icon' not in os.path.basename(file).lower())]

        if not ini_files:
            raise FileNotFoundError("No .ini file found in the script's folder.")
            
        for i,file in enumerate(ini_files):
            with open(file, encoding='utf-8') as f:
                merge_content = f.readlines()
            
            for line in merge_content:
                if line.strip().lower().startswith('; merged mod'):
                    print(f"Master .ini file found: {ini_files[i]}\n")
                    return ini_files[i]

    except Exception as e:
        print(f"Error in get_master_ini_file: {e}")
        raise

def get_swapvar_and_namespace_from_master_ini(master_ini_path,n):
    try:
        swapvar_value = 0
        namespace = ""       
        with open(master_ini_path, 'r', encoding='utf-8') as f:
            in_keyswap_section = False
            for line in f:
                line = line.strip()
                
                if line.lower().startswith('[keyswap]'):
                    in_keyswap_section = True
                    continue

                if in_keyswap_section:
                    if "$swapvar" in line:
                        try:
                            # Get the existing swapvar values and determine the next available value
                            existing_values = line.split('=')[1].strip().split(',')
                            swapvar_value = max(map(int, existing_values)) + 1  # Find the max value and increment
                            if n == 1:
                                print(f"Found existing swapvar values: {existing_values}. Next swapvar will be: {swapvar_value}\n\n")
                            break
                        except ValueError:
                            print("Error in updating swapvar values")
                            pass
                    
                if "namespace" in line.lower():
                    parts = line.split('=')  # Corrected to split by '='
                    if len(parts) == 2:
                        namespace = parts[1].strip()
        
        return swapvar_value, namespace
    except Exception as e:
        print(f"Error in get_swapvar_and_namespace_from_master_ini: {e}")
        raise

def get_relative_path(file_path, base_dir):
    try:
        relative_path = os.path.relpath(file_path, base_dir).replace(os.sep, '\\')
        return relative_path
    except Exception as e:
        print(f"Error in get_relative_path: {e}")
        raise

def is_merged_mod_ini(ini_file_path):
    """Check if the .ini file is a merged mod or a master ini."""
    try:

        with open(ini_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if the file has the 'Merged Mod' section or looks like a master ini
        if "; Merged Mod:" in content:
            if 'namespace' in content:
                return 1,0
            else:
                return 1,1  # This is a merged mod .ini
        else:
            return 0,-1  # This is a master .ini or a regular mod
    except Exception as e:
        print(f"Error in is_merged_mod_ini: {e}")
        raise

def process_namespace_ini_files(path_key_value,namespace,namespace2):
    path_key_value = {key.strip().removeprefix('.\\'): value for key, value in path_key_value.items()}
    is_in_texture = False
    updated_content = []
    for key,value in path_key_value.items():
        key = os.path.normpath(key)
        with open(key) as f:
            lines = f.readlines()
    
        for line in lines:
            if line.lower().startswith('[textureoverride'):
                is_in_texture = True
            
            if is_in_texture:
                if not line.split() or (line.startswith('[') and 'textureoverride' not in line.lower()):
                    is_in_texture = False

            
            if is_in_texture and line.lower().startswith('match_priority'):
                updated_content.append(f"match_priority = {value}\n")
                continue
            
            if is_in_texture and line.startswith(f'if $\\{namespace2}\\swapvar') or line.startswith(f'if $\\{namespace}\\swapvar'):
                updated_content.append(f"if $\\{namespace}\\swapvar == {value}\n")
                continue
                
            updated_content.append(line)           
        
        with open(key, 'w') as f:  # Open in write mode to overwrite the file
            f.writelines(updated_content)

        updated_content = []  # Clear the list for the next file

def merge_ini(master_ini_path, all_things,namespace,namespace2):
    # Read the content of the master INI file
    with open(master_ini_path, 'r', encoding='utf-8') as f:
        master_ini_content = f.readlines()  # Read lines as a list

    # Unpack the all_things list into mod_paths, existing_values_in_swapvar, and textures
    mod_paths, existing_values_in_swapvar, textures = all_things

    mod_paths_set = {os.path.normpath(path.strip()) for path in mod_paths}  # Normalize paths
    # Prepare to update content
    updated_content = []

    # Flags to indicate where to append merged mod section and track sections
    merged_mod_appended = False
    in_texture = False
    in_keyswap = False
    swapvar_count = 0
    path_key_value = {}

    for line in master_ini_content:
        line = line.strip()  # Remove leading/trailing whitespace

        # Skip empty lines in the file
        if not line:
            updated_content.append("\n")
            continue

        # Look for the section starting with '; Merged Mod' and append the new merged mods
        if line.strip().lower().startswith('; merged mod') and not merged_mod_appended:
            existing_mod_paths = line[len('; merged mod:'):].strip().split(',')
            # Strip any leading .\ from the existing paths
            existing_mod_paths = {os.path.normpath(mod.strip()).strip().lstrip('.\\') for mod in existing_mod_paths}
            new_mod_paths = mod_paths_set - existing_mod_paths  # Deduplicate
            merged_paths = sorted(existing_mod_paths | new_mod_paths)  # Merge and sort paths
            swapvar_count = len(merged_paths)
            # Add .\ before each path
            updated_content.append("; Merged Mod: " + ', '.join([path.strip() if path.startswith(".\\") else (".\\" + path).strip() for path in merged_paths]) + "\n")
            merged_mod_appended = True
            updated_content.append("\n")  # Add a blank line after the merged mod section
            continue

        # Handle $swapvar merging in the [KeySwap] section
        if line.lower().startswith('[key'):
            in_keyswap = True

        if in_keyswap and line.lower().startswith('$swapvar'):
            for i, path in enumerate(merged_paths):
                path_key_value[path] = i + 1
            merged_values = [str(v) for v in range(swapvar_count+1)]
            updated_content.append(f"$swapvar = {','.join(merged_values)}")
            updated_content.append("\n")  # Add a blank line after $swapvar
            continue

        # Handle [TextureOverride] section and prevent duplicate texture entries
        if line.lower().startswith('[textureoverride'):
            in_texture = True
            current_texture = {}  # To store the current texture's components (hash, $active)

        if in_texture:
            # Collect all lines inside the TextureOverride block
            if line.lower().startswith('['):  # We hit another section, exit texture override processing
                in_texture = False
                # Add the current texture block to the updated content
                if current_texture:
                    updated_content.append(f"[TextureOverride]\n")
                    for key, value in current_texture.items():
                        updated_content.append(f"{key} = {value}\n")
                    updated_content.append("\n")  # Add a blank line after the TextureOverride section
                # Now, we need to process this line, which is a new section header, so don't continue with texture processing.
                updated_content.append(line)
                updated_content.append("\n")
                continue
    
            # Add lines that belong to the texture override block dynamically (not just hash or $active)
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key, value = key_value
                key = key.strip()  # Strip any surrounding whitespace
                value = value.strip()  # Strip any surrounding whitespace
                if key not in current_texture:
                    current_texture[key] = value

            # End of texture block processing when an empty line is encountered
            if not line.strip():  # Empty line, end of block
                in_texture = False  # Exit texture section

        # Add non-empty lines after texture block processing
        if not in_texture:
            updated_content.append(f"{line}\n")

    # Write the updated content back to the INI file
    with open(master_ini_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_content)

    process_namespace_ini_files(path_key_value,namespace,namespace2)
    return merged_values

def rename_file_with_disable(new_ini_path):
    directory, filename = os.path.split(new_ini_path)
    new_filename = f"DISABLED{filename}"
    new_file_path = os.path.join(directory, new_filename)
    os.rename(new_ini_path, new_file_path)
    return new_file_path

def merge_master_inis(master_ini_path, new_ini_path):
    # Backup both files before merging
    backup_master_ini = create_backup(master_ini_path)
    to_add_path = new_ini_path.replace(os.path.dirname(master_ini_path), "").lstrip("\\")
    to_add_path = os.path.normpath(os.path.dirname(to_add_path))


    with open(new_ini_path, 'r', encoding='utf-8') as f:
        new_ini_content = f.readlines()

    in_keyswap = False
    in_mergedmod_section = False
    textures = []
    in_textures= False
    existing_values_in_swavpar = []
    max_value = 0
    swapvar_value, namespace = get_swapvar_and_namespace_from_master_ini(master_ini_path,0)
    _, namespace2 = get_swapvar_and_namespace_from_master_ini(new_ini_path,0)

    for i,line in enumerate(new_ini_content):
        if line.strip().startswith('; Merged Mod'):
            paths = line[len("; Merged Mod:"):].strip()  # Remove the prefix
            mod_paths = [path.strip() for path in paths.split(",") if path.strip()]
            mod_paths = [os.path.join(".", to_add_path, path.lstrip(".\\")) for path in mod_paths]
            print(f"\nmod_path : {mod_paths}\n")
        
        if line.lower().startswith("[key"):
            in_keyswap =True
        
        if line.startswith('$swapvar') and in_keyswap:
            _, value = line.split("=", 1)
            existing_values_in_swavpar = [int(v.strip()) + (swapvar_value-1) for v in value.split(",") if v.strip().isdigit() and v.strip() != '0']
            max_value = max(existing_values_in_swavpar)

        if line.lower().startswith('[textureoverride'):
            in_textures = True
        elif not line.strip():
            in_textures = False

        if in_textures:
            textures.append(line) 
    
    all_things = [mod_paths,existing_values_in_swavpar,textures]
    swapvar_value = merge_ini(master_ini_path,all_things,namespace,namespace2)
    new_file_path = rename_file_with_disable(new_ini_path)
    return mod_paths,swapvar_value




def process_ini_file(new_ini_path, swapvar_value, master_ini_path, base_dir, namespace):
    try:

        backup_master_ini = create_backup(master_ini_path)
        backup_new_ini = create_backup(new_ini_path)

        if os.path.abspath(new_ini_path) == os.path.abspath(master_ini_path):
            return

        with open(new_ini_path, 'r', encoding='utf-8') as f:
            new_ini_content = f.readlines()

        updated_content = []
        Check_Empty_Lines = 0
        in_texture_override = False
        in_if_block = False
        match_priority_found = False
        if_block_found = False
        in_hash = False
        endif_found = False

        for i, line in enumerate(new_ini_content):
            stripped_line = line.strip()

            if in_texture_override and in_hash:
                if 'match_priority' in stripped_line:
                    match_priority_found = True
                    updated_content.append(f'match_priority = {swapvar_value}\n')
                    continue
                elif not match_priority_found:
                    updated_content.append(f'match_priority = {swapvar_value}\n')
                if f'if $\\{namespace}\\swapvar' in stripped_line or (f'if $\\' in stripped_line and '\\swapvar' in stripped_line):
                    if_block_found = True
                    updated_content.append(f'if $\\{namespace}\\swapvar == {swapvar_value}\n')
                    in_hash = False
                    continue
                elif not if_block_found:
                    updated_content.append(f'if $\\{namespace}\\swapvar == {swapvar_value}\n')
                    in_if_block = True
                    in_hash = False

            if stripped_line.startswith('[TextureOverride'):
                match_priority_found = False
                if_block_found = False
                endif_found = False
                if in_if_block:
                    updated_content.append('endif\n\n')
                    in_if_block = False
                in_texture_override = True
                updated_content.append(line)
                continue

            if in_texture_override and stripped_line.startswith('hash ='):
                in_hash = True
                updated_content.append(line)
                continue

            if in_if_block:
                next_line = new_ini_content[i + 1].strip() if i + 1 < len(new_ini_content) else ''
                updated_content.append(f'    {line}')


                if not next_line and Check_Empty_Lines == 0:
                    next_lines = new_ini_content[i+1:i+6]  # Look ahead at the next 5 lines
                    for next_line in next_lines:
                        next_line = next_line.strip()
                        if next_line.startswith("["):  # New section begins, don't close block
                            break
                        elif next_line:  # Content exists after the empty line
                            Check_Empty_Lines = 1  # Indicate there is content
                            break

                if next_line.startswith('['):
                    updated_content.append('endif\n\n')
                    in_if_block = False
                    in_hash = False
                    in_texture_override = False
           
                continue

            updated_content.append(line)

        if in_if_block:
            updated_content.append('endif\n\n')

        with open(new_ini_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_content)

        with open(master_ini_path, 'r', encoding='utf-8') as f:
            master_ini_content = f.readlines()

        in_keyswap_section = False
        in_merged_mod_section = False
        new_relative_path = get_relative_path(new_ini_path, base_dir)

        new_relative_path = ".\\" + new_relative_path  # Correct this line

        for i, line in enumerate(master_ini_content):
            stripped_line = line.strip()

            if stripped_line.lower().startswith('[keyswap]'):
                in_keyswap_section = True
                continue

            if in_keyswap_section and '$swapvar' in stripped_line:
                existing_values = stripped_line.split('=')[1].strip().split(',')
                existing_values = list(map(str.strip, existing_values))
                if str(swapvar_value) not in existing_values:
                    existing_values.append(str(swapvar_value))
                master_ini_content[i] = f"$swapvar = {','.join(existing_values)}\n"
    
            if stripped_line.strip().lower().startswith('; merged mod:'):
                in_merged_mod_section = True
                parts = line.split(':')[1].strip().split(',')
                if new_relative_path not in parts:
                    parts.append(new_relative_path)
                    parts = [part.strip().lstrip('.\\') for part in parts]
                    master_ini_content[i] = "; Merged Mod: " + ', '.join([part.strip() if part.startswith(".\\") else (".\\" + part).strip() for part in parts]) + "\n"

        if not in_merged_mod_section:
            master_ini_content.append(f"; Merged Mod: {new_relative_path}\n")

        with open(master_ini_path, 'w', encoding='utf-8') as f:
            f.writelines(master_ini_content)
    
    except Exception as e:
        print(f"Error in process_ini_file: {e}")
        raise

def process_folder(folder_path):
    try:
        master_ini_path = get_master_ini_file()
        base_dir = os.path.dirname(master_ini_path)
        
        swapvar_value, namespace = get_swapvar_and_namespace_from_master_ini(master_ini_path,0)
        
        with open(master_ini_path, 'r', encoding='utf-8') as f:
            master_ini_content = f.readlines()

        # Extract all already added relative paths from the "Merged Mod" section
        added_files = []
        x = 0
        for line in master_ini_content:
            if 'Merged Mod:' in line:
                parts = line.split(':')[1].strip().split(',')
                added_files.extend([part.strip() for part in parts])
        
        # Normalize paths for comparison
        added_files = [os.path.relpath(os.path.join(base_dir, f.strip('.\\')), start=base_dir) for f in added_files if f.strip()]

        for root, dirs, files in os.walk(folder_path):
            # Skip disabled directories
            dirs[:] = [d for d in dirs if not d.lower().startswith('disabled')]
            files[:] = [f for f in files if not f.lower().startswith('disabled')]

            for file in files:
                if file.lower().endswith('.ini'):
                    new_ini_path = os.path.normpath(os.path.join(root, file))
                    if file.lower() == 'desktop.ini' or 'icon' in file.lower() or file.lower().startswith('disabled'):
                        continue

                    # Skip if this is the master .ini file
                    if new_ini_path == master_ini_path:
                        continue

                    # Normalize the path for comparison
                    normalized_path = os.path.relpath(new_ini_path, base_dir).replace("\\", "/")
                    normalized_path_alt = os.path.relpath(new_ini_path, base_dir).replace("/", "\\")
            
                    if any(normalized_path == added_file or normalized_path_alt == added_file for added_file in added_files):
                        continue                    
                        
                    check_merge, merge_type = is_merged_mod_ini(new_ini_path)

                    if check_merge == 1 and merge_type == 0:
                        print(f"Found merged mod INI: {new_ini_path}")
                        a = input(f"Do you want to merge this merged mod into {master_ini_path} (yes/no)\n? ")
                        if a.lower() == "yes":
                            # Call merge_master_inis to merge the two INIs
                            merged_added,swapvar_new_value = merge_master_inis(master_ini_path, new_ini_path)
                            swapvar_value = int(swapvar_new_value[len(swapvar_new_value)-1]) + 1
                            print(swapvar_value)
                            for i in merged_added:
                                print(f"{i}")
                                i = i.strip('.\\')
                                added_files.append(i)
                            print("\n")
                        elif a.lower() == "no":
                            pass
                        else:
                            print("Invalid Input!")
                        continue

                    relative_path = os.path.relpath(new_ini_path, base_dir)

                    print(f"Found new .ini file: {relative_path}")
                    x = 1
                    user_input = input(f"Do you want to add this ini to the master (y/n)? ")
                    print("\n")
                    
                    if user_input.lower() == 'y':
                        process_ini_file(new_ini_path, swapvar_value, master_ini_path, base_dir, namespace)
                        swapvar_value += 1
        return x
    except Exception as e:
        print(f"Error in process_folder: {e}")
        raise

if __name__ == "__main__":
    print("Welcome to ADD_SkinV1.2!😊")
    folder_path = os.path.dirname(os.path.abspath(__file__))
    if process_folder(folder_path) == 0:
        print("No ini file found!")
    print("Thanks for using this Tool!😊")
    input("Press Enter to Exit...")