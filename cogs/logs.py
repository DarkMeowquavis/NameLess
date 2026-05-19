import discord
from discord.ext import commands
from .database import get_db
import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, title: str, description: str, color=0x2F2F2F):
        """Send log to the set logs channel"""
        if not guild:
            return
            
        db = await get_db()
        async with db.execute("SELECT logs_channel FROM settings WHERE guild_id=?", (guild.id,)) as cur:
            row = await cur.fetchone()
        await db.close()

        if not row or not row[0]:
            return

        channel = guild.get_channel(row[0])
        if not channel:
            return

        embed = discord.Embed(
            title=f"<a:Royalrole:1506135213426868336> {title}",
            description=description,
            color=color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="NameLessBot • Logs")
        
        try:
            await channel.send(embed=embed)
        except:
            pass

    # ==================== COMMANDS ====================
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogs(self, ctx, channel: discord.TextChannel = None):
        """Set the logs channel"""
        if not channel:
            channel = ctx.channel

        db = await get_db()
        await db.execute("INSERT OR REPLACE INTO settings (guild_id, logs_channel) VALUES (?, ?)",
                        (ctx.guild.id, channel.id))
        await db.commit()
        await db.close()

        embed = discord.Embed(
            title="<a:Royalrole:1506135213426868336> Logs Channel Set",
            description=f"All important logs will now be sent to {channel.mention}",
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removlogs(self, ctx):
        """Remove logs channel"""
        db = await get_db()
        await db.execute("INSERT OR REPLACE INTO settings (guild_id, logs_channel) VALUES (?, NULL)",
                        (ctx.guild.id,))
        await db.commit()
        await db.close()
        await ctx.send("✅ Logs channel has been removed.")

async def setup(bot):
    await bot.add_cog(Logs(bot))