import os
import re

# Path to the folder containing HTML files
folder_path = 'C:\\gemagifinhsh'  # Replace with the actual path, e.g., 'C:\\gemagifinhsh'
output_file = 'izvuceni_linkovi.txt'

# Complete regex pattern to capture TITLE and HREF
pattern = re.compile(r'<TITLE>(.*?)</TITLE>.*?HREF="(.*?)"><font')

# Open the output file
with open(output_file, 'w', encoding='utf-8') as output:
    # List all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.html'):
            file_path = os.path.join(folder_path, filename)

            # Open HTML file and read content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # Find all matches for the defined pattern
                matches = re.findall(pattern, content)

                # Write matches to the output file
                for title, href in matches:
                    output.write(f'<TITLE>{title}</TITLE>HREF="{href}"><font\n')

print(f'Podaci su izvučeni i pohranjeni u {output_file}.')