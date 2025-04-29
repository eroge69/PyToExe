import tkinter as tk
from tkinter import simpledialog, messagebox
import random

class AdmissionPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("ADMISSION PORTAL")
        self.root.geometry("600x600")
        self.root.configure(bg="#f0f8ff")


        self.create_main_page()

    def create_main_page(self):
        frame = tk.Frame(self.root, bg="Red")
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        welcome_label = tk.Label(frame, text="ADMISSION PORTAL", font=("Monaco", 70, "bold"), bg="Alice Blue")
        welcome_label.pack(pady=40)

        next_page_button = self.add_button(frame, "NEXT PAGE", self.next_page)
        next_page_button.pack(pady=40)

        exit_button = self.add_button(frame, "EXIT", frame.quit)
        exit_button.pack(pady=40)

    def next_page(self):
        if messagebox.askyesno("Confirmation", "Do you want to go to the next page ? "):
            self.get_user_info()
            
        else:
            messagebox.showinfo("Info", "Staying on page")
            return self.next_page()                

    def create_admission_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="Red")
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        welcome_label = tk.Label(frame, text="WELCOME TO THE ADMISSION PORTAL", font=("Arial", 20, "bold"), bg="Alice Blue")
        welcome_label.pack(pady=30)

        handle_choice_1_button = self.add_button(frame, "1. Information concerning yourself", self.handle_choice_1)
        handle_choice_1_button.pack(pady=30)

        handle_choice_2_button = self.add_button(frame, "2. Subject scores in WAEC", self.handle_choice_2)
        handle_choice_2_button.pack(pady=30)

        handle_choice_3_button = self.add_button(frame, "3. Deciding admission through WAEC results", self.handle_choice_3)
        handle_choice_3_button.pack(pady=30)

        return_button = self.add_button(frame, "4. Return", self.Return)
        return_button.pack(pady=30)

        exit_button = self.add_button(frame, "5. Exit", self.Exit)
        exit_button.pack(pady=30)

        # Name and Gender input using tkinter dialog
        

    def get_user_info(self):
        name = simpledialog.askstring("Input", "What is your name ? ")
        if len(name) > 10:
            messagebox.showerror("Error", "Name too long!")
            return self.get_user_info
        elif len(name) < 3:
            messagebox.showerror('Error', 'Name too short.')
            return self.get_user_info   
        elif len(name) < 10:
            messagebox.showinfo("Info", f"Ok {name}.")
        elif not name:
            messagebox.showerror("Error", "Pls input a name")
            return self.get_user_info()    
        else:    
            return self.get_user_info()

        gender = simpledialog.askstring("Input", "Indicate your gender [male/female] :")
        if not gender:
            messagebox.showerror("Error", "Gender is required")
            return self.get_user_info()            
        elif gender.upper() == "MALE" or gender.upper() == "SIR":
            messagebox.showinfo("Info", "Ok Sir")
        elif gender.upper() == "FEMALE" or gender.upper() == "MA":
            messagebox.showinfo("Info", "Ok Ma")
        else:
            messagebox.showerror("Error", "Please indicate if you're a male or a female!")
            return self.get_user_info()
            

        age = simpledialog.askinteger("Age", "How old are you ? ")
        if age < 15:
            messagebox.showerror("Error", "Sorry for canditates above 15")
            return 
        else:
            messagebox.showinfo("Welcome", f"Nice to meet you {name}.")
            self.create_admission_page()
            self.gender = gender
            self.name = name
        
    def add_button(self, frame, text, command):
        return tk.Button(frame, text=text, command=command, font=("Arial", 12), bg="#4682b4", fg="white", activebackground="#5f9ea0", activeforeground="white")

    def handle_choice_1(self):
        email_account = simpledialog.askstring("Email", f"Input your email account, {self.name}?")
        if email_account:
            messagebox.showinfo("Info", f"A code will be sent to {email_account} shortly.")
            messagebox.showinfo("Code", "Code = 102020")
            code_input = simpledialog.askstring("Code Input", "Enter your code:")
            if code_input == "102020":
                messagebox.showinfo("Success", f"Thank you {self.name}.")
                if messagebox.askyesno("Next", "Do you want to proceed to the next page ? "):
                    self.handle_choice_2()
                else:
                    return    
            else:
                messagebox.showerror("Error", "Invalid Entry")
        elif not email_account:
            messagebox.showwarning("Warning", "Pls input an email account")
            return self.handle_choice_1()        

    def handle_choice_2(self):
        messagebox.showinfo("Info", """These are the following available departments:
1. Science
2. Art
3. Commercial """)
        department = simpledialog.askstring("Department", f"Which department do you belong to, {self.name}?")
        if department.upper() == "science" or "1" or "art" or "2" or "commercial" or "3":
            messagebox.showinfo("Info", f"OK {self.name}.")
            messagebox.showinfo("Courses", """Courses available include:
1. Medicine - Medicine and Other medicine related courses
2. Engineering - Engineering and Engineering related courses
3. Accounting - Accounting and commerce related courses
4. Law - Law and Art related courses. """)
        elif not department:
            messagebox.showerror("Error", "Pls input a department! ")
            return self.handle_choice_2
        elif department.lower() != "science" or "art" or "commercial" or "1" or "2" or "3":
            messagebox.showerror("Error", "Not part of the options, pls select from the options! ")
            return self.handle_choice_2
        else:
            messagebox.showerror("Error", "Invalid Entry!")
            return   
        course_to_study = simpledialog.askstring("Course", f"Which course do you want to study, {self.name}?" )
        messagebox.showinfo("Info", "OK " + self.name)
        self.calculate_total_score(course_to_study)

    def calculate_total_score(self, course_to_study):
        if course_to_study.lower() == 'medicine' or course_to_study == '1':
            english_score = float(simpledialog.askstring("Score", "Enter your English score in JAMB: "))
            biology_score = float(simpledialog.askstring("Score", "Enter your Biology score in JAMB: "))
            chemistry_score = float(simpledialog.askstring("Score", "Enter your Chemistry score in JAMB: "))
            physics_score = float(simpledialog.askstring("Score", "Enter your Physics score in JAMB: "))
            total_score = english_score + biology_score + chemistry_score + physics_score
            messagebox.showinfo("Total Score", f"Total score: {total_score}")
    

        elif course_to_study.lower() == 'engineering' or course_to_study == '2':
            maths_score = float(simpledialog.askstring("Score", "Enter your Maths score in JAMB:"))
            english_score = float(simpledialog.askstring("Score", "Enter your English score in JAMB:"))
            chemistry_score = float(simpledialog.askstring("Score", "Enter your Chemistry score in JAMB:"))
            physics_score = float(simpledialog.askstring("Score", "Enter your Physics score in JAMB:"))
            total_score = maths_score + english_score + chemistry_score + physics_score
            messagebox.showinfo("Total Score", f"Total score: {total_score}")

            
        elif course_to_study.lower() == 'accounting' or course_to_study == '3':
            maths_score = float(simpledialog.askstring("Score", "Enter your Maths score in JAMB:"))
            english_score = float(simpledialog.askstring("Score", "Enter your English score in JAMB:"))
            account_score = float(simpledialog.askstring("Score", "Enter your Account score in JAMB:"))
            commerce_score = float(simpledialog.askstring("Score", "Enter your Commerce score in JAMB:"))
            total_score = maths_score + english_score + account_score + commerce_score
            messagebox.showinfo("Total Score", f"Total score: {total_score}")


        elif course_to_study.lower() == 'law' or course_to_study == '4':
            english_score = float(simpledialog.askstring("Score", "Enter your English score in JAMB:"))
            government_score = float(simpledialog.askstring("Score", "Enter your Government score in JAMB:"))
            literature_score = float(simpledialog.askstring("Score", "Enter your Literature score in JAMB:"))
            crs_score = float(simpledialog.askstring("Score", "Enter your CRS score in JAMB:"))
            total_score = english_score + government_score + literature_score + crs_score
            messagebox.showinfo("Total Score", f"Total score: {total_score}")
                        
        else:
            messagebox.showerror("Error", "Invalid Input!")
            return    
 
    def handle_choice_3(self):
        messagebox.showinfo("Info", """Courses available include:
1. Medicine - Medicine and Other medicine related courses
2. Engineering - Engineering and Engineering related courses
3. Accounting - Accounting and commerce related courses
4. Law - Law and Art related courses. """)
        course_to_study = simpledialog.askstring("Course", f"Which course do you want to study, {self.name}?")
        self.confirm_admission(course_to_study)

    def confirm_admission(self, course_to_study):
        score_thresholds = {
            'medicine': 250,
            'engineering': 225,
            'accounting': 205,
            'law': 245
        }

        threshold = score_thresholds.get(course_to_study.lower(), None)
        if threshold:
            score = simpledialog.askstring("Score", f"What was your total score in JAMB ? ")
            confirm_score = simpledialog.askstring("Confirmation", f"Enter your JAMB score again for confirmation:")
            if int(score) != int(confirm_score):
                messagebox.showerror("Error", "Not the same value as inputed above! Pls check your info very well. ")
                return self.handle_choice_3()
            elif int(confirm_score) >= threshold:
                messagebox.showinfo("Admission", f"CONGRATULATIONS ON YOUR ADMISSION, {self.name}")
            else:
                messagebox.showerror("Admission", "NO ADMISSION, SORRY")
                return
    
    def Return(self):
        self.create_main_page2()

    def create_main_page2(self):
        for widget in self.root.winfo_children():
            widget.destroy()
                    
        frame = tk.Frame(self.root, bg="Red")
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        welcome_label = tk.Label(frame, text="ADMISSION PORTAL", font=("Arial", 70, "bold"), bg="Alice Blue")
        welcome_label.pack(pady=40)

        next_page_button = self.add_button(frame, "NEXT PAGE", self.next_page)
        next_page_button.pack(pady=40)

        exit_button = self.add_button(frame, "EXIT", self.Exit)
        exit_button.pack(pady=40)

    def Exit(self):
        if messagebox.askyesno("Exit", "Do you want to exit ? "):
            self.root.destroy()
        else:
            messagebox.showinfo("Exit", "Ok")

            
def main():
    root = tk.Tk()
    app = AdmissionPortal(root) 
    root.mainloop()

if __name__ == "__main__":
    main()
