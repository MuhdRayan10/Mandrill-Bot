from discord.ext import commands
from discord import app_commands
import discord

class RoadMap:
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roadmap", description="View our Roadmap!")
    async def roadmap(self, interaction):
        embed = discord.Embed()

        await interaction.response.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoadMap(bot))
