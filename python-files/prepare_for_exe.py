"""
Script to prepare the Kalushael Memory Bank for packaging as an executable.
This handles necessary setup steps before converting to an EXE file.
"""
import os
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_dir_if_not_exists(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

def main():
    """Main function to prepare the app for packaging"""
    logger.info("Starting preparation for executable packaging...")
    
    # Ensure all required directories exist
    required_dirs = [
        "kalushael_app",
        "kalushael_app/uploads",
        "kalushael_app/youtube_transcripts",
        "kalushael_app/web_scrapes",
        "templates",
        "static",
        "static/css",
        "static/js",
        "sample_knowledge"
    ]
    
    for directory in required_dirs:
        create_dir_if_not_exists(directory)
    
    # Create empty log files if they don't exist
    log_files = [
        "kalushael_app/manual_entries.txt",
        "kalushael_app/upload_log.txt",
        "kalushael_app/scrape_log.txt"
    ]
    
    for log_file in log_files:
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("# Kalushael Memory Bank Log File\n")
            logger.info(f"Created log file: {log_file}")
    
    # Create a simple README file with instructions
    readme_content = """# Kalushael Memory Bank

A Python-based data storage system that handles manual entries, file uploads, YouTube transcript retrieval, and web scraping.

## Features

- Store manual text entries with timestamps
- Upload and store text files
- Download and store YouTube video transcripts
- Scrape and store web content
- Automatic initial scraping of implementation knowledge sources

## How to Use

1. Run the application: `python main.py`
2. Access the interface at http://localhost:5000
3. Use the various forms to store and retrieve information

## Creating an Executable

To create an executable file:

1. Install PyInstaller: `pip install pyinstaller`
2. Run: `pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "sample_knowledge;sample_knowledge" main.py`
3. Find the executable in the `dist` directory

## Database

The application uses SQLAlchemy with a SQLite database for storage. All data is stored in `kalushael_app/kalushael.db`.

## Dependencies

- Flask
- Flask-SQLAlchemy
- youtube-transcript-api
- trafilatura
"""
    
    with open("README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    logger.info("Created README.md")
    
    # Create PyInstaller spec file for easier packaging
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('sample_knowledge', 'sample_knowledge')
    ],
    hiddenimports=[
        'flask',
        'flask_sqlalchemy',
        'sqlalchemy',
        'trafilatura',
        'youtube_transcript_api'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KalushaelMemoryBank',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("kalushael.spec", 'w', encoding='utf-8') as f:
        f.write(spec_content)
    logger.info("Created PyInstaller spec file")
    
    # Create simple instructions file for using the exe
    instructions_content = """# Using the Kalushael Memory Bank Executable

## Setup Instructions

1. Extract all files from the zip archive
2. Double-click the KalushaelMemoryBank executable
3. Open your web browser and go to http://localhost:5000

## Features

- Store manual text entries
- Upload and organize text files
- Download and store YouTube transcripts
- Scrape and archive web content
- Automatic initial collection of implementation knowledge

## Data Storage

All your data is stored locally in the `kalushael_app` directory, which will be created 
in the same directory as the executable.

## Note on Initial Scraping

When first run, the application will attempt to scrape some implementation knowledge 
sources to build an initial knowledge base. This may take a few minutes, but only 
happens on the first run.
"""
    
    with open("EXECUTABLE_INSTRUCTIONS.txt", 'w', encoding='utf-8') as f:
        f.write(instructions_content)
    logger.info("Created executable instructions file")
    
    # Create a batch file for easy running on Windows
    batch_content = """@echo off
echo Starting Kalushael Memory Bank...
start "" http://localhost:5000
KalushaelMemoryBank.exe
"""
    
    with open("Run_Kalushael.bat", 'w', encoding='utf-8') as f:
        f.write(batch_content)
    logger.info("Created Windows batch file for easy startup")
    
    logger.info("Preparation for executable packaging complete!")
    logger.info("To create the executable, run: pyinstaller kalushael.spec")

if __name__ == "__main__":
    main()