from discord.ext import commands
from discord import app_commands
import discord

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Verification(bot))
