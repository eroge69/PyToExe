import  time
import  os
import  random
os.system('cls')

os.system('cls')
time.sleep(2)
print ("BIOS VERSION 1.52.456SE BY SUPER EGGMAN")
print ("Copyright (R) 2024-2025")
time.sleep(2)
print("")
print("Main Processor : Intel(R) Pentium(TM) @ 1.252GHz")
print("<CPUID:0456 Patch ID:5252>")
print("Memory Testing : 2096052K OK")
time.sleep(2)
print("")
rom1 = "262144KB"
print("IDE Channel 1 Master : HOSOS")
print("IDE Channel 1 Master Space : " + rom1)
time.sleep(2)
ram1 = "8192KB"
print("RAM:" + ram1)
time.sleep(2)
print("\033[0;37;44m")
os.system('cls')
time.sleep(2)
print("")
print("")
print("")
print("")
print("")
print("                          ╔═════════════════════╗")
time.sleep(0.5)
print("                          ║ ║ ║ ╔═╗ ╔══ ╔═╗ ╔══ ║")
time.sleep(0.5)
print("                          ║ ║═║ ║ ║ ╚═╗ ║ ║ ╚═╗ ║")
time.sleep(0.5)
print("                          ║ ║ ║ ╚═╝ ══╝ ╚═╝ ══╝ ║")
time.sleep(0.5)
print("                          ╚═════════════════════╝")
time.sleep(0.5)
print("                                Loading...")

time.sleep(5)
os.system('cls')
time.sleep(1)
print("╔═════════════════════╗")
print("║ ║ ║ ╔═╗ ╔══ ╔═╗ ╔══ ║")
print("║ ║═║ ║ ║ ╚═╗ ║ ║ ╚═╗ ║")
print("║ ║ ║ ╚═╝ ══╝ ╚═╝ ══╝ ║")
print("╚═════════════════════╝")
print("     version 0.5")
print("commands:")
print("systeminfo:информация о HOSOS")
print("calc:калькулятор")
print("HOSOS:???")
print
while True:
	command1 = input("> ")
	if command1 == "systeminfo":
		print("HOSOSv0.5")
		print("Beta version")
	if command1 == "calc":
		calc1 = float (input("Введите 1-ое число "))
		calc2 = float (input("Введите 2-ое число "))
		calc3 = input("Что хотите сделать(+,-,/,*): ")
		if calc3 == "+":
			answer1 = (calc1 + calc2)
			print(str(answer1))
			print("Решено")
		if calc3 == "-":
			answer1 = (calc1 - calc2)
			print(str(answer1))
			print("Решено")
		if calc3 == "/":
			answer1 = (calc1 / calc2)
			print(str(answer1))
			print("Решено")
		if calc3 == "*":
			answer1 = (calc1 * calc2)
			print(str(answer1))
			print("Решено")
	if command1 == "games":
		print ("Snake")
	if command1 == "HOSOS":
		os.system('cls')
		print("\033[0;34;47m             HOSOS ")
		print("")
		print("\033[0;37;44mПоздравляю ты нашел ПОСХАЛКО!!!!")



