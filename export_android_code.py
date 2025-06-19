import os

# ===== CONFIGURATION SECTION =====
# 👉 Yahan apne project folder ka path likho
project_root = "E:\PROJECTS\android studio\Apps\MyMusicAppCompose"  # <-- Replace with your real path
output_file = "MyMusicApp_CodeExport.md"  # Output markdown file

# 👉 Yeh extensions wale files export honge
include_extensions = [".kt", ".xml"]

# ===== FUNCTION: Collect all code files from your app =====
def collect_code_files(root_path):
    code_files = []
    for root, _, files in os.walk(root_path):
        for file in files:
            if any(file.endswith(ext) for ext in include_extensions):
                full_path = os.path.join(root, file)
                code_files.append(full_path)
    return code_files

# ===== FUNCTION: Save all code into one .md file =====
def export_to_markdown(code_files, output_path):
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write("# 📦 MyMusicApp Code Export\n")
        out_file.write("This file contains all Kotlin and XML source files.\n\n")

        for file_path in code_files:
            relative_path = os.path.relpath(file_path, project_root)
            out_file.write(f"\n---\n\n## `{relative_path}`\n\n")
            out_file.write("```kotlin\n" if file_path.endswith(".kt") else "```xml\n")

            # Code ko read karke file mein likhna
            with open(file_path, "r", encoding="utf-8", errors="ignore") as code_file:
                out_file.write(code_file.read())

            out_file.write("\n```\n")  # End of code block

    print(f"\n✅ Export complete! File saved at: {output_path}")

# ===== MAIN SCRIPT START =====
if __name__ == "__main__":
    print("📁 Scanning your project files...")
    code_files = collect_code_files(project_root)
    export_to_markdown(code_files, output_file)
