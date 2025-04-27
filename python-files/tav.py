import sys
import requests
from bs4 import BeautifulSoup
import os
import shutil
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def color_text(tag, text):
    if tag.name in ['h1', 'h2', 'h3']:
        return Fore.CYAN + Style.BRIGHT + text + Style.RESET_ALL
    elif tag.name == 'title':
        return Fore.MAGENTA + Style.BRIGHT + text + Style.RESET_ALL
    elif tag.name == 'p':
        return Fore.WHITE + text + "\n"
    else:
        return text

def extract_and_color_text(soup):
    output = []

    for elem in soup.find_all(['title', 'h1', 'h2', 'h3', 'p', 'li']):
        text = elem.get_text(strip=True)
        if text:
            output.append(color_text(elem, text))

    return "\n".join(output)

def paginate_output(text):
    lines = text.splitlines()
    terminal_size = shutil.get_terminal_size((80, 20))
    page_height = terminal_size.lines - 2

    for i in range(0, len(lines), page_height):
        os.system('clear' if os.name == 'posix' else 'cls')
        chunk = lines[i:i+page_height]
        print("\n".join(chunk))
        if i + page_height < len(lines):
            input("\n-- Press Enter to continue --")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL>")
        sys.exit(1)

    url = sys.argv[1]

    # Download the HTML
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"Failed to download {url} (status code: {response.status_code})")
        sys.exit(1)

    # Parse and process text
    soup = BeautifulSoup(html_content, "html.parser")
    colored_text = extract_and_color_text(soup)

    # Paginate and display
    paginate_output(colored_text)

if __name__ == "__main__":
    main()
