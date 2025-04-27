import random

#Questrions & Defining variables
results = []
dices = input("Dices per throw: ")
die_type = input("Faces per die: ")
throw_times = input("Throws: ")

#Check if variables won't cause any issues
if dices.isnumeric() == False:
    print("Error: Please, insert a valid number in Dices per throw.")
    exit()

if die_type.isnumeric() == False:
    print("Error: Please, insert a valid number in Faces per die.")
    exit()

if throw_times.isnumeric() == False:
    print("Error: Please, insert a valid number in Throws.")
    exit()

#Game
def throwing():
    for i in range(int(dices)):
        results.append(random.randint(1,int(die_type)))
     

#Show results of 1 dice for any throw_times_input
for i in range(int(throw_times)):
    throwing()
    print("The results are " + ', '.join(map(str,results[:-1])) + " and " + str(results[-1]) + ".")
    results.clear()
    
    