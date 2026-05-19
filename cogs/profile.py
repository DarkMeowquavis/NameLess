import discord
from discord.ext import commands
import random
from .database import get_db

class Profile(commands.Cog, name="Profile"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        db = await get_db()
        async with db.execute("""
            SELECT void_coins, wins, losses, bio, xp, level 
            FROM players WHERE user_id=?
        """, (member.id,)) as cur:
            row = await cur.fetchone()
        await db.close()

        if not row:
            return await ctx.send("<a:status_offline_animated2:1506135434550579293> This person hasn't entered the game yet.")

        coins, wins, losses, bio, xp, level = row
        
        # Simple XP progress
        xp_needed = level * 300
        progress = (xp % xp_needed) / xp_needed * 100

        embed = discord.Embed(
            title=f"<a:Minecraft_enchanted_book:1506135189556957225> {member.display_name}'s Profile",
            color=0x2F2F2F
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="<a:Shiney_Gold_Coins_Inv:1506135220322177044> Void Coins", 
                       value=f"**{coins:,}**", inline=True)
        embed.add_field(name="🏆 Record", 
                       value=f"**{wins}W** / **{losses}L**", inline=True)
        embed.add_field(name="⭐ Level", 
                       value=f"**{level}**", inline=True)
        
        embed.add_field(name="Bio", 
                       value=bio or "Just another nameless monster...", inline=False)
        
        embed.set_footer(text="“There’s nothing special about being born. Not a thing.” — Johan Liebert")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))