# initialize element list
E = ["Tc","Pm", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv"]
# prompt user for input:

d = input("Access Granted. Input message:")

# clean input

D = d.replace(" ", "")

# prompt for passphrase
C = input("Awaiting Credentials:")

#convert all text to ascii code, then convert to number in alphabet
O = [ord(char) - 96 for char in D.lower()]

#convert passphrase to seed
N = [ord(char) for char in C.lower()]
n = sum(N)

#Bug testing
#print(f"d = {d}")
#print(f"D = {D}")
#print(f"C = {C}")
#print(f"O = {O}")
#print(f"N = {N}")
#print(f"n = {n}")

#initialize final output
Out = []

# convert each char to number under 35

#variable that allows for incremental increases to same character in string
I = n + len(O)
for i in O:
   Step_One = n * len(O) + i
   #print(f"in: {i}, Step One: {Step_One}")
   #protects against incidence analasys
   Step_One_Two = Step_One * I
   I = I + 1
   #print(f"Step One.5: {Step_One_Two}")
   Step_Two = Step_One_Two % 35
   #print(f"Step Two: {Step_Two}")
   Final = E[Step_Two]
   #print(f"Final: {Final}")
   Out.append(Final)

#final output
print(f"Message sent: {Out}")
