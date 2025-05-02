import pyodbc
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import csv
import os

#Global
test_string = ""

def runquery():
    global test_string
    # Connection setup using Windows Authentication
    server = 'C014046\ECADPRO2014'  # e.g. 'localhost\\SQLEXPRESS' or IP address
    database = 'ECADMASTER'

    label_text = query_text.get("1.0", tk.END).strip()

    #print(label_text)

    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"  # Windows Authentication
    )

    try:
        # Connect to database
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # SQL query
        #label_ = "SELECT * FROM ECADMASTER.DBO.RORDINE WHERE NUMERO = 12755"
        cursor.execute(label_text)
        print(label_text)

        # Fetch column names
        columns = [column[0] for column in cursor.description]

        # Fetch all data
        rows = cursor.fetchall()

        base_filename = "query_results"
        extension = ".csv"
        filename = base_filename + extension
        counter = 1
        folder_path = test_string

        if folder_path:
            # Loop to find a non-existing filename
            while os.path.exists(os.path.join(folder_path, filename)):
                filename = f"{base_filename}({counter}){extension}"
                counter += 1
            full_filename = os.path.join(folder_path, filename)
            # Write to the new unique CSV file
            with open(full_filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')  # Use semicolon here for Excel
                writer.writerow(columns)
                writer.writerows(rows)

            messagebox.showinfo("Success", f"✅ Exported to {full_filename} successfully!")
        else:
        # Loop to find a non-existing filename
            while os.path.exists(filename):
                filename = f"{base_filename}({counter}){extension}"
                counter += 1

            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')  # Use semicolon here for Excel
                writer.writerow(columns)
                writer.writerows(rows)

            messagebox.showinfo("Success", f"✅ Exported to {filename} successfully!")


        button.config(bg="green")

    except Exception as e:
        messagebox.showerror("Error", f"❌ Error: {e}")
        # Run Query button
        button.config(bg="red")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def choose_save_location():
    global test_string
    folder_path = filedialog.askdirectory(
        title="Escolher Pasta para guardar os ficheiros"
    )
    if folder_path:
        test_string = folder_path
        print("Escolher pasta", test_string)

# Create main UI window
root = tk.Tk()
root.title("MOB SQL Query Runner")
root.iconbitmap("mobcozinhas_logo.ico")
root.geometry("600x350")

# Filepath button

btn = tk.Button(root, text="Choose Folder", command=choose_save_location,)
btn.place(relx=0.1, rely = 0.1, anchor="center")
btn.pack(padx = 20, pady=20)
#btn.pack()

# Query input area
tk.Label(root, text="Inserir Query SQL:")
query_text = scrolledtext.ScrolledText(root, width=70, height=10)
query_text.pack(padx=10,pady=20)
#query_text.pack()

# Run Query button
button = tk.Button(
    root, 
    text="Executar e Exportar CSV", 
    command=runquery, 
    bg="black", 
    fg="white", 
    height= 1,
    width= 20
)
button.pack(pady=5)

# Exit Button
tk.Button(
    root, 
    text="Sair", 
    command=root.destroy, 
    bg="red", 
    fg="white",
    height= 1,
    width= 20
).pack()

# Run the UI loop
root.mainloop()

def main():
    #runquery()
    print("Executing Main!")


# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()



