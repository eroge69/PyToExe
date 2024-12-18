import os
from glob import glob

print(" ===================================================================================")
print(" ||                                                                               ||")
print(" || When prompted for values for [KeySkill2], set it to be the same as [KeySkill].||")
print(" ||                                                                               ||")
print(" || Key #1 is for keyboard input key; Key #2 is for Xbox controller input button. ||")
print(" ||                                                                               ||")
print(" ===================================================================================")
print()

def modify_ini(file_path, sections_with_keys):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    inside_section = None
    key_index = 0  # Track key order within each section

    for line in lines:
        stripped_line = line.strip()

        # Check if we are entering a relevant section
        if stripped_line.startswith('[') and stripped_line.endswith(']'):
            section_name = stripped_line[1:-1]  # Remove [ and ]
            inside_section = section_name if section_name in sections_with_keys else None
            key_index = 0  # Reset index when entering a new section
            updated_lines.append(line)
            continue

        # If inside the target section, modify the key
        if inside_section and stripped_line.startswith('key ='):
            keys = sections_with_keys[inside_section]
            if key_index < len(keys) and keys[key_index]:  # Only replace if key is not empty
                updated_lines.append(f"key = {keys[key_index]}\n")
                key_index += 1
            else:
                updated_lines.append(line)  # Leave untouched if the key input is empty
            continue

        # Append original line if no modification is made
        updated_lines.append(line)

    # Rewrite the file with modifications
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)

def process_all_ini_files(root_folder, sections):
    # Find all .ini files in the folder and subfolders
    ini_files = glob(os.path.join(root_folder, '**', '*.ini'), recursive=True)

    # Prompt user to input keys for each section
    sections_with_keys = {}
    for section in sections:
        print(f" + Enter new values for keys in section [{section}]:")        
        print()
        print("   Leave the entry empty (press Enter) if you do not want to modify its current value.")
        print()
        keys = []
        for i in range(2):  # Assuming 2 keys per section
            key = input(f"   - Key #{i + 1} for [{section}]: ").strip()
            if key:  # Only append if key is not empty
                keys.append(key)
            else:
                keys.append('')  # Append empty if input is empty
        sections_with_keys[section] = keys
        print()
        print(" ----------------------------------------------------")
        print()  # Adding a blank line after each section input

    for ini_file in ini_files:
        print(f"Processing file: {ini_file}")
        modify_ini(ini_file, sections_with_keys)

# Root folder for file search
root_folder = os.getcwd()  # Current folder
sections = ['KeySkill', 'KeySkill2', 'KeyBurst', 'KeyDash']

process_all_ini_files(root_folder, sections)
