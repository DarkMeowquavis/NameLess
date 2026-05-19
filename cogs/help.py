import discord
from discord.ext import commands
from discord.ui import View, Select

class HelpSelect(Select):
    def __init__(self, ctx):
        super().__init__(
            placeholder="Select a Module...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Economy", emoji="<a:Shiney_Gold_Coins_Inv:1506135220322177044>", description="Balance, Daily, Work, Beg, Gambling"),
                discord.SelectOption(label="Music", emoji="<a:Music_Playing:1506194424592466002>", description="Play, Queue, Skip, Controls"),
                discord.SelectOption(label="Hunt & Crime", emoji="<a:cat_gun:1506202437365792868>", description="Hunt, Rob, Pickpocket"),
                discord.SelectOption(label="Actions", emoji="🤗", description="Hug, Kiss, Kill, etc."),
                discord.SelectOption(label="Utility", emoji="<a:Royalrole:1506135213426868336>", description="Profile, AFK, Ping, Help"),
                discord.SelectOption(label="Owner", emoji="🔧", description="Add Void, Reload (Owner Only)"),
            ]
        )
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]

        if category == "Economy":
            embed = discord.Embed(title="<a:Shiney_Gold_Coins_Inv:1506135220322177044> Economy Commands", color=0x2F2F2F)
            embed.add_field(name="Basic", value="`balance` `daily` `work` `beg`", inline=False)
            embed.add_field(name="Gambling", value="`coinflip <amount>` `slots <amount>` `roulette <amount> [red/black/green]`", inline=False)

        elif category == "Music":
            embed = discord.Embed(title="<a:Music_Playing:1506194424592466002> Music Commands", color=0x2F2F2F)
            embed.add_field(name="Main", value="`play <song>` `join` `leave`", inline=False)
            embed.add_field(name="Control", value="`skip` `stop` `queue`", inline=False)

        elif category == "Hunt & Crime":
            embed = discord.Embed(title="<a:cat_gun:1506202437365792868> Hunt & Crime", color=0x2F2F2F)
            embed.add_field(name="Commands", value="`hunt` `rob @user` `pickpocket @user`", inline=False)

        elif category == "Actions":
            embed = discord.Embed(title="🤗 Actions", color=0x2F2F2F)
            embed.add_field(name="Commands", value="`hug` `kiss` `cuddle` `kill` `stab` `pat` `slap` `cry` `laugh`", inline=False)

        elif category == "Utility":
            embed = discord.Embed(title="<a:Royalrole:1506135213426868336> Utility", color=0x2F2F2F)
            embed.add_field(name="Commands", value="`profile` `afk <reason>` `ping`", inline=False)

        elif category == "Owner":
            embed = discord.Embed(title="🔧 Owner Commands", color=0x2F2F2F)
            embed.add_field(name="Commands", value="`add_void @user <amount>`", inline=False)

        embed.set_footer(text="NameLessBot • Johan Liebert Theme")
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(View):
    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.add_item(HelpSelect(ctx))

class Help(commands.Cog, name="Help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="<a:Royalrole:1506135213426868336> NameLessBot Help",
            description="**Johan Liebert Inspired Multipurpose Bot**\nChoose a category from the dropdown below:",
            color=0x2F2F2F
        )
        embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
        embed.set_footer(text="“The only thing all humans are equal in is death.”")

        view = HelpView(ctx)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))