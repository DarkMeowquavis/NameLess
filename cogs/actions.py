import discord
from discord.ext import commands
from discord.ui import View, Button
import random

class ActionView(View):
    def __init__(self, author: discord.Member, target: discord.Member, action_key: str):
        super().__init__(timeout=180)
        self.author = author
        self.target = target
        self.action_key = action_key

    @discord.ui.button(label="Do it Back", style=discord.ButtonStyle.gray, emoji="🔄")
    async def back_action(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("❌ Only the target can do it back!", ephemeral=True)

        # Disable the button after use
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            f"🔄 {self.target.mention} did it back to {self.author.mention}!",
            embed=interaction.message.embeds[0]
        )

class Actions(commands.Cog, name="Actions"):
    def __init__(self, bot):
        self.bot = bot

    gifs = {
        "hug": ["https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGdwenJoaDdlMDJ2bGMxOGlxMDRldmg5MDY3a2o3ZGpieWZhdnF2bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/EvYHHSntaIl5m/giphy.gif", "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWc2b281ZWcxbDVjYzh3ZDlzbDQ2aXlzNmU3NnNoMnNoaWVqcHlkdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gl8ymnpv4Sqha/giphy.gif"],
        "pat": ["https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm03dnBqb2l5eHB5aWRja3RldDBseDdqM2Juc3B0dGF0djhtaGUxbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/X42IAaDJ42pHqPllGk/giphy.gif", "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExc20zeHpnY3c2dzhva3I2eTc2cjcycTFvaXdzOWsxM3IxZzU5bHN5ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ye7OTQgwmVuVy/giphy.gif"],
        "kiss": ["https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWx4dnJocmhlMmc3dms0Mzl3d2Nzb2g0c3c4eTgxYzJvcmJ0emwxZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/vX1C2TejT6OCOz2kLd/giphy.gif", "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjQ2dWd2MzRrOW1mOWhnZG5hNHdycG0zZXRocnVhamYzbTd2bzJ2eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Lx8z9ra4yYgtEDb7gq/giphy.gif"],
        "slap": ["https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm00MDgyZ3N0NWJoc2F3cHc5YmcycmxhemJvY2V2M3oxMGlndmViNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jauNHUg3yB9ZmDtzOv/giphy.gif", "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGQzMHVtOGdxMjVrNWp5cTJ2cmo2MDZqdDd2dDYxYW5tbDlsYmlnOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Wy6tit6VeXBraTQNhC/giphy.gif"],
        "cry": ["https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2wzYnZoOGVqOWUwdTVzdzdjOWJjMnRtYnJtN3UyMW42YmdzeGc2bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hppWdK8gcmzXq/giphy.gif", "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXR4YXJoemxkdXN2dmxpdzk0NTM4czBleHBlbTJ0ajlsanU4bTR4dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PMNhDAGlxHbXj5VSUL/giphy.gif"],
        "bite": ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTZ4aWZqdmRhOTZpZGJwdWttc2FvYzVicGRoZ3g0bHJiMjN1c2lkZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LO9Y9hKLupIwko9IVd/giphy.gif", "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExeHJhOTNoeDdxeXFpOGU1NDA3M3h5eGN5aG5tNGl4anQ3MjZ3Zm52YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ixoMvaJ2NhFgouq9aY/giphy.gif"],
        "kill": ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdHk3a3VhZjRia2pmdTVwZjFqbjh6amtlemppbG94YzBwM21kMzVodyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/CiZB6WIjaoXYc/giphy.gif", "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnpybHJreWFqaG5vY3RwMG5xYzdnY2I5N3Fha2syaTdzeHV3OGJrZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oEduSQonFIXK55aQo/giphy.gif"],
        "stab": ["https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTB6OWJqNm1rNmgzMXN5enFxdDN1ZHJ4cjJ6aDRvMTJ5cWFlbWloNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Wmre9vn9QwEkqV5KcS/giphy.gif", "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWRtMzh0bGowaW5pbTBrZG41cGphdjJ3bWt0cmZwcTJpMzVoanBmaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eMi2sQKZDggWhNByIv/giphy.gif"],
        "poke": ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTh1cDR0NmQwbHJmeDZuZWQ3OGQxMnRyaDhqcXNoeDdjMmRwaGw0bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/aZSMD7CpgU4Za/giphy.gif", "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGgxYTVzcnVwa2FyYzN4NDIwaXE0cThsdjJtZmQ1ODVjYnNxZGRueCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PkR8gPgc2mDlrMSgtu/giphy.gif"],
        "cuddle": ["https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmJoeW5id2tqa3Qxd2FxajY1ejF5ZnVkOHVlODdya3hhaDQyaXcyNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Shkbr6iDNznoY/giphy.gif", "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzc2dThvaWNlajR3dzNmOWNzNHk3dDk5aGpwa3o2ODU2OTMzaDdyNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/h4BprYiFYNxRe/giphy.gif"],
        "holdhand": ["https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDBvOW4ybWltZnhzdGl5NDBkYmUwdmk5dWdza2o5OGY0NTllMm1kaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KGw8FDgFPZhZAxYkZI/giphy.gif", "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2F0cWNoMXR0M3Z6NnZ5bDNtampkaHdteGtwcTA1anhobnV6c3NhYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/103WhAXlgpScG4/giphy.gif"],
        "blush": ["https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTBocGtxOHl2aHc2ZXAycm11ZTMxNHp3ZTU3bDNsc3A2MXljNmh2ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/aCSURh6OnUyXdOuYcq/giphy.gif", "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmN2YWRjdWIzYXZpdjJ3eHdtYjl6cHVoY3dxaXN1OTlzNzk5NnF4cSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QCQxhJALgRF9S/giphy.gif"],
        "angry": ["https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXl6eWU0cjZqbTBxdTFhNWgxYzljaHFnYWd1Ynh4bzE5cmdiYWR2MSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/11tTNkNy1SdXGg/giphy.gif", "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjN4aHh4d3cwNmE0OXZkbnU4Nmt2czd5OG0yOHJ5b2gzNWJ1bHZuMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/vHcCevWbWkzwk/giphy.gif"],
        "laugh": ["https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTdscjR0c2FpYTYxMTU2MTNqYThib2gxaW1jZmlxeWtyYm11a21yZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2g6sCTsSoVuSfSxK4W/giphy.gif", "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjI2Zm1rZThzNXJxaDMxdHZxenB0YXljdXozcnRxbDAxNWpqZGFobiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZqlvCTNHpqrio/giphy.gif"],
        "wave": ["https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTB5OWN0d3Rzbzh0ejAzODYyNHQwdHdpcHowejFnanQ1bXcxa3l6OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/brsEO1JayBVja/giphy.gif", "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWE3anFiY25lOW03dXRsdTVldmczeDEzM3ptbDJlY2d3NHVxeDVxeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XGhTPVMgzLv7s2TOE6/giphy.gif"]
    }

    def get_gif(self, key: str):
        return random.choice(self.gifs.get(key, ["https://media.giphy.com/media/3o7z7z7z7z7z7z7z7/giphy.gif"]))

    async def send_action(self, ctx, member, key: str, title: str, verb: str, emoji: str = "", has_button: bool = False):
        if not member and key not in ["cry", "laugh", "blush", "angry", "wave"]:
            return await ctx.send(f"**Who do you want to {key}?**")
        
        if member == ctx.author and key not in ["cry", "laugh", "blush", "angry"]:
            return await ctx.send("**You can't do that to yourself...**")

        embed = discord.Embed(
            title=f"{emoji} {title}",
            description=f"{ctx.author.mention} {verb} {member.mention if member else ''}",
            color=0x2F2F2F
        )
        embed.set_image(url=self.get_gif(key))
        embed.set_footer(text="“Even monsters feel something...” — Johan Liebert")

        if has_button and member:
            view = ActionView(ctx.author, member, key)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(embed=embed)

    # ==================== COMMANDS ====================
    @commands.command()
    async def hug(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "hug", "🤗 Hug", "hugged", "🤗", has_button=True)

    @commands.command()
    async def cuddle(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "cuddle", "🫂 Cuddle", "cuddled", "🫂", has_button=True)

    @commands.command()
    async def kiss(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "kiss", "💋 Kiss", "kissed", "💋")

    @commands.command()
    async def kill(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "kill", "☠️ Kill", "killed", "☠️", has_button=True)

    @commands.command()
    async def stab(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "stab", "🔪 Stab", "stabbed", "🔪", has_button=True)

    @commands.command()
    async def pat(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "pat", "✋ Head Pat", "patted", "✋")

    @commands.command()
    async def slap(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "slap", "👋 Slap", "slapped", "👋")

    @commands.command()
    async def poke(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "poke", "👉 Poke", "poked", "👉")

    @commands.command()
    async def holdhand(self, ctx, member: discord.Member = None):
        await self.send_action(ctx, member, "holdhand", "🤝 Hold Hands", "held hands with", "🤝", has_button=True)

    @commands.command()
    async def blush(self, ctx):
        await self.send_action(ctx, None, "blush", "😊 Blush", "is blushing", "😊")

    @commands.command()
    async def angry(self, ctx):
        await self.send_action(ctx, None, "angry", "😠 Angry", "is angry", "😠")

    @commands.command()
    async def laugh(self, ctx):
        await self.send_action(ctx, None, "laugh", "😂 Laugh", "is laughing", "😂")

    @commands.command()
    async def cry(self, ctx):
        await self.send_action(ctx, None, "cry", "😭 Cry", "is crying", "😭")

    @commands.command()
    async def wave(self, ctx):
        await self.send_action(ctx, None, "wave", "👋 Wave", "waved", "👋")

async def setup(bot):
    await bot.add_cog(Actions(bot))