`python
import sqlite3
import requests
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash
from io import BytesIO
import socket
import os
from datetime import datetime
from PIL import Image
import shutil
import threading

# ======================================
# Конфигурация
# ======================================
app = Flask(name)
app.config.update({
    'SECRET_KEY': 'super-secret-key',
    'UPLOAD_FOLDER': 'static/covers',
    'DATABASE': 'game_collection.db',
    'ROMM_CONFIG': {
        'base_url': None,
        'api_key': None,
        'sync_enabled': False,
        'auto_discover': True
    },
    'IGDB_API_KEY': 'your_igdb_key'
})

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ======================================
# База данных (расширенная)
# ======================================
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS games
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        platform TEXT,
        status TEXT DEFAULT "✅ В коллекции",
        playtime INTEGER DEFAULT 0,
        hltb_time INTEGER,
        genre TEXT,
        release_year INTEGER,
        cover_url TEXT,
        rating INTEGER,
        notes TEXT,
        romm_id TEXT UNIQUE,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        igdb_id INTEGER,
        date_added DATE DEFAULT CURRENT_DATE)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS achievements
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        name TEXT,
        completed BOOLEAN DEFAULT 0,
        FOREIGN KEY(game_id) REFERENCES games(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS playlists
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        description TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS game_playlists
        (game_id INTEGER,
        playlist_id INTEGER,
        PRIMARY KEY (game_id, playlist_id),
        FOREIGN KEY(game_id) REFERENCES games(id),
        FOREIGN KEY(playlist_id) REFERENCES playlists(id))''')
    
    # Добавляем тестовые данные, если база пуста
    cursor.execute("SELECT COUNT(*) FROM games")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''INSERT INTO games 
            (title, platform, status, playtime, genre) 
            VALUES (?, ?, ?, ?, ?)''',
            ("The Witcher 3", "PC", "✅ Пройдена", 120, "RPG"))
    
    conn.commit()
    conn.close()

# ======================================
# RomM интеграция (улучшенная)
# ======================================
def discover_romm():
    """Автопоиск сервера RomM в локальной сети"""
    for ip in [f'192.168.1.{i}' for i in range(1, 255)] + ['localhost']:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((ip, 3000)) == 0:
                    return f"http://{ip}:3000"
        except: continue
    return None

def romm_api_request(endpoint):
    """Универсальный запрос к API RomM"""
    if not app.config['ROMM_CONFIG']['base_url']:
        return None
    
    try:
        response = requests.get(
            f"{app.config['ROMM_CONFIG']['base_url']}/api/v2/{endpoint}",
            headers={"Authorization": f"Bearer {app.config['ROMM_CONFIG']['api_key']}"},
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"RomM API error: {str(e)}")
        return None

def sync_with_romm(full_sync=False):
    """Умная синхронизация с RomM"""
    if not app.config['ROMM_CONFIG']['sync_enabled']:
        return {'error': 'Синхронизация отключена'}
    
    try
12:03

:
        # Получаем только изменения после последней синхронизации
        last_sync = datetime.now().isoformat() if full_sync else \
            get_db_value("SELECT MAX(last_updated) FROM games") or "1970-01-01"
        
        platforms = romm_api_request("platforms")
        if not platforms:
            return {'error': 'Не удалось получить платформы из RomM'}
        
        stats = {'added': 0, 'updated': 0, 'unchanged': 0}
        
        for platform in platforms:
            games = romm_api_request(
                f"games?platform={platform['slug']}&updated_after={last_sync}")
            if not games:
                continue
            
            for game in games:
                result = process_romm_game(game, platform)
                stats[result] += 1
        
        return {'success': True, 'stats': stats}
    except Exception as e:
        return {'error': str(e)}

def process_romm_game(game, platform):
    """Обработка одной игры из RomM"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Проверяем существующую запись
    cursor.execute(
        "SELECT id, last_updated FROM games WHERE romm_id=?",
        (game['id'],)
    )
    existing = cursor.fetchone()
    
    # Подготовка данных
    game_data = {
        'title': game.get('name'),
        'platform': platform.get('name'),
        'genre': ', '.join(game.get('genres', [])),
        'release_year': game.get('release_date', '')[:4],
        'cover_url': download_romm_asset(game.get('cover')),
        'romm_id': game['id'],
        'igdb_id': game.get('igdb_id'),
        'last_updated': datetime.now().isoformat()
    }
    
    if existing:
        # Обновляем только если данные новее
        if game['updated_at'] > existing[1]:
            cursor.execute('''
                UPDATE games SET 
                title=?, platform=?, genre=?, release_year=?, 
                cover_url=?, igdb_id=?, last_updated=?
                WHERE id=?
            ''', (*game_data.values(), existing[0]))
            conn.commit()
            conn.close()
            return 'updated'
        return 'unchanged'
    else:
        # Добавляем новую игру
        cursor.execute('''
            INSERT INTO games 
            (title, platform, genre, release_year, cover_url, romm_id, igdb_id, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(game_data.values()))
        conn.commit()
        
        # Дополняем метаданные из IGDB
        if game_data['igdb_id']:
            threading.Thread(
                target=fetch_igdb_metadata,
                args=(game_data['igdb_id'], cursor.lastrowid)
            ).start()
        
        conn.close()
        return 'added'

def download_romm_asset(asset_id):
    """Загрузка обложки из RomM"""
    if not asset_id:
        return None
    
    try:
        filename = f"romm_{asset_id}.jpg"
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(local_path):
            response = requests.get(
                f"{app.config['ROMM_CONFIG']['base_url']}/api/v2/assets/{asset_id}/file",
                headers={"Authorization": f"Bearer {app.config['ROMM_CONFIG']['api_key']}"},
                stream=True
            )
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
        
        return f"/static/covers/{filename}" if os.path.exists(local_path) else None
    except Exception as e:
        print(f"Error downloading asset: {str(e)}")
        return None

# ======================================
# IGDB интеграция
# ======================================
def fetch_igdb_metadata(igdb_id, local_game_id):
    """Дополнение метаданных из IGDB"""
    try:
        response = requests.post(
            "https://api.igdb.com/v4/games",
            h
12:03

eaders={"Authorization": f"Bearer {app.config['IGDB_API_KEY']}"},
            data=f"fields name,genres.name,summary,total_rating,time_to_beat; where id = {igdb_id};"
        )
        
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE games SET 
                genre=COALESCE(genre, ?), 
                notes=COALESCE(notes, ?),
                rating=COALESCE(rating, ?),
                hltb_time=COALESCE(hltb_time, ?)
                WHERE id=?
            ''', (
                ', '.join([g['name'] for g in data.get('genres', [])]),
                data.get('summary'),
                round(data.get('total_rating', 0)) if data.get('total_rating') else None,
                data.get('time_to_beat', {}).get('normally', 0),
                local_game_id
            ))
            
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"IGDB error: {str(e)}")

# ======================================
# Аналитика и рекомендации
# ======================================
def generate_recommendations():
    """Генерация рекомендаций на основе коллекции"""
    conn = sqlite3.connect(app.config['DATABASE'])
    
    # Анализ предпочитаемых жанров
    top_genres = pd.read_sql('''
        SELECT genre, COUNT(*) as count 
        FROM games 
        WHERE status='✅ В коллекции'
        GROUP BY genre 
        ORDER BY count DESC 
        LIMIT 3
    ''', conn)['genre'].tolist()
    
    # Поиск похожих игр
    recommendations = pd.read_sql(f'''
        SELECT title, platform, rating 
        FROM games 
        WHERE genre IN ({','.join(['?']*len(top_genres))})
        AND status != '✅ В коллекции'
        ORDER BY rating DESC
        LIMIT 5
    ''', conn, params=top_genres).to_dict('records')
    
    conn.close()
    return recommendations

def generate_stats():
    """Расширенная аналитика коллекции"""
    conn = sqlite3.connect(app.config['DATABASE'])
    
    # Основная статистика
    stats = pd.read_sql('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status='✅ В коллекции' THEN 1 ELSE 0 END) as owned,
            SUM(CASE WHEN status='✅ Пройдена' THEN 1 ELSE 0 END) as completed,
            SUM(playtime) / 60 as total_hours
        FROM games
    ''', conn).iloc[0].to_dict()
    
    # Время прохождения vs HLTB
    time_comparison = pd.read_sql('''
        SELECT title, playtime, hltb_time 
        FROM games 
        WHERE playtime > 0 AND hltb_time > 0
        LIMIT 50
    ''', conn)
    
    # Генерация графика
    if not time_comparison.empty:
        plt.figure(figsize=(10, 6))
        plt.scatter(time_comparison['hltb_time'], time_comparison['playtime'])
        plt.plot([0, max(time_comparison['hltb_time'].max(), time_comparison['playtime'].max())], 
                [0, max(time_comparison['hltb_time'].max(), time_comparison['playtime'].max())], 
                'r--')
        plt.xlabel('HLTB Time (hours)')
        plt.ylabel('Your Time (hours)')
        plt.title('Your Playtime vs Average')
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        stats['time_chart'] = buf.read().hex()
        plt.close()
    
    conn.close()
    return stats

# ======================================
# Вспомогательные функции
# ======================================

def get_db_value(query, params=()):
    """Получение одного значения из БД"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ======================================
# Веб-интерфейс (ключевые эндпоинты)
# ======================================
@app.route('/')
def index():
    return render_template_string('''
12:03

<h1>Game Collection Manager</h1>
        <p>Используйте API эндпоинты для взаимодействия:</p>
        <ul>
            <li>GET /api/games - список игр</li>
            <li>POST /api/sync/romm - синхронизация с RomM</li>
            <li>GET /api/stats - статистика коллекции</li>
            <li>GET /api/recommendations - рекомендации</li>
        </ul>
    ''')

@app.route('/api/games', methods=['GET'])
def get_games():
    """Получение списка игр с фильтрацией"""
    filters = {
        'platform': request.args.get('platform'),
        'status': request.args.get('status'),
        'genre': request.args.get('genre')
    }
    
    query = "SELECT * FROM games WHERE 1=1"
    params = []
    
    for key, value in filters.items():
        if value:
            query += f" AND {key} = ?"
            params.append(value)
    
    conn = sqlite3.connect(app.config['DATABASE'])
    games = pd.read_sql(query, conn, params=params).to_dict('records')
    conn.close()
    
    return jsonify(games)

@app.route('/api/sync/romm', methods=['POST'])
def sync_romm():
    """Запуск синхронизации с RomM"""
    result = sync_with_romm()
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получение статистики коллекции"""
    return jsonify(generate_stats())

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Получение рекомендаций"""
    return jsonify(generate_recommendations())

@app.route('/api/playlists', methods=['GET', 'POST'])
def manage_playlists():
    """Управление игровыми плейлистами"""
    if request.method == 'POST':
        # Создание нового плейлиста
        data = request.json
        if not data or not data.get('name'):
            return jsonify({'error': 'Не указано название плейлиста'}), 400
        
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO playlists (name, description) VALUES (?, ?)",
                (data['name'], data.get('description', ''))
            )
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Плейлист с таким именем уже существует'}), 400
        finally:
            conn.close()
    else:
        # Получение списка плейлистов
        conn = sqlite3.connect(app.config['DATABASE'])
        playlists = pd.read_sql("SELECT * FROM playlists", conn).to_dict('records')
        conn.close()
        return jsonify(playlists)

# ======================================
# Запуск приложения
# ======================================
if name == 'main':
    init_db()
    
    # Автопоиск RomM при первом запуске
    if app.config['ROMM_CONFIG']['auto_discover']:
        romm_url = discover_romm()
        if romm_url:
            app.config['ROMM_CONFIG']['base_url'] = romm_url
            print(f"Автоматически обнаружен RomM: {romm_url}")
    
    # Запуск веб-сервера
    app.run(host='0.0.0.0', port=5000, debug=True)
`