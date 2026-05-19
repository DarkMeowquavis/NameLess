import discord
from discord.ext import commands
import json
from .database import get_db

shop_items = {
    "Johan’s Scalpel": {"price": 800, "effect": "hunt_boost"},
    "Monster Mask": {"price": 1200, "effect": "rob_success"},
    "Red Rose": {"price": 500, "effect": "gift"},
    "Tenma’s Guilt": {"price": 2000, "effect": "xp_boost"},
    "Nameless Diary": {"price": 1500, "effect": "title"}
}

class Shop(commands.Cog, name="Shop"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(
            title="<:Aesthetic3:1506134013604007976> Void Shop",
            description="What will you sacrifice for power?",
            color=0x2F2F2F
        )
        
        for item, data in shop_items.items():
            embed.add_field(
                name=item,
                value=f"<a:Shiney_Gold_Coins_Inv:1506135220322177044> **{data['price']}** Void Coins",
                inline=False
            )
        
        embed.set_footer(text="Use +buy <item name>")
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, *, item_name: str):
        if item_name not in shop_items:
            embed = discord.Embed(
                title="<a:status_offline_animated2:1506135434550579293> Item Not Found",
                description="That item doesn't exist in the shop.",
                color=0x2F2F2F
            )
            return await ctx.send(embed=embed)

        price = shop_items[item_name]["price"]
        db = await get_db()
        
        async with db.execute("SELECT void_coins FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        
        if not row or row[0] < price:
            await db.close()
            embed = discord.Embed(
                title="<a:status_offline_animated2:1506135434550579293> Insufficient Funds",
                description="You don't have enough Void Coins.",
                color=0x2F2F2F
            )
            return await ctx.send(embed=embed)

        # Process purchase
        await db.execute("UPDATE players SET void_coins = void_coins - ? WHERE user_id=?", (price, ctx.author.id))
        
        async with db.execute("SELECT items FROM players WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
            inv = json.loads(row[0]) if row and row[0] else {}
        
        inv[item_name] = inv.get(item_name, 0) + 1
        await db.execute("UPDATE players SET items=? WHERE user_id=?", (json.dumps(inv), ctx.author.id))
        await db.commit()
        await db.close()

        embed = discord.Embed(
            title="<a:Animated_Verified:1506135122070605896> Purchase Successful",
            description=f"You bought **{item_name}** for <a:Shiney_Gold_Coins_Inv:1506135220322177044> **{price}** Void Coins.",
            color=0x2F2F2F
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shop(bot))