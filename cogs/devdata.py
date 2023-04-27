from discord.ext import commands
from discord import app_commands
import discord
from easy_sqlite3 import *
from helpers import Var as V

Var = V()


class DevData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.has_any_role(Var.liberator_role)
    @app_commands.command(name="export", description="[DEVS] Export data")
    @app_commands.choices(
        data=[
            app_commands.Choice(name="Purmarill Data", value=1),
            app_commands.Choice(name="Mystery Box Data", value=2),
            app_commands.Choice(name="Levels Data", value=3),
        ]
    )
    async def export(self, interaction, data: int):
        await interaction.response.defer()

        if data == 1:
            db = Database("./data/data")
            data = db.select("users")

            db.close()

        await interaction.followup.send("Command not ready yet :/")


async def setup(bot):
    await bot.add_cog(DevData(bot))
