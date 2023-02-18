import discord
from discord.ext import commands
from discord import ui, app_commands

from easy_sqlite3 import *
import csv

from helpers import Var as V
Var = V()


class Collaborations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        btn = ui.Button(label="Get the Role",
                        style=discord.ButtonStyle.green, custom_id="collaborations:white_realm_space")

        btn.callback = self.btn_callback

        self.views = ui.View(timeout=None)
        self.views.add_item(btn)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-888innercircle", description="Setup the Purmarill Interface in the specified channel")
    async def setup_collaborations(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title="Press the button below in order to claim your “White Realm Space” role", color=Var.base_color
        )

        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(f"Added `partnerships` app, to <#{channel.id}>", ephemeral=True)

    async def btn_callback(self, interaction: discord.Interaction):

        role = interaction.user.get_role(Var.white_realm_space_role)

        if role is not None:
            embed = discord.Embed(
                description="You already claimed your role, thank you for your interest.", color=Var.base_color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        bool_ = self.check_(interaction.user.id)
        if bool_:
            role = self.bot.guilds[0].get_role(Var.white_realm_space_role)

            await interaction.user.add_roles(role)
            embed = discord.Embed(
                description="Congratulations, now you have White Realm Space role!", color=Var.base_color)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(
                description='Unfortunately, you are not eligible to claim the "White Realm Space” role.', color=Var.base_color
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_(self, user_id: int) -> bool:
        db = Database("./data/data.db")
        data = db.select("users", where={"user": user_id}, size=1)

        if data is None:  # user has not given purmarill
            return False

        with open("./data/white_realm_holders.csv") as f:
            reader = csv.reader(f, delimiter=",")
            white_realm_holders = [str(row[0]) for row in reader]
        print(white_realm_holders)

        return True if data[3] in white_realm_holders else False


async def setup(bot):
    await bot.add_cog(Collaborations(bot))
