import discord
from discord.ext import commands
import asyncio
import os
import time

CATEGORY_IDS = [1326941336154275903, 1326885112197021766]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

async def animated_text(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

async def main():
    clear()
    await animated_text("🔒 Simpstore Ticket Cleaner Tool\n", 0.04)
    token = input("🔑 Enter your bot token: ").strip()

    intents = discord.Intents.default()
    intents.guilds = True
    intents.guild_messages = True
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        clear()
        await animated_text(f"✅ Logged in as {bot.user}!\n", 0.04)

        for guild in bot.guilds:
            await animated_text(f"🔎 Checking guild: {guild.name}...\n", 0.02)

            for category_id in CATEGORY_IDS:
                category = guild.get_channel(category_id)
                if not category:
                    await animated_text(f"⚠️ Category ID {category_id} not found.\n", 0.02)
                    continue

                await animated_text(f"🧹 Deleting channels in: {category.name}...\n", 0.03)

                for channel in category.channels:
                    try:
                        await channel.delete(reason="Mass ticket close by admin tool")
                        await animated_text(f"🗑️ Deleted: {channel.name}", 0.01)
                    except Exception as e:
                        await animated_text(f"❌ Failed to delete {channel.name}: {e}", 0.01)

        await animated_text("\n✅ All tickets have been cleaned up.\n", 0.04)
        await bot.close()

    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Invalid token. Please try again.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Exiting.")
