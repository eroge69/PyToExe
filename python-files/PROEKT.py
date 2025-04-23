from tkinter import *

def Scankey(event):
	val = event.widget.get()
	print(val)
	if val == '':
		data = list
	else:
		data = []
		for item in list:
			if val.lower() in item.lower():
				data.append(item)
	Update(data)

def Update(data):
	listbox.delete(0, 'end')
	# put new data
	for item in data:
		listbox.insert('end', item)
class Table:
    # Initialize a constructor
    def __init__(self, gui):

        # An approach for creating the table
        for i in range(total_rows):
            for j in range(total_columns):
                print(i)
                if i == 0:
                    self.entry = Entry(
                        gui,
                        width=20,
                        bg="LightSteelBlue",
                        fg="Black",
                        font=("Arial", 16, "bold"),
                    )
                else:
                    self.entry = Entry(gui, width=20, fg="blue", font=("Arial", 16, ""))

                self.entry.grid(row=i, column=j)
                self.entry.insert(END, employee_list[i][j])
list = employee_list = [
    ("ID", "Name", "City", "Age"),
    (1, "Gorge", "California", 30),
    (2, "Maria", "New York", 19),
    (3, "Albert", "Berlin", 22),
    (4, "Harry", "Chicago", 19),
    (5, "Vanessa", "Boston", 31),
    (6, "Ali", "Karachi", 30),]
total_rows = len(employee_list)
total_columns = len(employee_list[0])
ws = Tk()
entry = Entry(ws)
entry.pack()
entry.bind('<KeyRelease>', Scankey)
listbox = Listbox(ws)
listbox.pack()
Update(list)

ws.mainloop()