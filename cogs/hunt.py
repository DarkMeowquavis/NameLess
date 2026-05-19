import discord
from discord.ext import commands
import random
from .database import get_db

creatures = [
    ("The Nameless Monster", 250, 500),
    ("Johan Liebert's Shadow", 180, 350),
    ("Dr. Tenma's Nightmare", 120, 280),
    ("A Perfect Serial Killer", 200, 420),
    ("The Monster Within You", 150, 320),
    ("Franz Bonaparta's Legacy", 100, 250)
]

class Hunt(commands.Cog, name="Hunt"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 40, commands.BucketType.user)
    async def hunt(self, ctx):
        creature, min_r, max_r = random.choice(creatures)
        success = random.random() < 0.68

        embed = discord.Embed(
            title="<:emoji_3:1506135700502741173> Hunting in the Darkness...",
            color=0x2F2F2F
        )
        embed.add_field(name="Target", value=creature, inline=False)

        db = await get_db()
        await db.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (ctx.author.id,))

        if success:
            reward = random.randint(min_r, max_r)
            await db.execute("UPDATE players SET void_coins = void_coins + ?, wins = wins + 1 WHERE user_id = ?", 
                           (reward, ctx.author.id))
            embed.description = f"You eliminated **{creature}**.\n<a:Shiney_Gold_Coins_Inv:1506135220322177044> **+{reward} Void Coins**"
            embed.set_footer(text="“Look at the eyes. They never lie.” — Johan Liebert")
        else:
            await db.execute("UPDATE players SET losses = losses + 1 WHERE user_id = ?", (ctx.author.id,))
            embed.description = f"**{creature}** consumed you."
            embed.set_footer(text="<a:status_offline_animated2:1506135434550579293> Death is the only equality.")

        await db.commit()
        await db.close()
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Hunt(bot))