import os
import subprocess
import threading
import time
import customtkinter as ctk
from tkinter import filedialog
import webbrowser

root = ctk.CTk()
root.title("Analysis Tool")
root.attributes('-fullscreen', True)

root.configure(bg="#F4F6FA")
def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

root.bind("<Escape>", exit_fullscreen)

heading_card = ctk.CTkFrame(root, fg_color="#234E70", corner_radius=20)
heading_card.pack(pady=20, padx=20, fill='x')

heading_label = ctk.CTkLabel(heading_card, text="Detailed Analysis",
                             font=("Arial", 30, "bold"), text_color="white")
heading_label.pack(pady=20)

subheading_label = ctk.CTkLabel(root, text="Upload Input & Output folders to start Analysis",
                                font=("Arial", 16, "bold"), text_color="#234E70")
subheading_label.pack(pady=5)


def browse_folder(entry_field):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_field.delete(0, "end")
        entry_field.insert(0, folder_selected)


tool_card = ctk.CTkFrame(root, fg_color="#D6E4F0", corner_radius=15)
tool_card.pack(pady=15, padx=30, fill='x')

tool_label = ctk.CTkLabel(tool_card, text="Select Reporting Tool:", font=("Arial", 14, "bold"))
tool_label.pack(side="left", padx=15, pady=12)

tool_options = ["Tableau", "Looker", "SSRS", "Power BI","Microstrategy"]
tool_var = ctk.StringVar(value="Power BI")

tool_dropdown = ctk.CTkOptionMenu(tool_card, variable=tool_var, values=tool_options, font=("Arial", 14))
tool_dropdown.pack(side="left", padx=15, pady=12, expand=True, fill='x')


tool_info_label = ctk.CTkLabel(root, text="Expected File: .json (Power BI)", font=("Arial", 12), text_color="#888888")
tool_info_label.pack()

def update_tool_info(*args):
    tool = tool_var.get().lower()
    tips = {
        "ssrs": "Expected File: .rdl",
        "tableau": "Expected Files: .twb or .twbx",
        "looker": "Expected File: .lkml (LookML)",
        "power bi": "Expected File: .json (PBI Model)",
        "Microstrategy": "Expected File: .xlsx "
    }
    tool_info_label.configure(text=tips[tool])

tool_var.trace_add("write", update_tool_info)


input_card = ctk.CTkFrame(root, fg_color="#D6E4F0", corner_radius=15)
input_card.pack(pady=15, padx=30, fill='x')

input_entry = ctk.CTkEntry(input_card, font=("Arial", 14), placeholder_text="G:\\Shared drives\\AUTOMATION\\INPUT_FILES")
input_entry.pack(side="left", padx=15, pady=12, expand=True, fill='x')

input_button = ctk.CTkButton(input_card, text="Browse", command=lambda: browse_folder(input_entry),
                             width=120, fg_color="#234E70", hover_color="#163D5A",
                             font=("Arial", 14, "bold"), corner_radius=12)
input_button.pack(side="right", padx=15)

output_card = ctk.CTkFrame(root, fg_color="#D6E4F0", corner_radius=15)
output_card.pack(pady=15, padx=30, fill='x')

output_entry = ctk.CTkEntry(output_card, font=("Arial", 14), placeholder_text="G:\\Shared drives\\AUTOMATION\\OUTPUT_FILES")
output_entry.pack(side="left", padx=15, pady=12, expand=True, fill='x')

output_button = ctk.CTkButton(output_card, text="Browse", command=lambda: browse_folder(output_entry),
                              width=120, fg_color="#234E70", hover_color="#163D5A",
                              font=("Arial", 14, "bold"), corner_radius=12)
output_button.pack(side="right", padx=15)

result_card = ctk.CTkFrame(root, fg_color="#D6E4F0", corner_radius=15)
result_card.pack(pady=15, padx=30, fill='x')
result_card.grid_columnconfigure(0, weight=1)

global_result_msg = ctk.CTkLabel(result_card, text="", font=("Arial", 16, "bold"), text_color="#1A3C5E", wraplength=650, justify="center")
global_result_msg.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

close_btn = ctk.CTkButton(result_card, text="❌", width=20, height=20,
                          fg_color="transparent", hover_color="#e0e0e0", text_color="red",
                          font=("Arial", 14), command=lambda: close_message())
close_btn.grid(row=0, column=1, sticky="ne", padx=10, pady=5)
close_btn.grid_remove() 


def close_message():
    global_result_msg.configure(text="")
    close_btn.grid_remove()
    
    
    for widget in result_card.winfo_children():
        if isinstance(widget, ctk.CTkLabel) and widget != global_result_msg:
            widget.grid_remove()
            widget.destroy()

def show_result_message(message, color="black", link_path=None, highlight_msg=None, highlight_color="green"):
    close_message()
    global_result_msg.configure(text=message, text_color=color)
    close_btn.grid()

    if highlight_msg:
        highlight_label = ctk.CTkLabel(result_card, text=highlight_msg, text_color=highlight_color,
                                       font=("Arial", 16, "bold"))
        highlight_label.grid(row=2, column=0, columnspan=2, pady=(5, 0), padx=10)

    if link_path:
        link_label = ctk.CTkLabel(result_card, text="📄 View Analysis Report", text_color="blue",
                                  font=("Arial", 15, "underline"), cursor="hand2")
        link_label.grid(row=3, column=0, columnspan=2, pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open(f'file:///{link_path}'))



# Generate HTML Report
def generate_html_report(file_paths, output_html_path):
    html_content = "<html><head><title>Generated Reports</title></head><body>"
    html_content += "<h2>Generated Excel Reports</h2><table border='1' style='border-collapse: collapse;'>"
    html_content += "<tr><th>File Name</th><th>Link</th></tr>"
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_url = f"file:///{file_path.replace(os.sep, '/')}"
        html_content += f"<tr><td>{file_name}</td><td><a href='{file_url}'>{file_url}</a></td></tr>"
    html_content += "</table></body></html>"
    with open(output_html_path, 'w') as f:
        f.write(html_content)

# Run selected script
def run_analysis(script, input_folder, output_folder, tool_name,message):
    try:
        start_time = time.time()

        result = subprocess.run(["python", script, input_folder, output_folder],
                                capture_output=True, text=True, check=True)

        end_time = time.time()
        elapsed_time = end_time - start_time
        elapsed_msg = f"Time taken: {elapsed_time:.2f} seconds"

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        file_paths = [os.path.join(output_folder, f)
                        for f in os.listdir(output_folder)
                        if f.lower().endswith(".xlsx")]
        html_path = os.path.join(output_folder, "report_links.html")
        generate_html_report(file_paths, html_path)

        show_result_message(
            message, "black", link_path=html_path,
            highlight_msg="Analysis Completed for Valid files", highlight_color="green"
        )

        # Show time taken in small font
        time_label = ctk.CTkLabel(result_card, text=elapsed_msg, text_color="#555555",
                                    font=("Arial", 12))
        time_label.grid(row=4, column=0, columnspan=2, pady=(5, 10))

    except subprocess.CalledProcessError as e:
            print(e.stderr)
            show_result_message(f"Error: {e.stderr}", "red")


    

def start_analysis():
    close_message()
    input_folder = input_entry.get().strip()
    output_f = output_entry.get().strip()
    output_folder= os.path.join(output_f,"Report wise Analysis")
    os.makedirs(output_folder, exist_ok=True)

    if not input_folder or not output_f:
        show_result_message("Please select both Input & Output folders.", "red")
        return

    if not os.path.isdir(input_folder):
        show_result_message("Input folder does not exist. Please select a valid path.", "red")
        return

    if not os.path.isdir(output_f):
        show_result_message("Output folder does not exist. Please select a valid path.", "red")
        return
    

    selected_tool = tool_var.get().lower()

    expected_extensions = {
        "ssrs": [".rdl"],
        "power bi": [".json"],
        "tableau": [".twb", ".twbx"],
        "looker": [".lkml"]
        
    }

    analysis_scripts = {
        "ssrs": r"G:\Shared drives\CODE\LATEST_PYTHON_CODE\SSRS\SSRS automation.py",
        "power bi": r"G:\Shared drives\CODE\LATEST_PYTHON_CODE\POWER_BI\Analysis.py",
        "tableau": r"G:\Shared drives\CODE\LATEST_PYTHON_CODE\TABLEAU\Tableau Data Extract.py",
        "looker": r"G:\Shared drives\CODE\LATEST_PYTHON_CODE\Looker\lookml_extraction_optimised_analysis.py",
        "Microstrategy" : r"G:\Shared drives\code\LATEST_PYTHON_CODE\Microstrategy\mstr_summary.py"
    }

    valid_exts = expected_extensions[selected_tool]
    message=""
    if selected_tool == "looker":
        valid_files, invalid_files = [], []
        for root_dir, dirs, files in os.walk(input_folder):
            for file in files:
                full_path = os.path.join(root_dir, file)
                if ".lkml" in file.lower() or ".gitkeep" in file.lower():
                    valid_files.append(full_path)
               
        if not valid_files:
            show_result_message(" No valid `.lkml` files found!", "red")
            return
        
     
    else:
        input_files = os.listdir(input_folder)
        valid_files = [f for f in input_files if os.path.splitext(f)[1].lower() in valid_exts]
 
        if not valid_files:
            show_result_message(f"No valid {', '.join(valid_exts)} files found for {tool_var.get()}!", "red")
            return
      
            
    processing_msg = f"🔄 Processing {len(valid_files)} valid file(s)..."
   
    show_result_message(processing_msg, "blue")

    
    threading.Thread(
        target=run_analysis,
        args=(analysis_scripts[selected_tool], input_folder, output_folder, tool_var.get(), message),
        daemon=True
    ).start()        

    
button_card = ctk.CTkFrame(root, fg_color="#E3ECF3", corner_radius=15)
button_card.pack(pady=25, padx=30, fill='x')

analyze_button = ctk.CTkButton(button_card, text="Generate Detailed Analysis", command=start_analysis,
                               fg_color=("#AEC6CF", "#87CEEB"), hover_color="#5A9BD4",
                               text_color="black", font=("Arial", 25, "bold"),
                               height=60, corner_radius=15)
analyze_button.pack(pady=20, padx=20, fill='x')
def open_user_guide():
    webbrowser.open_new(r"G:\Shared drives\code\LATEST_PYTHON_CODE\GUI\Formatted_Report_Automation_Tool_User_Guide.pdf")  # Replace with your actual guide URL or path

user_guide_link = ctk.CTkLabel(root, text="📘 User Guide", text_color="#1A73E8", cursor="hand2",
                               font=("Segoe UI", 20, "underline"), bg_color="transparent")
user_guide_link.place(relx=0.99, rely=0.98, anchor="se")  
user_guide_link.bind("<Button-1>", lambda e: open_user_guide())

root.mainloop()
