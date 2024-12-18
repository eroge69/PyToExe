import os
from flask import Flask, render_template, request, send_file
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file and file.filename.endswith('.py'):
        unique_id = str(uuid.uuid4())
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_id + '.py')
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], unique_id)

        # Save uploaded file
        file.save(input_path)

        # Convert to EXE using PyInstaller
        try:
            subprocess.run(
                [
                    "pyinstaller",
                    "--onefile",
                    "--distpath", app.config['OUTPUT_FOLDER'],
                    input_path
                ],
                check=True
            )
            exe_path = os.path.join(app.config['OUTPUT_FOLDER'], unique_id + '.exe')
            return send_file(
                exe_path, as_attachment=True, download_name=f"{file.filename.replace('.py', '.exe')}"
            )
        except Exception as e:
            return f"Error during conversion: {str(e)}"
        finally:
            # Cleanup temporary files
            if os.path.exists(input_path):
                os.remove(input_path)
    else:
        return "Invalid file format. Please upload a .py file."

if __name__ == '__main__':
    app.run(debug=True)
