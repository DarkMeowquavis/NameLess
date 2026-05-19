import discord
from discord.ext import commands
import time

class AFK(commands.Cog, name="AFK"):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}  # {user_id: {"reason": str, "timestamp": int}}

    @commands.command()
    async def afk(self, ctx, *, reason: str = None):
        """Set AFK or remove AFK"""
        
        # Remove AFK
        if reason and reason.lower() in ["off", "remove", "end", "back", "done"]:
            if ctx.author.id in self.afk_users:
                data = self.afk_users.pop(ctx.author.id)
                duration = int(time.time()) - data["timestamp"]
                minutes = duration // 60
                seconds = duration % 60

                embed = discord.Embed(
                    title="<a:Animated_Verified:1506135122070605896> AFK Mode Disabled",
                    description=f"Welcome back, {ctx.author.mention}!",
                    color=0x2F2F2F
                )
                embed.add_field(name="AFK Duration", value=f"**{minutes}m {seconds}s**", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ You are not in AFK mode.")
            return

        # Set AFK
        if not reason:
            reason = "No reason given"
        
        self.afk_users[ctx.author.id] = {
            "reason": reason,
            "timestamp": int(time.time())
        }

        embed = discord.Embed(
            title="<a:status_offline_animated2:1506135434550579293> AFK Mode Enabled",
            description=f"{ctx.author.mention} is now **AFK**",
            color=0x2F2F2F
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text="“Even monsters need rest sometimes...” — Johan Liebert")
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        author_id = message.author.id

        # Ignore if the message is an afk command
        if message.content.lower().startswith('+afk'):
            return

        # Auto remove AFK when user sends normal message
        if author_id in self.afk_users:
            data = self.afk_users.pop(author_id)
            duration = int(time.time()) - data["timestamp"]
            minutes = duration // 60
            seconds = duration % 60

            embed = discord.Embed(
                title="<a:Animated_Verified:1506135122070605896> AFK Mode Disabled",
                description=f"Welcome back, {message.author.mention}!",
                color=0x2F2F2F
            )
            embed.add_field(name="AFK Duration", value=f"**{minutes}m {seconds}s**", inline=False)
            await message.channel.send(embed=embed, delete_after=8)

        # Notify when someone mentions an AFK user
        for user_id in list(self.afk_users.keys()):
            if user_id in [m.id for m in message.mentions]:
                data = self.afk_users[user_id]
                member = message.guild.get_member(user_id)
                if member:
                    duration = int(time.time()) - data["timestamp"]
                    minutes = duration // 60
                    embed = discord.Embed(
                        title="<a:status_offline_animated2:1506135434550579293> User is AFK",
                        description=f"{member.mention} is currently AFK.",
                        color=0x2F2F2F
                    )
                    embed.add_field(name="Reason", value=data["reason"], inline=False)
                    embed.add_field(name="AFK for", value=f"{minutes} minutes", inline=False)
                    await message.channel.send(embed=embed, delete_after=10)

async def setup(bot):
    await bot.add_cog(AFK(bot))