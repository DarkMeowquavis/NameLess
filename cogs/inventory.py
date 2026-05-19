import discord
from discord.ext import commands
import json
import random
from .database import get_db

items = ["Johan’s Scalpel", "Red Rose from Prague", "Nameless Diary", "Monster Mask", "Tenma’s Photo", "Forgotten Experiment File"]

class Inventory(commands.Cog, name="Inventory"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['inv'])
    async def inventory(self, ctx):
        db = await get_db()
        async with db.execute("SELECT items FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        await db.close()

        if not row or row[0] == '{}':
            embed = discord.Embed(
                title="<a:status_offline_animated2:1506135434550579293> Inventory Empty",
                description="Your inventory is empty... like a monster with no name.",
                color=0x2F2F2F
            )
            return await ctx.send(embed=embed)

        items_dict = json.loads(row[0])
        desc = "\n".join([f"• **{item}** ×{qty}" for item, qty in items_dict.items()])

        embed = discord.Embed(
            title=f"<a:Minecraft_enchanted_book:1506135189556957225> {ctx.author.name}'s Inventory",
            description=desc,
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 80, commands.BucketType.user)
    async def collect(self, ctx):
        item = random.choice(items)
        db = await get_db()
        await db.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (ctx.author.id,))

        async with db.execute("SELECT items FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
            inv = json.loads(row[0]) if row and row[0] else {}

        inv[item] = inv.get(item, 0) + 1
        await db.execute("UPDATE players SET items=? WHERE user_id=?", (json.dumps(inv), ctx.author.id))
        await db.commit()
        await db.close()

        embed = discord.Embed(
            title="<a:Animated_Verified:1506135122070605896> Item Collected",
            description=f"You collected **{item}**.",
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def use(self, ctx, *, item_name: str):
        db = await get_db()
        async with db.execute("SELECT items FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        if not row:
            await db.close()
            return await ctx.send("You have nothing to use.")

        inv = json.loads(row[0])
        if item_name not in inv or inv[item_name] <= 0:
            await db.close()
            embed = discord.Embed(
                title="<a:status_offline_animated2:1506135434550579293> Item Not Found",
                description="You don't have that item.",
                color=0x2F2F2F
            )
            return await ctx.send(embed=embed)

        inv[item_name] -= 1
        if inv[item_name] == 0:
            del inv[item_name]

        await db.execute("UPDATE players SET items=? WHERE user_id=?", (json.dumps(inv), ctx.author.id))
        await db.commit()
        await db.close()

        embed = discord.Embed(
            title="<a:Animated_Verified:1506135122070605896> Item Used",
            description=f"You used **{item_name}**. Its power flows through you...",
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventory(bot))