import discord
from discord.ext import commands
from discord import ui, app_commands

from easy_sqlite3 import *
import csv

from helpers import Var as V, check_in_csv

Var = V()


class WhiteRealmSpaceModal(ui.Modal, title="White Realm Space"):
    wallet_id = ui.TextInput(
        label="Wallet Address",
        placeholder="Enter your FLR wallet address",
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bool_ = check_in_csv(
            str(self.wallet_id).lower(), "./data/white_realm_holders.csv", 0
        )
        print(bool_, self.wallet_id)
        if bool_:
            role = interaction.guild.get_role(Var.white_realm_space_role)

            await interaction.user.add_roles(role)
            embed = discord.Embed(
                description="Congratulations! Now you have White Realm Space role!",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            embed = discord.Embed(
                description="Unfortunately, you are not eligible to get White Realm Space role.",
                color=Var.base_color,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


class ClubXModal(ui.Modal, title="Extremely Bullish"):
    wallet_id = ui.TextInput(
        label="Wallet Address",
        placeholder="Enter your XRPL wallet address",
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bool_ = check_in_csv(str(self.wallet_id).lower(), "./data/clubx.csv", 0)
        print(bool_, self.wallet_id)
        if bool_:
            role = interaction.guild.get_role(Var.clubx_role)

            await interaction.user.add_roles(role)
            embed = discord.Embed(
                description="Congratulations! Now you have the Extremely Bullish role!",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            embed = discord.Embed(
                description="Unfortunately, you are not eligible to get the Extremely Bullish role.",
                color=Var.base_color,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


class FatCats(ui.Modal, title="The Fat Cats Gallery"):
    wallet_id = ui.TextInput(
        label="Wallet Address",
        placeholder="Enter your FLR wallet address",
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bool_ = check_in_csv(
            str(self.wallet_id).lower(),
            [f"./data/fatcats/{i}.csv" for i in range(3)],
            1,
        )

        print(bool_, self.wallet_id)
        if bool_:
            role = interaction.guild.get_role(1082038353370820788)

            await interaction.user.add_roles(role)
            embed = discord.Embed(
                description="Congratulations! Now you have the Fat Cats role!",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            embed = discord.Embed(
                description="Unfortunately, you are not eligible to get the Fat Cats role.",
                color=Var.base_color,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


class SuperBadSeriesModal(ui.Modal, title="Genisis Seed Capsule"):
    wallet_id = ui.TextInput(
        label="Wallet Address",
        placeholder="Enter your FLR wallet address",
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bool_ = check_in_csv(str(self.wallet_id), "./data/sss.csv", 1)
        if bool_:
            role = interaction.guild.get_role(Var.genesis_speed_capsule)

            await interaction.user.add_roles(role)
            embed = discord.Embed(
                description="Congratulations! Now you have Genesis Seed Capsule role!",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            embed = discord.Embed(
                description="Unfortunately, you are not eligible to get Genesis Seed Capsule role.",
                color=Var.base_color,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


class Collaborations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        white_realm_space_btn = ui.Button(
            label="Get It!",
            style=discord.ButtonStyle.green,
            custom_id="collaborations:white_realm_space",
        )

        white_realm_space_btn.callback = self.white_realm_space_btn_callback

        self.views = ui.View(timeout=None)
        self.views.add_item(white_realm_space_btn)

        genisis_capsule_btn = ui.Button(
            label="Get It!",
            style=discord.ButtonStyle.green,
            custom_id="collaborations:genisis_capsule",
        )
        genisis_capsule_btn.callback = self.genisis_capsule_btn_callback

        self.view2 = ui.View(timeout=None)
        self.view2.add_item(genisis_capsule_btn)

        clubx_btn = ui.Button(
            label="Get It!",
            style=discord.ButtonStyle.green,
            custom_id="collaborations:clubx",
        )
        clubx_btn.callback = self.clubx_btn_callback

        self.view3 = ui.View(timeout=None)
        self.view3.add_item(clubx_btn)

        fatcats = ui.Button(
            label="Get It!",
            style=discord.ButtonStyle.green,
            custom_id="collaborations:fatcats",
        )
        fatcats.callback = self.fatcats_callback

        self.view4 = ui.View(timeout=None)
        self.view4.add_item(fatcats)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(
        name="setup-888innercircle",
        description="Setup the 888innercircle Interface in the specified channel",
    )
    async def setup_collaborations(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        embed = discord.Embed(
            title="Claim your White Realm Space role!", color=Var.base_color
        )

        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(
            f"Added `partnerships` app, to <#{channel.id}>", ephemeral=True
        )

    async def white_realm_space_btn_callback(self, interaction: discord.Interaction):
        role = interaction.user.get_role(Var.white_realm_space_role)

        if role is not None:
            embed = discord.Embed(
                description="You already claimed your role, thank you for your interest.",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.send_modal(WhiteRealmSpaceModal())

    async def fatcats_callback(self, interaction: discord.Interaction):
        role = interaction.user.get_role(Var.fatcats_role)

        if role is not None:
            embed = discord.Embed(
                description="You already claimed your role, thank you for your interest.",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.send_modal(FatCats())

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="superbadseries", description="Embed for superbadseries")
    async def super_bad_series(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        embed = discord.Embed(
            title="Claim your Genesis Seed Capsule role!", color=Var.base_color
        )

        await channel.send(embed=embed, view=self.view2)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(
        name="setup-fatcats",
        description="Setup the Fat Cats Interface in the specified channel",
    )
    async def fatcats(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        embed = discord.Embed(
            title="Claim your The Fat Cats Gallery role!", color=Var.base_color
        )

        await channel.send(embed=embed, view=self.view4)
        await interaction.response.send_message(
            f"Added `partnerships` app, to <#{channel.id}>", ephemeral=True
        )

    async def genisis_capsule_btn_callback(self, interaction: discord.Interaction):
        role = interaction.user.get_role(Var.genesis_speed_capsule)

        if role is not None:
            embed = discord.Embed(
                description="You already claimed your role, thank you for your interest.",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.send_modal(SuperBadSeriesModal())

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="clubx", description="Embed for Club X")
    async def clubx(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        embed = discord.Embed(
            title="Claim your Extremely Bullish role!", color=Var.base_color
        )

        await channel.send(embed=embed, view=self.view3)

    async def clubx_btn_callback(self, interaction: discord.Interaction):
        role = interaction.user.get_role(Var.clubx_role)

        if role is not None:
            embed = discord.Embed(
                description="You already claimed your role, thank you for your interest.",
                color=Var.base_color,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.send_modal(ClubXModal())


async def setup(bot):
    await bot.add_cog(Collaborations(bot))
