import webbrowser
import os

# Channel URL
url = "https://www.youtube.com/@MarinerKevs"

# Attempt to use Chrome directly if possible
try:
    if os.name == "nt":  # Windows
        chrome_path = "C://Program Files//Google//Chrome//Application//chrome.exe %s"
    elif os.name == "posix":  # macOS or Linux
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome %s"
    else:
        chrome_path = None

    if chrome_path:
        webbrowser.get(chrome_path).open_new(url)
    else:
        webbrowser.open_new_tab(url)
except:
    # Fall back to default browser
    webbrowser.open_new_tab(url)
