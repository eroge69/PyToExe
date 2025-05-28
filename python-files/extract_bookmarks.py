
import os
import csv
import json
import sqlite3

# Function to extract bookmarks from Chrome
def extract_chrome_bookmarks():
    bookmarks_path = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\Bookmarks'
    with open(bookmarks_path, 'r', encoding='utf-8') as f:
        bookmarks_data = json.load(f)
    
    bookmarks = []
    def parse_bookmarks(bookmark_folder):
        for item in bookmark_folder['children']:
            if item['type'] == 'url':
                bookmarks.append([item['name'], item['url'], bookmark_folder['name']])
            elif item['type'] == 'folder':
                parse_bookmarks(item)
    
    parse_bookmarks(bookmarks_data['roots']['bookmark_bar'])
    return bookmarks

# Function to extract bookmarks from Firefox
def extract_firefox_bookmarks():
    places_path = os.path.expanduser('~') + r'\AppData\Roaming\Mozilla\Firefox\Profiles'
    profile_folder = [f for f in os.listdir(places_path) if f.endswith('.default-release')][0]
    places_path = os.path.join(places_path, profile_folder, 'places.sqlite')
    
    conn = sqlite3.connect(places_path)
    cursor = conn.cursor()
    cursor.execute("SELECT moz_bookmarks.title, moz_places.url, moz_bookmarks.parent FROM moz_bookmarks JOIN moz_places ON moz_bookmarks.fk = moz_places.id WHERE moz_bookmarks.type = 1")
    bookmarks = cursor.fetchall()
    conn.close()
    
    return bookmarks

# Function to extract bookmarks from Edge
def extract_edge_bookmarks():
    bookmarks_path = os.path.expanduser('~') + r'\AppData\Local\Microsoft\Edge\User Data\Default\Bookmarks'
    with open(bookmarks_path, 'r', encoding='utf-8') as f:
        bookmarks_data = json.load(f)
    
    bookmarks = []
    def parse_bookmarks(bookmark_folder):
        for item in bookmark_folder['children']:
            if item['type'] == 'url':
                bookmarks.append([item['name'], item['url'], bookmark_folder['name']])
            elif item['type'] == 'folder':
                parse_bookmarks(item)
    
    parse_bookmarks(bookmarks_data['roots']['bookmark_bar'])
    return bookmarks

# Function to extract bookmarks from Brave
def extract_brave_bookmarks():
    bookmarks_path = os.path.expanduser('~') + r'\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Bookmarks'
    with open(bookmarks_path, 'r', encoding='utf-8') as f:
        bookmarks_data = json.load(f)
    
    bookmarks = []
    def parse_bookmarks(bookmark_folder):
        for item in bookmark_folder['children']:
            if item['type'] == 'url':
                bookmarks.append([item['name'], item['url'], bookmark_folder['name']])
            elif item['type'] == 'folder':
                parse_bookmarks(item)
    
    parse_bookmarks(bookmarks_data['roots']['bookmark_bar'])
    return bookmarks

# Function to save bookmarks to CSV
def save_to_csv(bookmarks, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'URL', 'Folder'])
        writer.writerows(bookmarks)

# Create FAVORIS folder
if not os.path.exists('FAVORIS'):
    os.makedirs('FAVORIS')

# Extract and save bookmarks for each browser
save_to_csv(extract_chrome_bookmarks(), 'FAVORIS/chrome_bookmarks.csv')
save_to_csv(extract_firefox_bookmarks(), 'FAVORIS/firefox_bookmarks.csv')
save_to_csv(extract_edge_bookmarks(), 'FAVORIS/edge_bookmarks.csv')
save_to_csv(extract_brave_bookmarks(), 'FAVORIS/brave_bookmarks.csv')

print("Bookmarks have been successfully exported to the FAVORIS folder.")
