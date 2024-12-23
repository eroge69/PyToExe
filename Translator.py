import curses
import pyperclip

# Al Bhed cipher
ALBHED = "ypltavkrezgmshubxncdijfqow"
ENGLISH = "abcdefghijklmnopqrstuvwxyz"

# Extended cipher for uppercase letters
ALBHED_UPPER = ALBHED.upper()
ENGLISH_UPPER = ENGLISH.upper()

def translate(text, to_al_bhed):
    source_lower, target_lower = (ENGLISH, ALBHED) if to_al_bhed else (ALBHED, ENGLISH)
    source_upper, target_upper = (ENGLISH_UPPER, ALBHED_UPPER) if to_al_bhed else (ALBHED_UPPER, ENGLISH_UPPER)
    translation_table = str.maketrans(source_lower + source_upper, target_lower + target_upper)
    return text.translate(translation_table)

def main(stdscr):
    # Initialize curses
    curses.curs_set(1)
    stdscr.clear()
    
    # States
    to_al_bhed = True
    input_text = ""
    translation = ""

    while True:
        # Clear screen
        stdscr.clear()
        
        # Display translation direction
        direction = "Al Bhed -> English" if not to_al_bhed else "English -> Al Bhed"
        stdscr.addstr(0, 0, f"Translation Direction: {direction}")
        stdscr.addstr(2, 0, "Input: " + input_text)
        stdscr.addstr(4, 0, "Translation: " + translation)

        # Refresh screen
        stdscr.refresh()

        # Get user input
        key = stdscr.getch()

        if key == 27:  # ESC key
            input_text = ""
            translation = ""
        elif key == 9:  # TAB key
            to_al_bhed = not to_al_bhed
            translation = translate(input_text, to_al_bhed)
            pyperclip.copy(translation)
        elif key == 10:  # ENTER key
            translation = translate(input_text, to_al_bhed)
            pyperclip.copy(translation)
        elif key in (8, 127, curses.KEY_BACKSPACE):  # Handle Backspace
            input_text = input_text[:-1]
        elif key == 22:  # CTRL + V
            input_text = pyperclip.paste()
            translation = translate(input_text, to_al_bhed)
        elif 32 <= key <= 126:  # Printable characters
            input_text += chr(key)

if __name__ == "__main__":
    curses.wrapper(main)
