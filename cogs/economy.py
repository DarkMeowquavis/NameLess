import discord
from discord.ext import commands
import random
import time
from .database import get_db

class Economy(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    async def add_coins(self, user_id: int, amount: int):
        db = await get_db()
        await db.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (user_id,))
        await db.execute("UPDATE players SET void_coins = void_coins + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()
        await db.close()

    # ==================== BASIC COMMANDS ====================

    @commands.command()
    async def balance(self, ctx):
        db = await get_db()
        async with db.execute("SELECT void_coins FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        await db.close()
       
        coins = row[0] if row else 0
        embed = discord.Embed(
            title="<a:Royalrole:1506135213426868336> Void Balance",
            description=f"<a:Shiney_Gold_Coins_Inv:1506135220322177044> **{coins:,}** Void Coins",
            color=0x2F2F2F
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text="“The only thing humans are equal in is death.” — Johan Liebert")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 12*3600, commands.BucketType.user)
    async def daily(self, ctx):
        db = await get_db()
        async with db.execute("SELECT last_daily FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        await db.close()
        current_time = int(time.time())
        if row and row[0]:
            time_left = (row[0] + 12*3600) - current_time
            if time_left > 0:
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                embed = discord.Embed(
                    title="<a:status_offline_animated2:1506135434550579293> Daily Already Claimed",
                    description=f"You can use `+daily` again in **{hours}h {minutes}m**.",
                    color=0x2F2F2F
                )
                return await ctx.send(embed=embed)
        amount = random.randint(250, 550)
        await self.add_coins(ctx.author.id, amount)
       
        embed = discord.Embed(
            title="<a:Animated_Verified:1506135122070605896> Daily Void Gift",
            description=f"<a:Shiney_Gold_Coins_Inv:1506135220322177044> You received **{amount}** Void Coins.",
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def work(self, ctx):
        earnings = random.randint(120, 320)
        await self.add_coins(ctx.author.id, earnings)
       
        embed = discord.Embed(
            title="<a:Animated_Verified:1506135122070605896> Work Complete",
            description=f"<a:Shiney_Gold_Coins_Inv:1506135220322177044> You earned **{earnings}** Void Coins.",
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def beg(self, ctx):
        if random.random() < 0.35:
            embed = discord.Embed(
                title="<a:status_offline_animated2:1506135434550579293> Beg Failed",
                description="No one gave you anything... how pathetic.",
                color=0x2F2F2F
            )
            return await ctx.send(embed=embed)
       
        amount = random.randint(30, 110)
        await self.add_coins(ctx.author.id, amount)
       
        embed = discord.Embed(
            title="<a:Animated_Verified:1506135122070605896> Beg Successful",
            description=f"<a:Shiney_Gold_Coins_Inv:1506135220322177044> Someone gave you **{amount}** Void Coins.",
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

    # ==================== GAMBLING ====================
    @commands.command(aliases=['cointoss'])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def coinflip(self, ctx, amount: int, side: str = None):
        if amount < 50:
            return await ctx.send("❌ Minimum bet is **50** Void Coins.")
        db = await get_db()
        async with db.execute("SELECT void_coins FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        await db.close()
        if not row or row[0] < amount:
            return await ctx.send("❌ Not enough Void Coins.")
        await self.add_coins(ctx.author.id, -amount)
        result = random.choice(["Heads", "Tails"])
        if side:
            choice = "Heads" if side.lower().startswith('h') else "Tails"
            won = (choice == result)
        else:
            won = random.random() < 0.5
            choice = None
        if won:
            winnings = amount * 2
            await self.add_coins(ctx.author.id, winnings)
            embed = discord.Embed(
                title="🎰 Coin Toss",
                description=f"**Result:** {result}\n" + (f"You chose **{choice}**\n" if choice else "") + f"\n<a:Shiney_Gold_Coins_Inv:1506135220322177044> **You won {winnings:,} Void Coins!**",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="🎰 Coin Toss",
                description=f"**Result:** {result}\n" + (f"You chose **{choice}**\n" if choice else "") + f"\n<a:Shiney_Gold_Coins_Inv:1506135220322177044> **You lost {amount:,} Void Coins...**",
                color=0xff0000
            )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def slots(self, ctx, amount: int = 100):
        if amount < 50:
            return await ctx.send("❌ Minimum bet is **50** Void Coins.")
        db = await get_db()
        async with db.execute("SELECT void_coins FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        await db.close()
        if not row or row[0] < amount:
            return await ctx.send("❌ Not enough Void Coins.")
        await self.add_coins(ctx.author.id, -amount)
        symbols = ["🖤", "💀", "👁️", "🌹", "🔪", "⚰️"]
        a, b, c = random.choice(symbols), random.choice(symbols), random.choice(symbols)
        embed = discord.Embed(title="<a:AnimatedSaberPeepo02:1506135143230865509> VOID SLOTS", color=0x2F2F2F)
        embed.add_field(name="Result", value=f"{a} | {b} | {c}", inline=False)
        if a == b == c:
            winnings = amount * 8
            await self.add_coins(ctx.author.id, winnings)
            embed.description = f"**JACKPOT!** <a:Shiney_Gold_Coins_Inv:1506135220322177044> You won **{winnings:,}** Void Coins!"
            embed.color = 0xffd700
        elif len(set([a, b, c])) == 2:
            winnings = int(amount * 2.5)
            await self.add_coins(ctx.author.id, winnings)
            embed.description = f"Good win! <a:Shiney_Gold_Coins_Inv:1506135220322177044> You received **{winnings:,}** Void Coins."
        else:
            embed.description = "<a:Shiney_Gold_Coins_Inv:1506135220322177044> Better luck next time..."
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def roulette(self, ctx, amount: int, choice: str = None):
        if amount < 100:
            return await ctx.send("❌ Minimum bet is **100** Void Coins.")
        db = await get_db()
        async with db.execute("SELECT void_coins FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        await db.close()
        if not row or row[0] < amount:
            return await ctx.send("❌ Not enough Void Coins.")
        await self.add_coins(ctx.author.id, -amount)
        roll = random.randint(0, 36)
        if roll == 0:
            result = "green"
            multiplier = 14
        elif roll % 2 == 0:
            result = "black"
            multiplier = 2
        else:
            result = "red"
            multiplier = 2
        win = choice and choice.lower() == result if choice else False
        if win or (not choice and result != "green"):
            winnings = amount * multiplier
            await self.add_coins(ctx.author.id, winnings)
            embed = discord.Embed(
                title=f"<a:robux:1506135204270706818> Roulette",
                description=f"**Result:** {result.upper()}\n\n<a:Shiney_Gold_Coins_Inv:1506135220322177044> **You won {winnings:,} Void Coins!**",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title=f"<a:robux:1506135204270706818> Roulette",
                description=f"**Result:** {result.upper()}\n\n<a:YTH_alertanimated:1506135262139256904> **You lost {amount:,} Void Coins...**",
                color=0xff0000
            )
        embed.set_footer(text="Johan Liebert Theme")
        await ctx.send(embed=embed)

    # ==================== CRIME ====================
    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def pickpocket(self, ctx, member: discord.Member):
        if member == ctx.author:
            return await ctx.send("❌ Can't pickpocket yourself.")
        success = random.random() < 0.78
        if success:
            amount = random.randint(40, 150)
            await self.add_coins(ctx.author.id, amount)
            embed = discord.Embed(
                title=f"<a:animatedamongusvent:1506135126336077974> Pickpocket Success",
                description=f"You stole **{amount:,}** Void Coins!",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title=f"<a:animatedamongusvent:1506135126336077974> Pickpocket Failed",
                description="You got nothing this time...",
                color=0xff0000
            )
        await ctx.send(embed=embed)

    # ==================== OWNER COMMAND (Add Coins) ====================
    @commands.command(aliases=['addcoins', 'givecoins', 'addvoid'])
    @commands.is_owner()
    async def add_void(self, ctx, member: discord.Member, amount: int):
        """Manually add Void Coins (Owner Only)"""
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.")

        await self.add_coins(member.id, amount)

        embed = discord.Embed(
            title="<a:Shiney_Gold_Coins_Inv:1506135220322177044> Void Coins Added",
            description=f"✅ Successfully added **{amount:,}** Void Coins to {member.mention}",
            color=0x00ff00
        )
        embed.set_footer(text=f"Added by {ctx.author}")
        await ctx.send(embed=embed)

    # ==================== COOLDOWN HANDLER ====================
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = round(error.retry_after)
            if seconds >= 3600:
                time_str = f"{seconds//3600}h {(seconds%3600)//60}m"
            elif seconds >= 60:
                time_str = f"{seconds//60}m {seconds%60}s"
            else:
                time_str = f"{seconds}s"
            embed = discord.Embed(
                title="<a:status_offline_animated2:1506135434550579293> Command on Cooldown",
                description=f"You can use this command again in **{time_str}**.",
                color=0x2F2F2F
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))