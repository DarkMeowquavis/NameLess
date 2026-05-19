import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

# Disable default help command
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# ==================== SET BOT OWNER ====================
bot.owner_id = 1362631068879946010   # ← Your ID (You can now use owner-only commands)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is now online!')
   
    # Initialize Database
    try:
        from cogs.database import get_db
        await get_db()
        print("✅ Database initialized successfully! (namelessbot.db)")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Johan Liebert Theme
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="the nameless monster"
    )
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print("🖤 Johan Liebert theme activated.")
   
    # Load Cogs
    await load_cogs()

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if filename == "database.py":  # Skip database
                continue
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

# Ping Command
@bot.command()
async def ping(ctx):
    embed = discord.Embed(
        title="Pong.",
        description=f"`{round(bot.latency * 1000)}ms`",
        color=0x2F2F2F
    )
    await ctx.send(embed=embed)

async def main():
    await bot.start(os.getenv("TOKEN"))

import asyncio
asyncio.run(main())