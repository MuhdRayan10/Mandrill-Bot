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

        white_realm_space_btn = ui.Button(label="Get It!",
                                          style=discord.ButtonStyle.green, custom_id="collaborations:white_realm_space")

        white_realm_space_btn.callback = self.white_realm_space_btn_callback

        self.views = ui.View(timeout=None)
        self.views.add_item(white_realm_space_btn)

        genisis_capsule_btn = ui.Button(
            label="Get It!", style=discord.ButtonStyle.green, custom_id="collaborations:genisis_capsule")
        genisis_capsule_btn.callback = self.genisis_capsule_btn_callback

        self.view2 = ui.View(timeout=None)
        self.view2.add_item(genisis_capsule_btn)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-888innercircle", description="Setup the 888innercircle Interface in the specified channel")
    async def setup_collaborations(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title="Claim your White Realm Space role!", color=Var.base_color
        )

        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(f"Added `partnerships` app, to <#{channel.id}>", ephemeral=True)

    async def white_realm_space_btn_callback(self, interaction: discord.Interaction):

        role = interaction.user.get_role(Var.white_realm_space_role)

        if role is not None:
            embed = discord.Embed(
                description="You already claimed your role, thank you for your interest.", color=Var.base_color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        bool_ = self.check_1(interaction.user.id)
        if bool_:
            role = self.bot.guilds[0].get_role(Var.white_realm_space_role)

            await interaction.user.add_roles(role)
            embed = discord.Embed(
                description="Congratulations! Now you have White Realm Space role!", color=Var.base_color)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(
                description='Unfortunately, you are not eligible to get White Realm Space role.', color=Var.base_color
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_1(self, user_id: int) -> bool:
        db = Database("./data/data.db")
        data = db.select("users", where={"user": user_id}, size=1)

        if data is None:  # user has not given purmarill
            return False

        with open("./data/white_realm_holders.csv") as f:
            reader = csv.reader(f, delimiter=",")
            white_realm_holders = [str(row[0]) for row in reader]
        print(white_realm_holders)

        return True if data[3] in white_realm_holders else False

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="superbadseries", description="Embed for superbadseries")
    async def super_bad_series(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(title="Claim your Genesis Seed Capsule role!")

        await channel.send(embed=embed, view=self.view2)

    async def genisis_capsule_btn_callback(self, interaction: discord.Interaction):
        role = interaction.user.get_role(Var.genesis_speed_capsule)

        if role is not None:
            embed = discord.Embed(
                description="You already claimed your role, thank you for your interest.", color=Var.base_color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        bool_ = self.check_2(interaction.user.id)
        if bool_:
            role = self.bot.guilds[0].get_role(Var.genesis_speed_capsule)

            await interaction.user.add_roles(role)
            embed = discord.Embed(
                description='Congratulations, now you have "Genesis Seed Capsule" role!', color=Var.base_color)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(
                description='Unfortunately, you are not eligible to claim the "Genesis Seed Capsule" role.', color=Var.base_color
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        def check_2(self, user_id: int):
            db = Database("./data/data.db")
            data = db.select("users", where={"user": user_id}, size=1)

            if data is None:  # user has not given purmarill
                return False

            return True  # todo


async def setup(bot):
    await bot.add_cog(Collaborations(bot))
