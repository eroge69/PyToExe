import os
import random

fajlnev = "a.txt"
for a in range(50):
    fajlnev += ".txt"
    fajlkezelesx = open(fajlnev, "x", encoding="utf-8")
    fajlkezelesx.close()
    fajlkezelesw = open(fajlnev, "wb")
    fajlkezelesw.seek(1073741824 - 1)
    fajlkezelesw.write(b"\0")
    fajlkezelesw.close()
    os.stat(fajlnev).st_size



