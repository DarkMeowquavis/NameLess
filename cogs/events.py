import discord
from discord.ext import commands
import time
import asyncio
from .database import get_db

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_start = {}
        self.bot.loop.create_task(self.voice_update_loop())

    # ==================== LOGS HELPER ====================
    async def send_log(self, guild, title: str, description: str, color=0x2F2F2F):
        if not guild:
            return
        logs_cog = self.bot.get_cog("Logs")
        if logs_cog:
            await logs_cog.send_log(guild, title, description, color)

    # ==================== MESSAGE LOGS ====================
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        desc = f"**Author:** {message.author} ({message.author.id})\n**Channel:** {message.channel.mention}\n**Content:** {message.content[:500]}"
        await self.send_log(message.guild, "🗑️ Message Deleted", desc, 0xff0000)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        desc = f"**Author:** {before.author}\n**Channel:** {before.channel.mention}\n**Before:** {before.content[:500]}\n**After:** {after.content[:500]}"
        await self.send_log(before.guild, "✏️ Message Edited", desc, 0xffff00)

    # ==================== MESSAGE COUNTING ====================
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
            
        db = await get_db()
        await db.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (message.author.id,))
        await db.execute("UPDATE players SET messages_sent = messages_sent + 1 WHERE user_id = ?", (message.author.id,))
        await db.commit()
        await db.close()

    # ==================== VOICE LOGS + TRACKING ====================
    async def voice_update_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                current_time = time.time()
                to_save = []

                for user_id, start_time in list(self.voice_start.items()):
                    duration = int(current_time - start_time)
                    if duration >= 60:
                        to_save.append((user_id, duration))
                        self.voice_start[user_id] = current_time

                if to_save:
                    db = await get_db()
                    for user_id, duration in to_save:
                        await db.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (user_id,))
                        await db.execute("UPDATE players SET voice_time = voice_time + ? WHERE user_id = ?", (duration, user_id))
                    await db.commit()
                    await db.close()
            except:
                pass
            await asyncio.sleep(30)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or not member.guild:
            return

        user_id = member.id

        # Voice Join
        if before.channel is None and after.channel is not None:
            self.voice_start[user_id] = time.time()
            desc = f"**User:** {member.mention} ({member.id})\n**Channel:** {after.channel.name}"
            await self.send_log(member.guild, "🎙️ Voice Join", desc, 0x00ff00)

        # Voice Leave
        elif before.channel is not None and after.channel is None:
            if user_id in self.voice_start:
                duration = int(time.time() - self.voice_start[user_id])
                if duration >= 30:
                    desc = f"**User:** {member.mention} ({member.id})\n**Left Channel:** {before.channel.name}\n**Time Spent:** {duration//3600}h {(duration%3600)//60}m {duration%60}s"
                    await self.send_log(member.guild, "🚪 Voice Leave", desc, 0xff8800)

                # Save remaining time
                db = await get_db()
                await db.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (user_id,))
                await db.execute("UPDATE players SET voice_time = voice_time + ? WHERE user_id = ?", (duration, user_id))
                await db.commit()
                await db.close()

                del self.voice_start[user_id]

async def setup(bot):
    await bot.add_cog(Events(bot))