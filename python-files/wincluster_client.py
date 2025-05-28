import os
from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

BACKUP_DIR = os.path.join(os.path.dirname(__file__), "cluster_backups")
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

API_TOKEN = "byt-mig-till-något-hemligt"  # Samma som i huvudpanelen

def api_auth():
    token = request.headers.get("X-Panel-Token")
    return token == API_TOKEN

@app.route('/api/cluster/upload', methods=['POST'])
def cluster_upload():
    if not api_auth():
        return jsonify({"error": "Unauthorized"}), 403
    file = request.files.get('file')
    server = request.form.get('server', 'unknown')
    if not file:
        return jsonify({"error": "Ingen fil"}), 400
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    server_dir = os.path.join(BACKUP_DIR, server)
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)
    dest = os.path.join(server_dir, f"{now}_{file.filename}")
    file.save(dest)
    return jsonify({"status": "saved", "path": dest})

@app.route('/api/cluster/list', methods=['GET'])
def cluster_list():
    if not api_auth():
        return jsonify({"error": "Unauthorized"}), 403
    result = {}
    for server in os.listdir(BACKUP_DIR):
        files = os.listdir(os.path.join(BACKUP_DIR, server))
        result[server] = files
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)