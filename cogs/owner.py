import discord
from discord.ext import commands
import os
import sys
import asyncio

class Owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str = None):
        """Reload a specific cog"""
        if not cog:
            return await ctx.send("❌ Please specify a cog. Example: `+reload economy`")

        cog_name = f"cogs.{cog}"
        try:
            if cog_name in self.bot.extensions:
                await self.bot.reload_extension(cog_name)
                await ctx.send(f"✅ Successfully reloaded `{cog}` cog.")
            else:
                await self.bot.load_extension(cog_name)
                await ctx.send(f"✅ Loaded `{cog}` cog.")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{cog}`:\n```py\n{e}\n```")

    @commands.command(aliases=['restart'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Restart the bot"""
        await ctx.send("🔄 Restarting bot...")
        await self.bot.close()
        # This will trigger restart if you're using a process manager (like pm2, systemd, etc.)
        # Or you can use os.execv if running directly
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        """Load a cog"""
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Loaded cog: `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to load `{cog}`:\n```{e}```")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        """Unload a cog"""
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Unloaded cog: `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload `{cog}`:\n```{e}```")

    @commands.command()
    @commands.is_owner()
    async def listcogs(self, ctx):
        """List all loaded cogs"""
        cogs = [cog for cog in self.bot.extensions]
        embed = discord.Embed(title="Loaded Cogs", color=0x2F2F2F)
        embed.description = "\n".join(f"`{cog}`" for cog in cogs) or "No cogs loaded."
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Owner(bot))