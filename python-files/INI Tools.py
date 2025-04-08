bl_info = {
    "name": "INI Tools",
    "author": "MaximiliumM",
    "version": (1, 12),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > INI Tools",
    "description": "Generate or update INI files with toggles from Blender scene",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy
import os
import re
import shutil
from datetime import datetime

def natural_sort_key(name):
    parts = re.split(r'(\d+)', name)
    return [int(part) if part.isdigit() else part.lower() for part in parts]

class NewMeshItem(bpy.types.PropertyGroup):
    mesh_name: bpy.props.StringProperty()
    drawindexed_line: bpy.props.StringProperty()

class CopyMeshLineOperator(bpy.types.Operator):
    bl_idname = "wm.copy_mesh_line"
    bl_label = "Copy Mesh Line"

    index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        item = scene.new_meshes[self.index]
        # Keep indentation consistent (4 spaces as default)
        line_to_copy = f"; {item.mesh_name}\n" \
                       f"    drawindexed = {item.drawindexed_line}\n"
        bpy.context.window_manager.clipboard = line_to_copy
        self.report({'INFO'}, f"Copied lines for {item.mesh_name} to clipboard.")
        return {'FINISHED'}

class INIToolsPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    custom_keys: bpy.props.StringProperty(
        name="Key List",
        description="Custom keys for toggling, separated by commas (e.g. '1,2,3,0,VK_OEM_PLUS')",
        default="1,2,3,4,5,6,7,8,9,0,VK_OEM_MINUS,VK_OEM_PLUS,VK_OEM_4,VK_OEM_6,VK_OEM_1,VK_OEM_7,VK_OEM_COMMA,VK_OEM_PERIOD,VK_OEM_2,VK_OEM_5"
    )

    backup_ini: bpy.props.BoolProperty(
        name="Backup INI",
        description="Enable or disable creating backup files for the selected INI.",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Set your custom keys (comma-separated):")
        layout.prop(self, "custom_keys", text="")
        layout.prop(self, "backup_ini", text="Backup INI")

class GenerateINIWithTogglesOperator(bpy.types.Operator):
    bl_idname = "wm.ini_tools"
    bl_label = "Run"
    bl_description = "Generate, update, or modify the INI file based on the current scene configuration"

    filepath: bpy.props.StringProperty(
        name="INI File",
        description="Path to the exported INI file",
        subtype='FILE_PATH',
    )

    def execute(self, context):
        scene = context.scene
        # Clear old new meshes data each time we run
        scene.new_meshes.clear()

        game_selection = scene.game_selection
        operation_mode = scene.operation_mode
        use_fix_normal_maps = (game_selection == 'ZZZ' and scene.fix_normal_maps)
        ini_filepath = bpy.path.abspath(scene.ini_file_path)

        if not ini_filepath or not os.path.exists(ini_filepath):
            self.report({'ERROR'}, f"The file '{ini_filepath}' does not exist or is not set.")
            return {'CANCELLED'}

        # Grab addon preferences
        prefs = bpy.context.preferences.addons[__name__].preferences
        do_backup = prefs.backup_ini

        backup_filepath = None
        if do_backup:
            ini_filename = os.path.basename(ini_filepath)
            base_name, ext = os.path.splitext(ini_filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(ini_filepath), "Backup")
            os.makedirs(backup_dir, exist_ok=True)

            backup_filename = f"{base_name}_{timestamp}{ext}.bkp"
            backup_filepath = os.path.join(backup_dir, backup_filename)

            shutil.copy2(ini_filepath, backup_filepath)

        if operation_mode == 'REMOVE':
            return self.remove_labels(ini_filepath)

        with open(ini_filepath, "r") as file:
            ini_content = file.readlines()

        if operation_mode == 'GENERATE':
            already_generated = any("[Constants]" in line for line in ini_content) or any("[Present]" in line for line in ini_content)
            if already_generated:
                self.report({'ERROR'}, "This INI already seems modified. Use 'Update Existing INI' instead of Generate.")
                return {'CANCELLED'}

        if operation_mode == 'GENERATE':
            patterns_to_remove = [
                re.compile(r'^\s*drawindexed\s*=\s*auto', re.IGNORECASE),
                re.compile(r'^\s*override_vertex_count', re.IGNORECASE),
                re.compile(r'^\s*override_byte_stride', re.IGNORECASE),
            ]
            ini_content = [
                line for line in ini_content
                if not any(pattern.match(line) for pattern in patterns_to_remove)
            ]

        toggle_variables = {}
        index_mappings = {}
        component_variables = {}

        def standardize_var_name(name):
            return name.lower().replace(" ", "_")

        def capitalize_var_name(var_name):
            parts = var_name.split('_')
            parts = [p.capitalize() for p in parts]
            return "".join(parts)

        def extract_name_index(name):
            name = name.split('.')[0]
            match = re.match(r"(.+?)_(\d+)$", name)
            if match:
                base_name = match.group(1)
                index = int(match.group(2))
            else:
                base_name = name
                index = None
            return base_name, index

        containers_collection = bpy.data.collections.get("Containers")
        if not containers_collection:
            self.report({'ERROR'}, "Error: 'Containers' collection not found in the scene.")
            return {'CANCELLED'}

        component_collections = [
            coll for coll in bpy.data.collections
            if coll.name != "Containers" and coll.objects
        ]

        for component_coll in component_collections:
            component_name = component_coll.name
            component_variables[component_name] = {}

            for mesh_obj in component_coll.objects:
                if mesh_obj.type != 'MESH' or mesh_obj.hide_get():
                    continue

                base_name, index = extract_name_index(mesh_obj.name)
                var_name = standardize_var_name(base_name)

                if var_name not in toggle_variables:
                    toggle_variables[var_name] = set()
                    index_mappings[var_name] = {}

                option = index if index is not None else 0
                toggle_variables[var_name].add(option)

                if var_name not in index_mappings:
                    index_mappings[var_name] = {}
                if option not in index_mappings[var_name]:
                    new_index = len(index_mappings[var_name])
                    index_mappings[var_name][option] = new_index

                if var_name not in component_variables[component_name]:
                    component_variables[component_name][var_name] = {}
                mapped_option = index_mappings[var_name][option]
                if mapped_option not in component_variables[component_name][var_name]:
                    component_variables[component_name][var_name][mapped_option] = []
                component_variables[component_name][var_name][mapped_option].append(mesh_obj)

        for var_name in toggle_variables:
            mapped_indices = list(sorted(index_mappings[var_name].values()))
            if len(mapped_indices) == 1:
                mapped_indices = [0,1]
            toggle_variables[var_name] = mapped_indices

        if operation_mode == 'GENERATE':
            prefs = bpy.context.preferences.addons[__name__].preferences
            keys_list = [k.strip() for k in prefs.custom_keys.split(",") if k.strip()]

            constants_section = ["; Constants -------------------------\n\n", "[Constants]\n\n"]
            constants_section.append("global $active\n\n")

            for var_name, options in toggle_variables.items():
                options_str = " ".join([f"[{i} = Option{i}]" for i in options])
                comment_line = f";{var_name.capitalize()} {options_str}"
                default_value = options[0]
                variable_line = f"global persist ${var_name} = {default_value}\n"
                constants_section.append(comment_line + "\n")
                constants_section.append(variable_line + "\n")

            present_section = ["\n[Present]\n", "post $active = 0\n\n"]

            key_swap_sections = []
            keys_assigned = 0
            for var_name in toggle_variables.keys():
                capitalized_name = capitalize_var_name(var_name)
                key_swap_sections.append(f"[KeySwap{capitalized_name}]\n")
                if keys_assigned < len(keys_list):
                    key = keys_list[keys_assigned]
                    keys_assigned += 1
                    key_swap_sections.append(f"key =  {key}\n")
                else:
                    key = 'REPLACE'
                    self.report({'WARNING'}, f"Not enough keys for variable '{var_name}'. Assign a key manually.")
                    key_swap_sections.append("; PLEASE REPLACE WITH ACTUAL KEY\n")
                    key_swap_sections.append(f"key =  {key}\n")
                key_swap_sections.append("condition = $active == 1\n")
                key_swap_sections.append("type = cycle\n")
                opts = ",".join(map(str, toggle_variables[var_name]))
                key_swap_sections.append(f"${var_name} = {opts}\n\n")

            insert_index = None
            for i, line in enumerate(ini_content):
                if line.strip().startswith("; Constants"):
                    insert_index = i
                    break

            if insert_index is not None:
                del_index = insert_index + 1
                while del_index < len(ini_content) and not ini_content[del_index].strip().startswith(";"):
                    del ini_content[del_index]
                ini_content = ini_content[:insert_index] + constants_section + present_section + key_swap_sections + ini_content[insert_index:]
            else:
                ini_content = constants_section + present_section + key_swap_sections + ini_content

        def get_container_name(mesh_name):
            vb_index = mesh_name.find('-vb')
            if vb_index != -1:
                return mesh_name[:vb_index]
            return mesh_name

        def compute_drawindexed_values():
            drawindexed_data = {}
            containers_collection = bpy.data.collections.get("Containers")
            if not containers_collection:
                self.report({'ERROR'}, "Error: 'Containers' collection not found during indexing.")
                return {}

            # Grab the XXMI object to check if apply_modifiers_and_shapekeys is on
            scene = bpy.context.scene
            xxmi = getattr(scene, "xxmi", None)
            apply_mods = xxmi and getattr(xxmi, "apply_modifiers_and_shapekeys", False)

            base_mesh_objects = [
                obj for obj in containers_collection.objects
                if obj.type == 'MESH' and not obj.hide_viewport and not obj.hide_get()
            ]
            base_mesh_objects.sort(key=lambda obj: natural_sort_key(obj.name))

            container_mesh_map = {}

            for base_obj in base_mesh_objects:
                container_name = get_container_name(base_obj.name)
                if not container_name:
                    print(f"Warning: Could not extract container from '{base_obj.name}'. Skipping.")
                    continue

                if container_name not in drawindexed_data:
                    drawindexed_data[container_name] = {}
                if container_name not in container_mesh_map:
                    container_mesh_map[container_name] = {
                        'mesh_lines': {},
                        'group_cumulative': 0
                    }

                sub_collection = bpy.data.collections.get(container_name)
                sub_meshes = []
                if sub_collection:
                    sub_meshes = [
                        obj for obj in sub_collection.objects
                        if obj.type == 'MESH' and not obj.hide_viewport and not obj.hide_get()
                    ]
                    sub_meshes.sort(key=lambda obj: natural_sort_key(obj.name))

                meshes_to_process = [base_obj] + sub_meshes

                for mesh_obj in meshes_to_process:
                    # We'll retrieve (or create) a "final" mesh, optionally applying modifiers
                    # & shape keys if the user toggled that. Then count faces and do tri conversion.

                    final_obj = mesh_obj
                    temp_obj = None

                    if apply_mods:
                        # Duplicate the object so we can apply stuff without affecting the original
                        temp_obj = mesh_obj.copy()
                        temp_obj.data = mesh_obj.data.copy()
                        
                        # Link the temp object to the current collection or to the scene
                        bpy.context.collection.objects.link(temp_obj)

                        # Make it active so operators apply to it
                        bpy.context.view_layer.objects.active = temp_obj
                        temp_obj.select_set(True)

                        # Convert to mesh applies all modifiers + shape keys into final_obj.data
                        bpy.ops.object.convert(target='MESH')
                        
                        final_obj = temp_obj

                    # Now do the tri-conversion on final_obj so we get an accurate face_count
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.quads_convert_to_tris()
                    bpy.ops.object.mode_set(mode='OBJECT')

                    final_mesh = final_obj.data
                    face_count = len(final_mesh.polygons)
                    index_count = face_count * 3

                    start_index_offset = container_mesh_map[container_name]['group_cumulative']
                    base_vertex_location = 0
                    container_mesh_map[container_name]['group_cumulative'] += index_count

                    drawindexed_line = f"{index_count}, {start_index_offset}, {base_vertex_location}"
                    container_mesh_map[container_name]['mesh_lines'][mesh_obj.name] = drawindexed_line

                    # Clean up temp_obj to avoid leaving duplicates in the scene
                    if temp_obj:
                        bpy.data.objects.remove(temp_obj, do_unlink=True)

            return container_mesh_map


        container_mesh_map = compute_drawindexed_values()

        resource_names = set()
        resource_pattern = re.compile(r'^\[(Resource.+?)\]', re.IGNORECASE)
        for line in ini_content:
            match = resource_pattern.match(line.strip())
            if match:
                resource_name = match.group(1)
                resource_names.add(resource_name)

        component_to_textureoverride = {}
        for component_name in component_variables.keys():
            textureoverride_name = f"TextureOverride{component_name}"
            for line in ini_content:
                if line.strip() == f"[{textureoverride_name}]":
                    component_to_textureoverride[component_name] = textureoverride_name
                    break

        if operation_mode == 'UPDATE':
            updated_mesh_lines = {}
            for component_name in component_variables.keys():
                if component_name not in container_mesh_map:
                    continue
                mesh_data = container_mesh_map[component_name]['mesh_lines']

                potential_base_meshes = [
                    obj for obj in bpy.data.collections['Containers'].objects
                    if obj.type == 'MESH' and get_container_name(obj.name) == component_name
                    and not obj.hide_viewport and not obj.hide_get()
                ]
                potential_base_meshes.sort(key=lambda obj: natural_sort_key(obj.name))

                if potential_base_meshes:
                    base_obj = potential_base_meshes[0]
                    base_line = mesh_data.get(base_obj.name, None)
                    if base_line:
                        updated_mesh_lines[base_obj.name] = base_line

                vars_for_component = component_variables[component_name]
                for var_name, options_dict in vars_for_component.items():
                    for option, meshes in options_dict.items():
                        meshes.sort(key=lambda m: natural_sort_key(m.name))
                        for m in meshes:
                            line_val = mesh_data.get(m.name, None)
                            if line_val:
                                updated_mesh_lines[m.name] = line_val

            new_ini_content = []
            last_mesh_name = None
            found_any_label = False
            updated_count = 0

            for line in ini_content:
                stripped = line.strip()
                if stripped.startswith(';'):
                    comment = stripped.lstrip(';').strip()
                    if comment:
                        found_any_label = True
                    last_mesh_name = comment
                    new_ini_content.append(line)
                    continue

                if last_mesh_name and stripped.lower().startswith('drawindexed ='):
                    if last_mesh_name in updated_mesh_lines:
                        new_val = updated_mesh_lines[last_mesh_name]
                        indent = line[:line.index('drawindexed')]
                        line = f"{indent}drawindexed = {new_val}\n"
                        updated_count += 1
                    last_mesh_name = None
                    new_ini_content.append(line)
                    continue

                new_ini_content.append(line)

            ini_content = new_ini_content

            if found_any_label and updated_count == 0:
                self.report({'WARNING'}, "No matching meshes found for update. The file structure didn't change.")
            elif not found_any_label:
                self.report({'ERROR'}, "No labeled drawindexed entries found. Cannot update existing INI without labels.")
                return {'CANCELLED'}

            labeled_meshes_in_ini = set()
            current_mesh = None
            for line in ini_content:
                stripped = line.strip()
                if stripped.startswith(';'):
                    current_mesh = stripped.lstrip(';').strip()
                elif stripped.lower().startswith("drawindexed =") and current_mesh:
                    labeled_meshes_in_ini.add(current_mesh.lower())
                    current_mesh = None
                elif stripped.startswith('['):
                    current_mesh = None

            all_scene_meshes = set()
            for component_name, vars_dict in component_variables.items():
                if component_name not in container_mesh_map:
                    continue
                mesh_data = container_mesh_map[component_name]['mesh_lines']
                for m_name in mesh_data.keys():
                    all_scene_meshes.add(m_name.lower())

            new_meshes = [m for m in all_scene_meshes if m not in labeled_meshes_in_ini]

            for component_name, vars_dict in component_variables.items():
                if component_name not in container_mesh_map:
                    continue
                mesh_data = container_mesh_map[component_name]['mesh_lines']
                for m_original_name in mesh_data.keys():
                    m_normalized = m_original_name.lower()
                    if m_normalized not in labeled_meshes_in_ini:
                        item = scene.new_meshes.add()
                        item.mesh_name = m_original_name
                        item.drawindexed_line = mesh_data[m_original_name]

            destination_path = bpy.context.scene.xxmi.destination_path if hasattr(bpy.context.scene, "xxmi") else None
            if destination_path and os.path.isdir(destination_path):
                exported_ini_file = None
                for filename in os.listdir(destination_path):
                    if filename.lower().endswith(".ini"):
                        exported_ini_file = os.path.join(destination_path, filename)
                        break

                if exported_ini_file and os.path.isfile(exported_ini_file):
                    # 1) Read the exported INI as lines
                    with open(exported_ini_file, "r", encoding="utf-8", errors="replace") as ef:
                        exported_lines = ef.readlines()

                    # 2) Parse for all draw= lines: (section, condition) -> [lines...]
                    exported_draws = self.parse_draw_lines(exported_lines)

                    # 3) Merge into our current INI content
                    ini_content = self.merge_draw_lines_into_content(exported_draws, ini_content)

                    self.report({'INFO'}, "Merged multiple 'draw =' lines from the exported .ini.")
                else:
                    self.report({'WARNING'}, "No .ini file found in destination_path. Cannot update 'draw =' lines.")
            else:
                self.report({'WARNING'}, "Invalid destination_path for XXMI Tools. Cannot update 'draw =' lines.")

            # If the user toggled "Copy Files", do the copying
            if scene.copy_files:
                self.copy_extra_files(context, ini_filepath)

        elif operation_mode == 'GENERATE':
            active_inserted = False
            for component_name in component_variables.keys():
                if component_name not in container_mesh_map:
                    continue

                mesh_data = container_mesh_map[component_name]['mesh_lines']

                potential_base_meshes = [
                    obj for obj in bpy.data.collections['Containers'].objects
                    if obj.type == 'MESH' and get_container_name(obj.name) == component_name
                    and not obj.hide_viewport and not obj.hide_get()
                ]
                potential_base_meshes.sort(key=lambda obj: natural_sort_key(obj.name))

                if not potential_base_meshes:
                    continue

                base_obj = potential_base_meshes[0]
                base_line = mesh_data.get(base_obj.name, None)
                if not base_line:
                    continue

                drawindexed_base = [(base_obj.name, base_line)]
                drawindexed_vars = {}
                vars_for_component = component_variables[component_name]
                for var_name, options_dict in vars_for_component.items():
                    drawindexed_vars[var_name] = {}
                    for option, meshes in options_dict.items():
                        meshes.sort(key=lambda m: natural_sort_key(m.name))
                        cmd_list = []
                        for m in meshes:
                            line_val = mesh_data.get(m.name, None)
                            if line_val:
                                cmd_list.append((m.name, line_val))
                        drawindexed_vars[var_name][option] = cmd_list

                if component_name in component_to_textureoverride:
                    tex_override_name = component_to_textureoverride[component_name]
                    section_header = f"[{tex_override_name}]"
                    for idx, line in enumerate(ini_content):
                        if line.strip() == section_header:
                            insert_pos = idx + 1
                            has_variables = (len(drawindexed_vars) > 0)
                            if has_variables and not active_inserted:
                                ini_content.insert(insert_pos, "$active = 1\n")
                                insert_pos += 1
                                active_inserted = True

                            while insert_pos < len(ini_content) and ini_content[insert_pos].strip():
                                insert_pos += 1

                            statements = []
                            # Base mesh
                            for (mesh_name, base_val) in drawindexed_base:
                                indent = "    "
                                statements.append(f"{indent}; {mesh_name}\n")
                                statements.append(f"{indent}drawindexed = {base_val}\n")

                            # Variables
                            for var_name in drawindexed_vars:
                                option_list = list(drawindexed_vars[var_name].keys())
                                for idx_option, option in enumerate(option_list):
                                    prefix = "if" if idx_option == 0 else "else if"
                                    statements.append(f"{prefix} ${var_name} == {option}\n")
                                    for (mesh_name, val) in drawindexed_vars[var_name][option]:
                                        statements.append(f"    ; {mesh_name}\n")
                                        statements.append(f"    drawindexed = {val}\n")
                                statements.append("endif\n")

                            ini_content = ini_content[:insert_pos] + statements + ini_content[insert_pos:]

                            if use_fix_normal_maps:
                                normal_map_resource = f"Resource{component_name}NormalMap"
                                if normal_map_resource in resource_names:
                                    ib_line_idx = idx + 1
                                    while ib_line_idx < len(ini_content):
                                        ib_line = ini_content[ib_line_idx].strip()
                                        if ib_line.lower().startswith("ib ="):
                                            ini_content.insert(ib_line_idx + 1, f"ps-t4 = {normal_map_resource}\n")
                                            break
                                        elif ib_line == "":
                                            break
                                        else:
                                            ib_line_idx += 1
                            break

        elif operation_mode == 'ADD_LABELS':
            # Build reverse map from normalized line_val to mesh names
            line_map = {}
            for container_name, container_data in container_mesh_map.items():
                mesh_data = container_data['mesh_lines']
                for m_name, line_val in mesh_data.items():
                    if not isinstance(line_val, str):
                        print(f"Warning: line_val for '{m_name}' is not a string. Skipping.")
                        continue
                    # Normalize line_val by removing spaces and converting to lowercase
                    normalized_lval = re.sub(r'\s+', '', line_val).lower()
                    if normalized_lval not in line_map:
                        line_map[normalized_lval] = []
                    line_map[normalized_lval].append(m_name)

            new_ini_content = []
            for i, line in enumerate(ini_content):
                stripped = line.strip().lower()
                if stripped.startswith("drawindexed ="):
                    # Split the line safely
                    parts = re.split(r'=', line, maxsplit=1)
                    if len(parts) < 2:
                        print(f"Warning: Malformed drawindexed line at line {i+1}: '{line.strip()}'")
                        new_ini_content.append(line)
                        continue
                    line_val = parts[1].strip()
                    # Normalize line_val by removing spaces and converting to lowercase
                    normalized_line_val = re.sub(r'\s+', '', line_val).lower()

                    # Check if the previous line is a label
                    prev_line_has_label = False
                    if new_ini_content:
                        prev_line_stripped = new_ini_content[-1].strip()
                        if prev_line_stripped.startswith(';'):
                            prev_line_has_label = True

                    candidate_meshes = line_map.get(normalized_line_val, [])
                    if candidate_meshes:
                        if len(candidate_meshes) > 1:
                            # Multiple meshes mapped to this line_val, assign and pop
                            matched_mesh = candidate_meshes.pop(0)                            
                        else:
                            # Single mesh mapped to this line_val, reuse without popping
                            matched_mesh = candidate_meshes[0]
                        if prev_line_has_label:
                            # Already labeled, add to new_meshes
                            item = scene.new_meshes.add()
                            item.mesh_name = matched_mesh
                            item.drawindexed_line = line_val  # Keep original formatting
                            new_ini_content.append(line)
                        else:
                            # Add label
                            try:
                                indent = line[:line.lower().index('drawindexed')]
                            except ValueError:
                                indent = ""
                                print(f"Warning: 'drawindexed' not found in line {i+1}: '{line.strip()}'")
                            new_ini_content.append(f"{indent}; {matched_mesh}\n")
                            new_ini_content.append(line)
                    else:
                        print(f"No match found for '{normalized_line_val}'. Adding to unknown.")
                        item = scene.new_meshes.add()
                        item.mesh_name = "UnknownMeshLine"
                        item.drawindexed_line = line_val
                        new_ini_content.append(line)
                else:
                    new_ini_content.append(line)

            ini_content = new_ini_content

        with open(ini_filepath, "w") as file:
            file.writelines(ini_content)

        if do_backup and backup_filepath:
            self.report({'INFO'}, f"INI file processed successfully. Backup created at '{os.path.basename(backup_filepath)}'")
        else:
            self.report({'INFO'}, "INI file processed successfully.")
        return {'FINISHED'}

    def parse_draw_lines(self, ini_lines):
        """
        Parse lines from an INI file, returning a dictionary of
        (section_name, condition_line) -> [list_of_draw_lines].
        
        `condition_line` is the *exact* text of the most recent
        'if' or 'else if' line (or None if outside such blocks).
        """
        data = {}
        current_section = None
        current_condition = None

        for line in ini_lines:
            stripped = line.strip()

            # Detect [SectionName]
            if stripped.startswith('[') and stripped.endswith(']'):
                current_section = stripped[1:-1]  # e.g. TextureOverrideMiyabiHairBlend
                current_condition = None
                continue
            
            # Detect if / else if lines for our 'condition' block
            # (You can refine this logic if your ini is more complex)
            lower = stripped.lower()
            if lower.startswith('if ') or lower.startswith('else if'):
                current_condition = stripped
                continue
            elif stripped == 'endif':
                current_condition = None
                continue

            # If we see a line starting with draw =
            # store it in our dictionary for that (section, condition)
            if stripped.startswith('draw ='):
                key = (current_section, current_condition)
                if key not in data:
                    data[key] = []
                data[key].append(line)  # store the full line (with indentation)
        
        return data


    def merge_draw_lines_into_content(self, exported_data, existing_lines):
        """
        For each line in existing_lines, if it's a 'draw = ...' line,
        try to replace it with the corresponding line(s) from exported_data.
        We'll match by (section_name, condition_line).
        
        Returns a new list of lines with updated draw statements.
        """
        new_lines = []
        current_section = None
        current_condition = None

        for line in existing_lines:
            stripped = line.strip()

            # Update current_section
            if stripped.startswith('[') and stripped.endswith(']'):
                current_section = stripped[1:-1]
                current_condition = None
                new_lines.append(line)
                continue
            
            # Update current_condition
            lower = stripped.lower()
            if lower.startswith('if ') or lower.startswith('else if'):
                current_condition = stripped
                new_lines.append(line)
                continue
            elif stripped == 'endif':
                current_condition = None
                new_lines.append(line)
                continue

            # If line starts with 'draw =', try to replace with lines from exported_data
            if stripped.startswith('draw ='):
                key = (current_section, current_condition)
                # If we have no matching lines from the exported file, just keep the old line
                if key not in exported_data or not exported_data[key]:
                    new_lines.append(line)
                else:
                    # Replace with all of the exported lines for that same block
                    # Typically there's only one line in the list, but we
                    # store them in a list to handle multiple lines if needed
                    for exported_line in exported_data[key]:
                        new_lines.append(exported_line)
                continue
            
            # Otherwise just copy the line verbatim
            new_lines.append(line)

        return new_lines

    def copy_extra_files(self, context, ini_filepath):
        scene = context.scene
        xxmi_path = getattr(scene, "xxmi", None)
        if not xxmi_path or not hasattr(xxmi_path, "destination_path"):
            self.report({'WARNING'}, "No valid xxmi.destination_path found. Skipping file copy.")
            return

        source_folder = bpy.path.abspath(xxmi_path.destination_path)
        if not os.path.isdir(source_folder):
            self.report({'WARNING'}, f"Source folder does not exist: {source_folder}")
            return

        target_folder = os.path.dirname(ini_filepath)
        if not os.path.isdir(target_folder):
            self.report({'WARNING'}, f"Target folder does not exist: {target_folder}")
            return

        containers_collection = bpy.data.collections.get("Containers")
        if not containers_collection:
            self.report({'ERROR'}, "No 'Containers' collection found. Skipping file copy.")
            return

        # We'll collect container names (e.g. “MiyabiBodyA”, “MiyabiHairA”, “MiyabiHairB”, etc.)
        # and group them by a ‘base_name’ and set of suffixes found.
        container_map = {}  # base_name -> set(suffixes)

        for obj in containers_collection.objects:
            if obj.type != 'MESH':
                continue
            # Example: "MiyabiBodyA-vb0=9ddb3c1b.txt"
            name_no_vb = obj.name.split('-vb0=')[0]  # e.g. "MiyabiBodyA"
            if name_no_vb == obj.name:
                # if there's no '-vb0=', fallback
                name_no_vb = name_no_vb.split('-vb')[0]

            # Check if the last letter is A, B, C, etc.
            # e.g. "MiyabiBodyA" -> suffix = "A", base_name = "MiyabiBody"
            # e.g. "MiyabiBodyABC" won't happen, but as an example
            suffix = None
            if len(name_no_vb) > 1:
                possible_suffix = name_no_vb[-1]  # last character
                if possible_suffix.isalpha():
                    suffix = possible_suffix
                    base_name = name_no_vb[:-1]
                else:
                    base_name = name_no_vb
            else:
                base_name = name_no_vb

            if base_name not in container_map:
                container_map[base_name] = set()
            if suffix:
                container_map[base_name].add(suffix)

        # Now for each base_name, build the file list and copy
        for base_name, suffixes in container_map.items():
            # Always copy these .buf files for the base_name
            blend_buf = f"{base_name}Blend.buf"
            pos_buf   = f"{base_name}Position.buf"
            tex_buf   = f"{base_name}Texcoord.buf"
            files_to_copy = [blend_buf, pos_buf, tex_buf]

            # If no suffix at all, we do base_name.ib
            if not suffixes:
                files_to_copy.append(f"{base_name}.ib")
            else:
                # Check for A, B, C, D, E... in order, stopping if missing
                possible_suffixes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
                for s in possible_suffixes:
                    if s in suffixes:
                        files_to_copy.append(f"{base_name}{s}.ib")
                    else:
                        # if one letter is missing, we stop checking further
                        break

            # Attempt to copy each file from source_folder -> target_folder
            for f_name in files_to_copy:
                src = os.path.join(source_folder, f_name)
                dst = os.path.join(target_folder, f_name)
                if os.path.isfile(src):
                    try:
                        shutil.copy2(src, dst)
                    except Exception as e:
                        self.report({'WARNING'}, f"Failed copying {f_name}: {e}")
                else:
                    # Not necessarily an error, but let's at least let user know
                    self.report({'INFO'}, f"File not found, skipping: {src}")

        self.report({'INFO'}, "Finished copying extra files.")

    def remove_labels(self, ini_filepath):
        with open(ini_filepath, "r") as file:
            ini_content = file.readlines()

        new_ini_content = []

        for i, line in enumerate(ini_content):
            stripped = line.strip()
            if stripped.startswith(';'):
                # Peek next line for a drawindexed line
                if i + 1 < len(ini_content):
                    next_stripped = ini_content[i+1].strip().lower()
                    if next_stripped.startswith("drawindexed ="):
                        # skip this label line
                        continue
            new_ini_content.append(line)

        with open(ini_filepath, "w") as file:
            file.writelines(new_ini_content)

        self.report({'INFO'}, "Labels removed successfully.")
        return {'FINISHED'}

    def invoke(self, context, event):
        scene = context.scene
        self.filepath = scene.ini_file_path
        if not self.filepath:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            return self.execute(context)

class GenerateINIPanel(bpy.types.Panel):
    bl_label = "INI Tools"
    bl_idname = "VIEW3D_PT_generate_ini"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "INI Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Select Mode:")
        col = layout.column()
        col.prop(scene, "operation_mode", expand=True)

        layout.prop(scene, "game_selection", text="Game")
        if scene.game_selection == 'ZZZ':
            layout.prop(scene, "fix_normal_maps")

        layout.prop(scene, "copy_files", text="Copy Files")

        layout.prop(scene, "ini_file_path", text="INI File")

        layout.operator("wm.ini_tools", text="Run")

        if hasattr(scene, "new_meshes") and scene.new_meshes:
            layout.separator()
            if scene.operation_mode == 'ADD_LABELS':
                layout.label(text="Unknown Values:", icon='INFO')
            else:
                layout.label(text="Newly Added Meshes:", icon='INFO')
            for i, item in enumerate(scene.new_meshes):
                row = layout.row(align=True)
                row.label(text=item.mesh_name)
                copy_op = row.operator("wm.copy_mesh_line", text="Copy", icon='COPYDOWN')
                copy_op.index = i
            if scene.operation_mode == 'ADD_LABELS':
                layout.label(text="Copy these lines and handle them manually.")
            else:
                layout.label(text="Copy drawindexed values.")

def register():
    bpy.utils.register_class(NewMeshItem)
    bpy.utils.register_class(CopyMeshLineOperator)
    bpy.utils.register_class(INIToolsPreferences)
    bpy.utils.register_class(GenerateINIWithTogglesOperator)
    bpy.utils.register_class(GenerateINIPanel)

    bpy.types.Scene.ini_file_path = bpy.props.StringProperty(
        name="INI File",
        description="Path to the exported INI file",
        subtype='FILE_PATH',
    )

    bpy.types.Scene.fix_normal_maps = bpy.props.BoolProperty(
        name="Fix Normal Maps",
        description="Add ps-t4 lines to fix normal maps (for ZZZ mode)",
        default=True,
    )

    bpy.types.Scene.game_selection = bpy.props.EnumProperty(
        name="Game",
        description="Select the game mode",
        items=[
            ('GENSHIN', "Genshin Impact", "Genshin Impact mode (No normal map fix)"),
            ('ZZZ', "Zenless Zone Zero", "Zenless Zone Zero mode (Normal map fix available)")
        ],
        default='GENSHIN'
    )

    bpy.types.Scene.operation_mode = bpy.props.EnumProperty(
        name="Operation Mode",
        description="Select which operation to perform",
        items=[
            ('GENERATE', "Generate New INI", "Generate a new INI file from scratch"),
            ('UPDATE', "Update Existing INI", "Update drawindexed values of an existing INI and list new meshes here."),
            ('ADD_LABELS', "Add Labels", "Add labels to known drawindexed values"),
            ('REMOVE', "Remove Labels", "Remove labeled drawindex comments from the INI file"),
        ],
        default='GENERATE'
    )

    bpy.types.Scene.copy_files = bpy.props.BoolProperty(
        name="Copy Files",
        description="Copy buffer/index files from exported folder to the INI folder",
        default=False
    )

    bpy.types.Scene.new_meshes = bpy.props.CollectionProperty(type=NewMeshItem)

def unregister():
    del bpy.types.Scene.new_meshes
    del bpy.types.Scene.ini_file_path
    del bpy.types.Scene.fix_normal_maps
    del bpy.types.Scene.game_selection
    del bpy.types.Scene.operation_mode
    del bpy.types.Scene.copy_files

    bpy.utils.unregister_class(GenerateINIPanel)
    bpy.utils.unregister_class(GenerateINIWithTogglesOperator)
    bpy.utils.unregister_class(INIToolsPreferences)
    bpy.utils.unregister_class(CopyMeshLineOperator)
    bpy.utils.unregister_class(NewMeshItem)

if __name__ == "__main__":
    register()
