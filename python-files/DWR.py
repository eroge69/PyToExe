from flask import Flask, send_from_directory, abort
import os
import threading
import os
import signal

app = Flask(__name__)

# Folder containing GIF images
IMAGE_FOLDER = r'C:\ftp\rb5gif'  # ✅ Use raw string for Windows paths

@app.route('/images/<filename>')
def download_image(filename):
    #Block access if the file isn't a .gif
    if not filename.lower().endswith('.gif'):
        abort(403)  # Forbidden

    # ✅ Serve the .gif file if it exists
    return send_from_directory(IMAGE_FOLDER, filename)

def auto_shutdown():
    """Shuts down the Flask server after 5 minutes."""
    print("5 minutes passed. Server is shutting down...")
    os.kill(os.getpid(), signal.SIGINT)  # Send SIGINT signal to terminate the server

if __name__ == '__main__':
    # Start the auto-shutdown timer (5 minutes = 300 seconds)
    threading.Timer(300, auto_shutdown).start()
    
    print("Server running. Will shut down in 5 minutes...")
    app.run(host='0.0.0.0', port=5000)
