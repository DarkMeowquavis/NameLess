import discord
from discord.ext import commands
import random
from .database import get_db

class Crime(commands.Cog, name="Crime"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 50, commands.BucketType.user)
    async def rob(self, ctx, member: discord.Member):
        if member == ctx.author:
            embed = discord.Embed(
                title="<a:status_offline_animated2:1506135434550579293> Robbery Failed",
                description="You can't rob yourself... even Johan wouldn't do that.",
                color=0x2F2F2F
            )
            return await ctx.send(embed=embed)

        success = random.random() < 0.58

        db = await get_db()
        await db.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (ctx.author.id,))

        if success:
            amount = random.randint(80, 280)
            await db.execute("UPDATE players SET void_coins = void_coins + ? WHERE user_id = ?", 
                           (amount, ctx.author.id))
            embed = discord.Embed(
                title="<a:pepepoliceAnimated:1506135199875076227> Robbery Successful",
                description=f"You successfully robbed **{member.display_name}** for <a:Shiney_Gold_Coins_Inv:1506135220322177044> **{amount} Void Coins**.",
                color=0x2F2F2F
            )
        else:
            loss = random.randint(50, 150)
            await db.execute("UPDATE players SET void_coins = void_coins - ? WHERE user_id = ?", 
                           (loss, ctx.author.id))
            embed = discord.Embed(
                title="<a:yeheboianimated:1506135257533911100> Robbery Failed",
                description=f"You got caught robbing **{member.display_name}**. Lost <a:Shiney_Gold_Coins_Inv:1506135220322177044> **{loss} Void Coins**.",
                color=0x2F2F2F
            )

        await db.commit()
        await db.close()
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Crime(bot))