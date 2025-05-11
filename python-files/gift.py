import os
import threading
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import sounddevice as sd
import soundfile as sf
from time import sleep
from PIL import Image
from random import random
from math import floor
from PIL import Image
from playsound import playsound,PlaysoundException

class colors:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BRIGHT_BG_BLACK = '\033[100m'
    BRIGHT_BG_RED = '\033[101m'
    BRIGHT_BG_GREEN = '\033[102m'
    BRIGHT_BG_YELLOW = '\033[103m'
    BRIGHT_BG_BLUE = '\033[104m'
    BRIGHT_BG_MAGENTA = '\033[105m'
    BRIGHT_BG_CYAN = '\033[106m'
    BRIGHT_BG_WHITE = '\033[107m'

def image_to_ascii(image_path, width=80, chars=' .:-=+*#%@'):
    try:
        img = Image.open(image_path)
        original_width, original_height = img.size
        aspect_ratio = original_height / original_width
        height = int(width * aspect_ratio * 0.5)
        img = img.resize((width, height))
        pixels = list(img.getdata())
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
        return None

    char_len = len(chars)
    colored_ascii_image = []

    for i in range(height):
        row = ""
        for j in range(width):
            pixel_index = i * width + j
            if 0 <= pixel_index < len(pixels):
                r, g, b = pixels[pixel_index]
                brightness = (r + g + b) // 3  # Simple average for brightness
                index = int((brightness / 255) * (char_len - 1))
                char = chars[index]
                # ANSI escape code for RGB color (approximate)
                ansi_color = f"\033[38;2;{r};{g};{b}m"
                reset_color = "\033[0m"
                row += ansi_color + char + reset_color
        colored_ascii_image.append(row)

    return colored_ascii_image

def main_script():
    mom = image_to_ascii("C:\\Users\\bsthi\\Downloads\\undertale\\mom.jpg")
    outsider = image_to_ascii("C:\\Users\\bsthi\\Downloads\\undertale\\outsider.jpg")
    alltogether = image_to_ascii("C:\\Users\\bsthi\\Downloads\\undertale\\alltogether.jpg")
    print(f"{colors.CYAN}Hey mom, here's my gift to you through this code")
    for line in mom:
        print(line)
        sleep(0.3)
    print(f"{colors.YELLOW}Through the power of the INTERNET, I have these placed here for you{colors.RED}")
    flower("rose")
    flower("tulip")
    flower("clover")
    flower("flowey")
    print(f"{colors.GREEN}Then we have you out in the wild")
    for line in outsider:
        print(line)
        sleep(0.3)
    print(f"{colors.BRIGHT_RED}And us all together{colors.RESET}")
    for line in alltogether:
        print(line)
        sleep(0.3)


def play_audio_threaded(file_path):
    audio_thread = threading.Thread(target=play_audio, args=(file_path,))
    audio_thread.start()
    
    main_script()

    audio_thread.join() # Wait for the audio thread to finish


def play_audio(file_path):
    try:
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        status = sd.wait()  # Wait until playback is finished
        if status:
            print(f"Error during playback: {status}")
    except sf.LibsndfileError as e:
        print(f"Error reading OGG file: {e}")
    except sd.PortAudioError as e:
        print(f"Error during playback: {e}")

def flower(type:str):
    ascii_art = ""
    if type == "rose":
        ascii_art=r"""
            _____         
        /  ___  \\
        /  /  _  \  \\
    /( /( /(_)\ )\ )\\
    (  \  \ ___ /  /  )
    (    \ _____ /    )
    /(               )\\
    |  \             /  |
    |    \ _______ /    |
    \    / \   / \    /
    \/    | |    \/
            | | 
            | |
            | |
            Roses to show my love"""
        ascii_art += f"{colors.WHITE}"
            
    elif type == "clover":
            ascii_art=f"""                 ***          ***
                ***....**     **...***
                **........** **.......**
        ***    **..........*.........**    ***
    **.....**  **..................**  **.....**
    **.........**  **..............**  **.........**
    *..............*   *..........*   *..............*
    **..............*   *......*   *..............**
    **..............** *....* **..............**
        *......................................*
    **..............**........**..............**
    **..............*    *....*    *..............**
    *..............*      *....*      *..............*
    **.........**        *....*        **.........**
    **.....**         *....*           **.....**
        ***          **....*               ***
                    ** * * *
                    Clovers to show luck :){colors.YELLOW}"""

    elif type == "tulip":
            ascii_art=r"""         .-""--.,
        /` \.-.{/ \\
        /  .' ; '.  \\
        | /       \ |
        |/         \|
        T      :    Y
        |      :    ;
        |      :    |
  |\.   \     :     /
  | \'.  '.  .    .'
   | |  \   `"T=T"`
    | /   \    | |
    |` :   |   | |
    \   :  |   | |    _ 
    |   .  \  | |  /` `-._
    |   :   | | | |   .'  /'.
    \   .   | | | |  .   |   `\\
    |       | | | |      /     |
    |   '    \| | | :   /'-.   |
    \   '   || |/  ;   |   \  /
    |   :   ;| ||  .   |   '-'
    \   :   || |/ ;    /
    |   '  ;| |  '   |
        \  :  || | '   /
        `\ ' \| ;'   /
        `\' | |  /`
            `\| |/`
            | |
            | |
            | |
            |/
            """


    elif type == "flowey":
            ascii_art =f"""                        `oooooooo/            /oooooooo`                        
                    :sss``+++hMMMMNsssss`  -sssNMMMMMMy+``sss:                   
                    .hmMMMhhho .::::::::::   `::::::::::` yhMMMmh.                 
                    mmMMMMMMN..                            mMMMMMMmm                
                    `:NNN/```  `````NNNNNNNNNNNNNNNN`````  ```/NNN:`                
            .......         .+MMMMMMMMMMMMMMMMMMMMMMMMMM+.         .......         
        :/MMMMMMM:-     :/MMMMMMMMNhhhNMMMMNhhhNMMMMMMMM/:     -:MMMMMMM/:       
        :+NMMMMMMMMMd :+NMMMMMMMMMd   yMMMMy   dMMMMMMMMMN+:   dMMMMMMMMMN+:     
    -omMMNoooooooo/   yMMMMMMMMMMMd   yMMMMy   dMMMMMMMMMMMy   /ooooooooNMMmo-   
    +MMMMNyyyyyyy     yMMMMMMMMMMMd   yMMMMy   dMMMMMMMMMMMy     yyyyyyyNMMMM+   
    +MMMMMMMMMMMMds   yMMMMMMMMMMMd   yMMMMy   dMMMMMMMMMMMy   sdMMMMMMMMMMMM+   
    `...NMMMMMMMMMd   yMMMMMMo.dMMMmmmNMMMMNmmmMMMd.oMMMMMMy   dMMMMMMMMMN...`   
            `mNMMMMMMd.`   mMMMMMM-   ............   -MMMMMMm   `.dMMMMMMNm`        
            :dddddddd+   ydMMMMM+- .dddddddddddd. -+MMMMMdy   +dddddddd:          
                    ./.  `ydMMMMM/:            :/MMMMMdy`  ./.                   
                    ooohM/    .odMMMMmoooooooooooomMMMMdo.    /Mhooo                
                +sMMMMM/      -+++MMMMMMMMMMMMMMMM+++-      /MMMMMs+              
                /hNMMMMh:shhy       ::::::::::::::::       yhhs:hMMMMNh/            
                sMMMMd.+mNMMMmmmmm-                  -mmmmmMMMNm+.dMMMMs            
                sMMMMd`oMMMMMMMMMMNNNNmmmmm``mmmmmNNNNMMMMMMMMMMo`dMMMMs            
                +mmmMMMMMMMMMMNmmmmmmy            ymmmmmmNMMMMMMMMMMmmm+            
                    hhhhhhhhhho                          ohhhhhhhhhh                
                                    -+++`                                        
                                    .ohMMMso                                       
                                    -MMMMMMm                                       
                                    ddMMMMM:-                                       
                                    MMMMM+.                                         
                                    mNMMM+.                                         
                                    -MMMMM/-                                       
                                    .ydMMMMN/-                                     
                                    -omMMMMy                                     
                                        :+NMMms:                                   
                                        mMMMM+                                   
                                        smMMMMMNm-                                 
                                oN-   `+NMMMMMMMMM-  -No                            
                                +m/. -mNMMMMMMMMNm- ./m+                            
                                sh:- :hhhhhhhh: -:hs                              
                                    ss++++++++++++ss                                
                                    `oooooooooooo`
                                And Lil' ol' Flowey from Undertale to show more {colors.RED}L.O.V.E{colors.RESET} ;)"""
        
    for line in ascii_art.splitlines():
                print(line)
                sleep(0.05)
    if type == "tulip":
        print(f"Tulips to show happiness {colors.RED}=){colors.GREEN}")
    print("\n\n\n")

if __name__ == "__main__":
    play_audio_threaded("C:\\Users\\bsthi\\Downloads\\undertale\\Fallen_Down.ogg")
    
def gotcha2():
    msg1 = "DID YOU REALLY THINK THIS WAS A GIFT?"
    msg2 = "Pffft! It's all fake!"
    msg3="Boy! Your son really did play a trick on you with that slide show of a message!"
    msg4="It was so well made that even someone like me, who's soulless, cares about such relation!"
    msg5="Oh well! See you in the next life partner!"
    audio_file = "C:\Users\bsthi\Downloads\undertale\scaryvoice.mp3"  # Replace with your scary sound file path
    for char in msg1:
        print(char, end="")
        sleep(0.1)
        try:
            playsound(audio_file, block=False)  # Non-blocking play
        except PlaysoundException as e:
            print(f"\nError playing scary sound: {e}")
    print("\n")
    sleep(1.5)
    for char in msg2:
        print(char, end="")
        sleep(0.1)
        try:
            playsound(audio_file, block=False)  # Non-blocking play
        except PlaysoundException as e:
            print(f"\nError playing scary sound: {e}")
    print("\n")
    sleep(1.5)
    for char in msg3:
        print(char, end="")
        sleep(0.1)
        try:
            playsound(audio_file, block=False)  # Non-blocking play
        except PlaysoundException as e:
            print(f"\nError playing scary sound: {e}")
    print("\n")
    sleep(1.5)
    for char in msg4:
        print(char, end="")
        sleep(0.1)
        try:
            playsound(audio_file, block=False)  # Non-blocking play
        except PlaysoundException as e:
            print(f"\nError playing scary sound: {e}")
    print("\n")
    sleep(1.5)
    for char in msg5:
        print(char, end="")
        sleep(0.1)
        try:
            playsound(audio_file, block=False)  # Non-blocking play
        except PlaysoundException as e:
            print(f"\nError playing scary sound: {e}")

    # break_computer() # Removed the call here to avoid infinite loop

def play_mus(file):
    try:
        playsound(file, block=False)  # Non-blocking play for the music
    except PlaysoundException as e:
        print(f"\nError playing music: {e}")

def break_computer():
    audio_thread = threading.Thread(target=play_mus,args=("C:\\Users\\bsthi\\Downloads\\undertale\\continous-laugh.mp3",))
    audio_thread.start()
    i = 3
    while i>0 and i < 180000:
        if i %2 == 1:
            print("H",end="")
        else:
            print("A",end="")
        i+=1
    audio_thread.join()
    

def play_audio_threaded(file_path):
    audio_thread = threading.Thread(target=play_mus, args=(file_path,))
    audio_thread.start()

    gotcha2()
    audio_thread.join() # Wait for the audio thread to finish
# Replace "your_music_file.mp3" with the actual path to your music file
# Make sure "scaryvoice.mp3" exists in the same directory or provide the full path
sleep(5)
print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
play_audio_threaded("C:\\Users\\bsthi\\Downloads\\undertale\\gotcha.mp3")
break_computer()
