import webbrowser
import threading
from app import app

def run():
    app.run(debug=False, port=5000, host='127.0.0.1')

if __name__ == '__main__':
    threading.Thread(target=run).start()
    webbrowser.open('http://localhost:5000/cliente')