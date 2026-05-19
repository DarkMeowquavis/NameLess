import discord
from discord.ext import commands
import yt_dlp
import asyncio
from discord.ui import View, Button

class MusicController(View):
    def __init__(self, ctx, music_cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music_cog = music_cog

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.voice or not self.ctx.voice_client:
            await interaction.response.send_message("❌ You must be in a voice channel.", ephemeral=True)
            return False
        if interaction.user.voice.channel != self.ctx.voice_client.channel:
            await interaction.response.send_message("❌ You must be in the same voice channel.", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="<a:Music_Playing:1506194424592466002>", label="Resume", style=discord.ButtonStyle.green, row=0)
    async def resume(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client and self.ctx.voice_client.is_paused():
            self.ctx.voice_client.resume()
            await interaction.response.send_message("<a:Animated_Verified:1506135122070605896> **Resumed**", ephemeral=True)

    @discord.ui.button(emoji="<a:Pause:1506194427050332160>", label="Pause", style=discord.ButtonStyle.gray, row=0)
    async def pause(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.ctx.voice_client.pause()
            await interaction.response.send_message("<a:status_offline_animated2:1506135434550579293> **Paused**", ephemeral=True)

    @discord.ui.button(emoji="<a:skip:1506194429000552488>", label="Skip", style=discord.ButtonStyle.blurple, row=0)
    async def skip(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            await interaction.response.send_message("⏭️ **Skipped**", ephemeral=True)

    @discord.ui.button(emoji="<a:YTH_alertanimated:1506135262139256904>", label="Stop", style=discord.ButtonStyle.red, row=1)
    async def stop(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client:
            await self.ctx.voice_client.disconnect()
            self.music_cog.queue[interaction.guild_id] = []
            await interaction.response.send_message("<a:YTH_alertanimated:1506135262139256904> **Stopped & Disconnected**", ephemeral=True)
            self.stop()

    @discord.ui.button(emoji="<a:in_queue:1506194417667674227>", label="Queue", style=discord.ButtonStyle.gray, row=1)
    async def show_queue(self, interaction: discord.Interaction, button: Button):
        await self.music_cog.queue(interaction)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.now_playing = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queue:
            self.queue[guild_id] = []
        return self.queue[guild_id]

    @commands.command()
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("❌ Join a voice channel first.")

        # Nice searching embed
        embed = discord.Embed(
            title="<a:Royalrole:1506135213426868336> Searching the Abyss...",
            description=f"**{query}**",
            color=0x2F2F2F
        )
        msg = await ctx.send(embed=embed)

        YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}" if not query.startswith("http") else query, download=False)
            
            if 'entries' in info:
                info = info['entries'][0]

            url = info['url']
            title = info.get('title', 'Unknown Song')

            self.get_queue(ctx.guild.id).append((url, title))

            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                await self.play_next(ctx)
            else:
                await msg.edit(content=f"✅ **{title}** added to queue.")
        except:
            await msg.edit(content="❌ Could not find that song.")

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return await ctx.send("**The playlist has reached its end.**")

        url, title = queue.pop(0)
        self.now_playing[ctx.guild.id] = title

        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)

        ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))

        # Beautiful Now Playing embed
        embed = discord.Embed(
            title="<a:Music_Playing:1506194424592466002> Now Playing",
            description=f"**{title}**",
            color=0x8B0000
        )
        embed.set_footer(text=f"Requested by {ctx.author} • Johan Liebert Theme")

        view = MusicController(ctx, self)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    async def queue(self, ctx):
        q = self.get_queue(ctx.guild.id)
        if not q:
            return await ctx.send("**Queue is empty.**")
        
        msg = "**Current Queue:**\n"
        for i, (_, title) in enumerate(q[:10], 1):
            msg += f"`{i}.` {title}\n"
        await ctx.send(msg)

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ **Skipped**")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue[ctx.guild.id] = []
            await ctx.send("<a:YTH_alertanimated:1506135262139256904> **Stopped & Disconnected**")

async def setup(bot):
    await bot.add_cog(Music(bot))