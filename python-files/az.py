
import psutil
import tkinter as tk
import sys
import urllib.parse
import webbrowser


def open_url(base_url, args):
    def quote(arg):
        if ' ' in arg:
            arg = f'"{arg}"'
        return urllib.parse.quote_plus(arg)

    qstring = '+'.join(quote(arg) for arg in args)
    url = urllib.parse.urljoin(base_url, '?q=' + qstring)
    webbrowser.open(url)

def google_search():
    label.config(text="Apertura Google")
    open_url('https://www.google.com/search', sys.argv[1:])

def infinity_chat():
    label.config(text="Apertura Infinity PMI")
    open_url('https://infinity.pmi.org/chat', sys.argv[1:])

def gemini():
    label.config(text="Apertura Gemini")
    open_url('https://gemini.google.com/app/2180eb0bfa7bc5a7?hl=it', sys.argv[1:])

def chatgpt():
    label.config(text="Apertura ChatGPT")
    open_url('https://chatgpt.com/gpts?utm_source=vimeo_912299249', sys.argv[1:])

def copilot():
    label.config(text="Apertura Copilot")
    open_url('https://copilot.microsoft.com/chats/AqAGaHm7ddSrAJbiwZu7H', sys.argv[1:])

def coursera():
    label.config(text="Apertura Coursera")
    open_url('https://www.coursera.org/learn/program-management-execution-stakeholders-governance/lecture/JX7AT/stakeholder-identification-and-analysis', sys.argv[1:])
    
def close_web_pages():
    label.config(text="Chiudo i browser...")
    browser_names = ['chrome', 'firefox', 'edge']
    finestra.destroy()
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'] and any(browser in process.info['name'].lower() for browser in browser_names):
                process.terminate()
                print(f"Closed: {process.info['name']}")
        except Exception as e:
            print(f"Error closing process: {e}")

# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("Finestra con Pulsanti")

# Creazione di un'etichetta
label = tk.Label(finestra, text="", font=("Helvetica", 14))
label.pack(pady=10)

# Creazione dei pulsanti con colori diversi
pulsante_google = tk.Button(finestra, text="Google Search", command=google_search, bg="lightblue", fg="black")
pulsante_google.pack(pady=5)

pulsante_infinity = tk.Button(finestra, text="Infinity PMI", command=infinity_chat, bg="lightgreen", fg="black")
pulsante_infinity.pack(pady=5)

pulsante_gemini = tk.Button(finestra, text="Gemini", command=gemini, bg="yellow", fg="black")
pulsante_gemini.pack(pady=5)

pulsante_chatgpt = tk.Button(finestra, text="ChatGPT", command=chatgpt, bg="orange", fg="black")
pulsante_chatgpt.pack(pady=5)

pulsante_copilot = tk.Button(finestra, text="Copilot", command=copilot, bg="lightyellow", fg="black")
pulsante_copilot.pack(pady=5)

pulsante_coursera = tk.Button(finestra, text="Coursera", command=coursera, bg="pink", fg="black")
pulsante_coursera.pack(pady=5)

pulsante_chiudipagine = tk.Button(finestra, text="Chiudi Pagine", command=close_web_pages, bg="red", fg="black")
pulsante_chiudipagine.pack(pady=5)
#finestra.destroy()

# Avvio del loop principale
finestra.mainloop()