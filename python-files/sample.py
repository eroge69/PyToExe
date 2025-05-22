import itertools
import os

x = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","`","~","!","@","#","$","₹","%","^","&","*","(",")","+","=","<",">",",",".","/","?",";",":",'"',"'", "{","[","}","]","|","\\"]

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, 'pass.txt')

def generate_combinations(length):
    with open(output_file, 'a', encoding='utf-8') as f:
        for combination in itertools.product(x, repeat=length):
            f.write(''.join(combination) + '\n')

for length in range(6, 21):
    generate_combinations(length)
