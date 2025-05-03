import os
import re           # Import the regular expressions module
import subprocess
import platform
import shlex
import webbrowser
import html  
import sys          # Handling command-line arguments
import shutil
from collections import defaultdict

# Path to the HTML file and mods folder
html_file = os.path.abspath('CourseOfTemptation.html')
mods_folder = os.path.join(os.getcwd(), "mods")
logs_folder = os.path.join(mods_folder, "logs")  # Log folder to capture all output
backup_folder = os.path.join(logs_folder, "backup")  # Backup folder
mainlog_file = os.path.join(logs_folder, 'MainPatchLog.txt')  # Main log file
log_file = os.path.join(logs_folder, 'ModPatchLog.txt')  # Mod log file
faillog_file = os.path.join(logs_folder, 'FailsPatchLog.txt')  # Fail log file
customlog_file = os.path.join(os.getcwd(), 'CustomLog.txt')  # Custom log file
current_file_name = os.path.basename(sys.argv[0])
distmode = False

# Define the cache directory name
cache_dir_name = 'cache'
current_directory = os.path.dirname(os.path.abspath(html_file))  # Get the current directory of the HTML file
cache_dir = os.path.join(logs_folder, cache_dir_name)  # Full path to cache directory

# Function to Create the Log Directory if it Doesn't Exist
def create_directories():
    try:
        if not os.path.exists(mods_folder):
            os.makedirs(mods_folder)
            
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)
            
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
            
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
                
    except Exception as e:
        handle_output(f"An error occurred: {e}", "console")
        
# Function to Create a Backup of the HTML File and Restore if Exists
def create_backup():
    backup_file = os.path.join(backup_folder, 'CourseOfTemptation.html')
    if not os.path.exists(backup_file):  # Check if backup already exists
        try:
            shutil.copy(html_file, backup_file)  # Create a backup
            handle_output(f"Backup created at: {backup_file}", "log")
        except Exception as e:
            handle_output(f"Failed to create backup: {e}", "console")
    else:
        # Restore the backup to the HTML file
        try:
            shutil.copy(backup_file, html_file)  # Restore the backup
            handle_output(f"Backup restored from: {backup_file} to {html_file}", "log")
        except Exception as e:
            handle_output(f"Failed to restore backup: {e}", "console")
    
# Function to Launch the HTML File in the Default Browser
def open_in_browser(html_file):
    # Check if the HTML file exists
    if not os.path.isfile(html_file):
        handle_output(f"The HTML file does not exist: {html_file}", "console")
        return

    # Define browsers and their paths
    if sys.platform.startswith('win'):
        browsers = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "opera": r"C:\Program Files\Opera\launcher.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        }
    elif sys.platform.startswith('darwin'):
        browsers = {
            "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
            "opera": "/Applications/Opera.app/Contents/MacOS/Opera",
            "safari": "/Applications/Safari.app/Contents/MacOS/Safari",
            "edge": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "brave": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        }
    else:
        handle_output("Unsupported operating system.", "console")
        return

    # Try to open Chrome first
    if os.path.exists(browsers["chrome"]):
        command_string = f"{shlex.quote(browsers['chrome'])} --app={shlex.quote(html_file)}"
        command = shlex.split(command_string)
        try:
            subprocess.Popen(command)
            return  # Exit if successful
        except Exception as e:
            handle_output(f"Failed to launch Chrome with command {command}: {e}", "console")

    handle_output("Chrome is not available. Please check your installation.", "console")

# Function to Handle Logging and Console Output
def handle_output(message, output_type=""):
    locconsole = "console"
        
    if output_type == "log":
        log_message(message, "mod")
    elif output_type == locconsole:
        print_to_console(message)
    elif output_type == "alllogs":
        log_message(message, "")
    elif output_type == "all":
        log_message(message, "mod")
    elif output_type == "failed":
        log_message(message, "failed")
    elif output_type == "custom":
        log_message(message, "custom")
     
# Function to Log Messages to a File
def log_message(message, log_type="mod"):
    if log_type == "main":
        with open(mainlog_file, 'a', encoding='utf-8') as log:
            log.write(message + '\n')
    elif log_type == "mod":
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(message + '\n')
    elif log_type == "failed":
        with open(faillog_file, 'a', encoding='utf-8') as log:
            log.write(message + '\n')
    elif log_type == "custom":
        with open(customlog_file, 'a', encoding='utf-8') as log:
            log.write(message + '\n')
    else:
        with open(mainlog_file, 'a', encoding='utf-8') as log:
            log.write(message + '\n')
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(message + '\n')

# Function to Print Messages to the Console
def print_to_console(message):
    print(message)

# Function to Clear Logs
def clear_logs():
    with open(mainlog_file, 'w') as log:
        pass  
    with open(log_file, 'w') as log:
        pass  
    with open(faillog_file, 'w') as log:
        pass  

# Function to check for repeated old lines across all mod files
def check_for_repeats(mod_file_indexes):
    line_count = defaultdict(lambda: {'count': 0, 'files': set()})

    # Count occurrences of each old line across all mod files
    for mod_file, old_lines in mod_file_indexes.items():
        for line in old_lines:
            line_count[line]['count'] += 1
            line_count[line]['files'].add(mod_file)

    # Output warnings for any old lines that appear more than once
    for line, data in line_count.items():
        if data['count'] > 1:
            files = ', '.join(data['files'])
            handle_output(f"Warning: '{line}' is repeated {data['count']} times across the following mod files: {files}", "alllogs")

# Call this function after populating mod_file_indexes
def preprocess_content(content, old_delim="Replace:", new_delim="With:"):
    """
    Processes the content by modifying all complete <tw-passagedata> blocks.

    - Inserts `<e>` after any size="width,height"> if the line after it is empty.
    - Does NOT insert `<e>` if text follows size="width,height"> on the same line.
    """

    # Pattern for matching complete <tw-passagedata> blocks.
    tw_block_pattern = re.compile(
        r'(<tw-passagedata\b(?:(?!<tw-passagedata\b).)*?</tw-passagedata>)',
        re.DOTALL
    )

    def process_tw_block(tw_block):
        # Match any size="width,height" pattern in the tw_block.
        match = re.search(r'(size="(\d+),(\d+)">)(\s*\n)(?=\S)', tw_block)
        if match:
            # Insert <e> if the next line is empty
            modified = re.sub(
                r'(size="\d+,\d+">)(\s*\n)(?=\S)',  # Match size attribute and check if it's followed by an empty line
                r'\1\2<e>\n',  # Insert <e> after size attribute if the line is empty
                tw_block
            )
            return modified
        return tw_block

    # --- CASE 1: Content contains Replace/With markers ---
    if old_delim in content and new_delim in content:
        pattern = re.compile(
            r'({0}.*?{1})(.*?)(?=(?:{0})|$)'.format(re.escape(old_delim), re.escape(new_delim)),
            re.DOTALL
        )

        def modify_block(match):
            header = match.group(1)
            block = match.group(2)
            block = tw_block_pattern.sub(lambda m: process_tw_block(m.group(0)), block)
            return header + block

        return pattern.sub(modify_block, content)

    # --- CASE 2: Content without Replace/With markers ---
    return tw_block_pattern.sub(lambda m: process_tw_block(m.group(0)), content)

def escape_html_between_tags(text, start_tag="<e>", end_tag="</e>", delete_tags=True):
    """
    Escapes HTML characters only within blocks delimited by lines that are exactly
    the start tag and end tag. Inline tags are not handled by this version.
    
    When delete_tags=True:
      - Lines that contain only the start or end tag are omitted.
      - The inner content is replaced by its escaped version.
    
    When delete_tags=False:
      - The start and end tag lines are kept unmodified.
      - The inner content is replaced by its escaped version.
    
    If a control keyword (e.g. "Replace:", "With:", "Add Passage:", or "Add Javascript")
    is encountered while inside a tag block, the block is terminated immediately.
    
    If the inner content already appears escaped (i.e. contains "&lt;" or "&quot;"),
    it will not be escaped again.
    """
    result = []
    inside = False
    buffer = []
    control_keywords = ["Replace:", "With:", "Add Passage:", "Add Javascript"]
    
    lines = text.split("\n")
    for line in lines:
        stripped_line = line.strip()
        
        # Check for control keywords
        if any(kw in stripped_line for kw in control_keywords):
            if inside:
                content = "\n".join(buffer)
                if "&lt;" in content or "&quot;" in content:
                    escaped_content = content
                else:
                    escaped_content = html.escape(content)
                if delete_tags:
                    result.append(escaped_content)
                else:
                    # When not deleting, keep the original start tag line (already in output)
                    result.append(escaped_content)
                    # Do not add an extra end tag here.
                buffer = []
                inside = False
            result.append(line)
            continue
        
        # Start tag on its own line
        if stripped_line == start_tag:
            inside = True
            if not delete_tags:
                result.append(line)  # output the start tag as-is
            continue
        
        # End tag on its own line
        if stripped_line == end_tag:
            if inside:
                content = "\n".join(buffer)
                if "&lt;" in content or "&quot;" in content:
                    escaped_content = content
                else:
                    escaped_content = html.escape(content)
                if delete_tags:
                    result.append(escaped_content)
                else:
                    result.append(escaped_content)
                    result.append(line)  # output the end tag as-is
                buffer = []
                inside = False
            else:
                result.append(line)
            continue
        
        # Inside a tag block: collect the content
        if inside:
            buffer.append(line)
        else:
            result.append(line)
    
    # If still inside a tag block at the end, flush the buffer.
    if inside:
        content = "\n".join(buffer)
        if "&lt;" in content or "&quot;" in content:
            escaped_content = content
        else:
            escaped_content = html.escape(content)
        if delete_tags:
            result.append(escaped_content)
        else:
            result.append(escaped_content)
    
    return "\n".join(result)

def pre_proc(mod_content, old_delim):
    # For new-style directives, define shortcuts so that the target closing tag is unambiguous.
    shortcuts = {
        "Add Passage:": "</tw-storydata>",
        "Add Javascript:": "</script><tw-passagedata"
    }
    keys_pattern = "|".join(map(re.escape, shortcuts.keys()))
    pattern = (
        rf"^(?P<key>{keys_pattern})\s*\n"          # Key must be at start-of-line
        rf"(?P<content>.*?)(?="                       # Non-greedy capture of content until...
        rf"^(?:{re.escape(old_delim)})"               # ...a line starting with the old delimiter, or...
        rf"|^(?:{keys_pattern})"                      # ...a new key at the beginning of a line, or...
        rf"|\Z)"                                     # ...end of the string.
    )

    def replacer(match):
        key = match.group("key")
        content = match.group("content").strip()
        wrap = shortcuts[key]
        # Note: instead of appending the closing tag twice (once in content and again), we now output:
        # Replace the target with new content that will be inserted just before the closing tag.
        return f"\n\nReplace: \n{wrap}\nWith: \n{content}\n\n"

    # Use MULTILINE so that ^ and $ match at line breaks and DOTALL so that . includes newlines.
    result = re.sub(pattern, replacer, mod_content, flags=re.MULTILINE | re.DOTALL)
    return result

# Function to Update Old Lines from HTML
def update_old_lines_from_html(old_lines, html_content):
    """
    If 'old_lines' contains the marker "[to]", this function:
    
    - Splits 'old_lines' into two parts: the content before the marker (prefix)
      and the content after the marker (suffix).
    - Searches the html_content for a substring that starts with the prefix
      and ends with the suffix.
    - Extracts the content found between these two parts.
    - Returns the new 'old_lines' constructed as: prefix + extracted content + suffix.
    
    If the marker is not found in 'old_lines' or no matching substring is found
    in the html_content, it returns 'old_lines' unchanged.
    """
    marker = "[to]"
    if marker in old_lines:
        # Split old_lines into the part before and after the marker.
        prefix, suffix = old_lines.split(marker, 1)
        # Build a regex pattern that captures any text between the prefix and suffix.
        pattern = re.escape(prefix) + r'(.*?)' + re.escape(suffix)
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            extracted_content = match.group(1)
            # Reconstruct old_lines with the extracted content between prefix and suffix.
            new_old_lines = prefix + extracted_content + suffix
            return new_old_lines
    return old_lines

# Function to Process Mod Files Using the Replacement Technique
def proc_replacement(mod_content, mod_list, mod_file_indexes, mod_file, old_delim, new_delim): 
    # Run Pre Process Content to add <e> and </e> wherever necessary
    mod_content = preprocess_content(mod_content, old_delim, new_delim)  # Insert <e> and </e> correctly
    # For old_delim 'Replace:' (the new technique), run pre_proc first.
    if old_delim == 'Replace:':
        mod_content = pre_proc(mod_content, old_delim)

    replacements = mod_content.split(old_delim)  # Split by the given delimiter
    # Define special targets that require the closing tag to appear only once.
    special_targets = {"</tw-storydata>", "</script><tw-passagedata"}
    
    for replacement in replacements:
        handle_output(f"Custom Log Before Escape: {replacement}", "custom")
        replacement = escape_html_between_tags(replacement)
        handle_output(f"Custom Log After Escape: {replacement}", "custom")
        if new_delim in replacement:
            old_lines, new_lines = replacement.split(new_delim, 1)  # Split at the first occurrence

            old_line_stripped = old_lines.strip()
            new_line_stripped = new_lines.strip()

            # If this replacement uses a special target, remove any extra trailing closing tag.
            if old_line_stripped in special_targets:
                if new_line_stripped.endswith(old_line_stripped):
                    new_line_stripped = new_line_stripped[:-len(old_line_stripped)].rstrip()

            found = False
            for item in mod_list:
                if item['old_line'] == old_line_stripped:
                    found = True
                    # If the target is special, remove the closing tag from existing content.
                    if old_line_stripped in special_targets:
                        if item['new_line'].endswith(old_line_stripped):
                            item['new_line'] = item['new_line'][:-len(old_line_stripped)].rstrip()
                        # Append new content and then re-append the closing tag.
                        item['new_line'] += "\n" + new_line_stripped + old_line_stripped
                    else:
                        item['new_line'] += f"\n{new_line_stripped}"
                    break

            if not found:
                if old_line_stripped in special_targets:
                    mod_list.append({'old_line': old_line_stripped, 'new_line': new_line_stripped + old_line_stripped})
                else:
                    mod_list.append({'old_line': old_line_stripped, 'new_line': new_line_stripped})

            # Ensure the mod_file_indexes has an entry for mod_file
            if mod_file not in mod_file_indexes:
                mod_file_indexes[mod_file] = []  # Initialize as an empty list if not present
            if old_lines not in mod_file_indexes:
                mod_file_indexes[old_lines] = []
            
            mod_file_indexes[mod_file].append(old_lines.strip())  # Append the stripped old line directly

# Function to Load and Process All Mod Files
def load_mods(mods_folder):
    mod_list = []
    mod_file_indexes = {}  # Track mod file and its replacement indices

    successful_mod_files = []  # Track successful mod files
    for root, dirs, files in os.walk(mods_folder):
        for mod_file in sorted(files, key=lambda f: f.lower()):  # Alphabetical order
            if mod_file.endswith('.mod'):
                mod_path = os.path.join(root, mod_file)
                with open(mod_path, 'r', encoding='utf-8') as mod:
                    mod_content = mod.read()
                    
                    # Process using the old technique (~~ and ~)
                    proc_replacement(mod_content, mod_list, mod_file_indexes, mod_file, '~~', '~')

                    # Then, process using the new technique (Replace: and With:)
                    proc_replacement(mod_content, mod_list, mod_file_indexes, mod_file, 'Replace:', 'With:')
                        
                successful_mod_files.append(mod_file)
    return mod_list, mod_file_indexes, successful_mod_files

# Function to Replace the Content in the HTML File
def patch_html_file(html_file, mod_list, mod_file_indexes):
    successful_mods = []
    failed_mods = []

    # Clear previous logs before starting
    clear_logs()
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("Mod patching started...\n")
    
    if not os.path.exists(html_file):
        handle_output(f"Error: HTML file '{html_file}' not found.", "log")
        input("Press Enter to exit...")
        exit(1)

    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()  

    replacements_made = 0
    replacements_failed = 0

    # Process each replacement pair
    for item in mod_list:
        old_lines = item['old_line']
        new_lines = item['new_line']

        # Update old_lines if it contains the marker "[to]"
        old_lines = update_old_lines_from_html(old_lines, html_content)

        # Create a regex pattern that allows whitespace/newlines
        old_lines_pattern = re.escape(old_lines).replace(r'\n', r'\s*')
        pattern = rf'({old_lines_pattern})'

        if re.search(pattern, html_content):
            handle_output(f"Replacing '{old_lines}' with '{new_lines}'", "log")
            html_content = re.sub(pattern, new_lines, html_content)
            replacements_made += 1
            for key, value in mod_file_indexes.items():
                if old_lines in value:
                    successful_mods.append(key)
        else:
            handle_output(f"No match found for '{old_lines}'", "log")
            handle_output(f"No match found for '{old_lines}'", "failed")
            replacements_failed += 1
            for key, value in mod_file_indexes.items():
                if old_lines in value:
                    failed_mods.append(key)

    if replacements_made == 0:
        handle_output("No matches found for any mod lines.", "log")
    else:
        handle_output(f"Total replacements made: {replacements_made}", "alllogs")
        handle_output(f"Total replacements failed: {replacements_failed}", "alllogs")
        
        successful_mods = list(set(successful_mods))
        failed_mods = list(set(failed_mods))

        handle_output("Successful Mods:", "alllogs")
        for mod in successful_mods:
            handle_output(f"{mod}", "alllogs")
        handle_output("Failed Mods:", "alllogs")
        for mod in failed_mods:
            handle_output(f"{mod}", "alllogs")

    # Write the updated HTML content back to the file
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

    handle_output("Mod patching complete.", "log")

# Function to Run the Main Logic
def main():
    try:
        if current_file_name not in ["KittyPatcher.py", "KittyPatcher.exe"]:
            distmode = True
        
        # Create Directories and Backup
        create_directories()
        create_backup()
        
        mod_list, mod_file_indexes, successful_mod_files = load_mods(mods_folder)
        patch_html_file(html_file, mod_list, mod_file_indexes)
        
        for mod_file, old_lines in mod_file_indexes.items():
            handle_output(f"{mod_file}", "alllogs")

        check_for_repeats(mod_file_indexes)
        
        handle_output(f"Mod files processed: {', '.join(successful_mod_files)}\n", "log")
        handle_output(f"Check the log file '{log_file}' for detailed patch information.", "log")
        
        handle_output("Mod patching complete.", "console")
        handle_output(f"Check the log file '{log_file}' for detailed information on what was replaced.", "console")
        
        if not current_file_name.lower().startswith("kitty"):
           open_in_browser(html_file)
            
    except Exception as e:
        handle_output(f"An error occurred: {e}", "console")
    
    finally:
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
