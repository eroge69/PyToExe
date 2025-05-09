import pyautogui
import time

Idbox = (161, 306)  
Exam = (314, 306)  
Print = (158, 426)  
printcd = (317, 404) 
printerbox = (158,450)
printer17 = (158,475)
printer18 = (158,500)
Avviacd = (158,525)
closecd = (158,550)
printreferto = (158,575)
avviastampa1 = (158,600)
avviastampa2 = (158,625)
tambox = (1741,980)

CD = input("vuoi stampare i CD?: ")
Referto = input("vuoi stampare i referti?: ")
if CD == "si":
    s17 = input("la stampante 17 funziona?: ")
    s18 = input("la stampante 18 funziona?: ")
    
N = 0

while True:
  PatID = input("Inserisci il codice paziente: ") 
  
  pyautogui.moveTo(Idbox)
  time.sleep(0.5)
  pyautogui.click()
  pyautogui.typewrite(PatID)
  pyautogui.press('enter')
  time.sleep(1.5)
  
  pyautogui.moveTo(Exam)
  pyautogui.click()
  time.sleep(1.5)

  if CD == "si":
     pyautogui.moveTo(Print)
     pyautogui.click()
     time.sleep(1.5)

     pyautogui.moveTo(printcd)
     pyautogui.click()
     time.sleep(1.5)
    
     pyautogui.moveTo(printerbox)
     pyautogui.click()
     time.sleep(0.2)

     if s17 == "si" and s18 == "si":
       if N % 2 == 0:
         pyautogui.moveTo(printer17)
         pyautogui.click()
         time.sleep(0.2)
       else:
         pyautogui.moveTo(printer18)
         pyautogui.click()
         time.sleep(0.2)
     if s17 == "no" and s18 == "si":
         pyautogui.moveTo(printer18)
         pyautogui.click()
         time.sleep(0.2)
     if s17 == "si" and s18 == "no":
         pyautogui.moveTo(printer17)
         pyautogui.click()
         time.sleep(0.2)
    
     pyautogui.moveTo(Avviacd)
     pyautogui.click()
     time.sleep(1.5)

     pyautogui.moveTo(closecd)
     pyautogui.click()
     time.sleep(1.5)

  if Referto == "si":
     pyautogui.moveTo(Print)
     pyautogui.click()
     time.sleep(1.5)

     pyautogui.moveTo(printreferto)
     pyautogui.click()
     time.sleep(1.5)
    
     pyautogui.moveTo(avviastampa1)
     pyautogui.click()
     time.sleep(0.2)

     pyautogui.moveTo(avviastampa2)
     pyautogui.click()
     time.sleep(0.2)

  pyautogui.moveTo(Idbox)
  pyautogui.click()
  pyautogui.press('delete')

  N = N + 1
  print(f"Pazienti fatti: {N}")
  
  pyautogui.moveTo(tambox)
  pyautogui.click()