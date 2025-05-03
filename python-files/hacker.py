import random
import time
from termcolor import colored

class Column:
    def __init__(self):
        self.chars = 1
        self.mode = None
    @staticmethod
    def generate_char():
        alph = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        other = " !?.,-:;_#+*/()[]{}§$%&=ß\\@><^°|~\"\'"
        memory = alph + other
        return memory[random.randint(0, len(memory)-1)]
    def generate_chinese(self):
        return self.generate_char()
    def next(self):
        self.update()
        match self.mode:
            case "empty":
                return " "
            case "character":
                return self.generate_char()
            case "chinese":
                return self.generate_chinese()
    def update(self):
        self.chars -= 1
        if self.chars > 0:
            return
        self.chars = random.randint(MIN_LEN, MAX_LEN)
        number = random.randint( 0, sum( PROBS.values() ) )
        if number < PROBS["empty"]:
            self.mode = "empty"
        elif (number - PROBS["empty"]) < PROBS["character"]:
            self.mode = "character"
        else:
            self.mode = "chinese"

#Set here the parameters for your run (the comments on the right explain the params):
COLS = 180    #amount of shown columns
SPEED = 60    #speed in lines per second (lps)
MIN_LEN = 10  #min. length of the columns
MAX_LEN = 50  #max. length of the columns
PROBS = {     #sets, how many of these col-types will be shown relatively to the others
    "empty" : 6,
    "character" : 0,
    "chinese" : 1
}

#The start of the program
cols = [Column() for i in range(COLS)]
while True:
    string = ""
    for col in cols:
        string += col.next()
    print(colored(string,"light_green"))
    time.sleep(1/SPEED)

#The program does not have an algorithm to create random chinese letters yet, and it's not yet in green
#But it's already really cool