import discord
from discord.ext import commands
from discord.ui import View, Button
from .database import get_db

class LeaderboardView(View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        self.current_page = "wealth"

    def format_voice_time(self, seconds: int):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    async def get_leaderboard(self, category: str):
        db = await get_db()
        title_emoji = "<a:Royalrole:1506135213426868336>"
        
        if category == "wealth":
            async with db.execute("SELECT user_id, void_coins FROM players ORDER BY void_coins DESC LIMIT 10") as cur:
                rows = await cur.fetchall()
            title = f"{title_emoji} Wealth Leaderboard"
            emoji = "<a:Shiney_Gold_Coins_Inv:1506135220322177044>"

        elif category == "level":
            async with db.execute("SELECT user_id, level, xp FROM players ORDER BY level DESC, xp DESC LIMIT 10") as cur:
                rows = await cur.fetchall()
            title = f"{title_emoji} Level Leaderboard"
            emoji = "<a:up_level_up:1506202017088012318>"

        elif category == "hunter":
            async with db.execute("SELECT user_id, wins FROM players ORDER BY wins DESC LIMIT 10") as cur:
                rows = await cur.fetchall()
            title = f"{title_emoji} Hunter Leaderboard"
            emoji = "<a:cat_gun:1506202437365792868>"

        elif category == "voice":
            async with db.execute("SELECT user_id, voice_time FROM players ORDER BY voice_time DESC LIMIT 10") as cur:
                rows = await cur.fetchall()
            title = f"{title_emoji} Voice Time Leaderboard"
            emoji = "<a:VOICE:1506202659336622160>"

        elif category == "messages":
            async with db.execute("SELECT user_id, messages_sent FROM players ORDER BY messages_sent DESC LIMIT 10") as cur:
                rows = await cur.fetchall()
            title = f"{title_emoji} Messages Leaderboard"
            emoji = "<a:levelling:1506202014533550153>"

        else:  # overall
            async with db.execute("""
                SELECT user_id, void_coins, level, wins, voice_time, messages_sent 
                FROM players 
                ORDER BY (void_coins + level*300 + wins*50 + voice_time/3600 + messages_sent/100) DESC LIMIT 10
            """) as cur:
                rows = await cur.fetchall()
            title = f"{title_emoji} Overall Leaderboard"
            emoji = "<a:slayer_sparkle_diamond:1506135228576432231>"

        await db.close()
        return title, emoji, rows

    def get_user(self, user_id):
        user = self.bot.get_user(user_id)
        return user.display_name if user else f"Unknown ({user_id})"

    # Buttons with better colors
    @discord.ui.button(label="Wealth", emoji="<a:Shiney_Gold_Coins_Inv:1506135220322177044>", style=discord.ButtonStyle.green, row=0)
    async def wealth_btn(self, interaction: discord.Interaction, button: Button):
        await self.switch_page(interaction, "wealth")

    @discord.ui.button(label="Level", emoji="<a:up_level_up:1506202017088012318>", style=discord.ButtonStyle.gray, row=0)
    async def level_btn(self, interaction: discord.Interaction, button: Button):
        await self.switch_page(interaction, "level")

    @discord.ui.button(label="Hunter", emoji="<a:cat_gun:1506202437365792868>", style=discord.ButtonStyle.gray, row=0)
    async def hunter_btn(self, interaction: discord.Interaction, button: Button):
        await self.switch_page(interaction, "hunter")

    @discord.ui.button(label="Voice", emoji="<a:VOICE:1506202659336622160>", style=discord.ButtonStyle.blurple, row=1)
    async def voice_btn(self, interaction: discord.Interaction, button: Button):
        await self.switch_page(interaction, "voice")

    @discord.ui.button(label="Messages", emoji="<a:levelling:1506202014533550153>", style=discord.ButtonStyle.gray, row=1)
    async def messages_btn(self, interaction: discord.Interaction, button: Button):
        await self.switch_page(interaction, "messages")

    @discord.ui.button(label="Overall", emoji="<a:slayer_sparkle_diamond:1506135228576432231>", style=discord.ButtonStyle.red, row=1)
    async def overall_btn(self, interaction: discord.Interaction, button: Button):
        await self.switch_page(interaction, "overall")

    async def switch_page(self, interaction: discord.Interaction, category: str):
        self.current_page = category
        title, emoji, rows = await self.get_leaderboard(category)
        
        embed = discord.Embed(title=title, color=0x2F2F2F)
        embed.set_footer(text="NameLessBot • Johan Liebert Theme")

        for i, row in enumerate(rows, 1):
            user_name = self.get_user(row[0])
            
            if category == "wealth":
                value = f"{row[1]:,} Void Coins"
            elif category == "level":
                value = f"Level **{row[1]}**"
            elif category == "hunter":
                value = f"**{row[1]}** Wins"
            elif category == "voice":
                value = self.format_voice_time(row[1])
            elif category == "messages":
                value = f"**{row[1]:,}** messages"
            else:
                value = "Combined Power"

            embed.add_field(
                name=f"`#{i:02d}` {emoji} {user_name}",
                value=value,
                inline=False
            )

        await interaction.response.edit_message(embed=embed, view=self)


class Leaderboard(commands.Cog, name="Leaderboard"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['lb', 'top'])
    async def leaderboard(self, ctx):
        view = LeaderboardView(self.bot)
        title, emoji, rows = await view.get_leaderboard("wealth")
        
        embed = discord.Embed(title=title, color=0x2F2F2F)
        embed.set_footer(text="NameLessBot • Johan Liebert Theme")

        for i, row in enumerate(rows, 1):
            user_name = view.get_user(row[0])
            embed.add_field(
                name=f"`#{i:02d}` <a:Shiney_Gold_Coins_Inv:1506135220322177044> {user_name}",
                value=f"{row[1]:,} Void Coins",
                inline=False
            )

        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))