#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ul307
#
# Created:     09.04.2024
# Copyright:   (c) ul307 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import time
import shutil

start_t=time.time()
for i in range(1000):
    with open (f"textak_{i}.txt", "w") as f:
       f.write(str(i))
end_t=time.time()

print(f"tvorba: {end_t-start_t}")

obsah=os.listdir(".")
obsah.remove("module1.py")

start_m=time.time()
for i in obsah:
    if i.endswith(".txt"):
        os.remove(i)
end_m=time.time()
print(f"mazani:{end_m-start_m}")
"""
shutil.copy("module1.py","Plocha.py" )
"""