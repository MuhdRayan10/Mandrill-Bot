import discord
from discord.ext import commands

# Cog class
class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # persistance views

    # Syncing new commands
    @commands.command()
    async def sync(self, ctx):
        fmt = await ctx.bot.tree.sync() 
        await ctx.send(f"Synced {len(fmt)} commands.")

async def setup(bot):
    await bot.add_cog(Misc(bot))