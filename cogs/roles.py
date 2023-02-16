import discord
from discord import ui
from discord import app_commands
from discord.ext import commands
from easy_sqlite3 import *

from web3 import Web3
from cogs.twitter import Twitter

# global config variables
from helpers import Var
Var = Var()


class Explorill(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.view = ui.View(timeout=None)
        button = ui.Button(
            label="Get Explorill", style=discord.ButtonStyle.green, custom_id="explorill:green")
        button.callback = self.give_explorill

        self.view.add_item(button)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup", description="[MODS] Setup explorill role interface")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        embed = discord.Embed(
            title='Click the button to get your Explorill role', color=Var.base_color)

        await channel.send(embed=embed, view=self.view)
        await interaction.response.send_message(content=f"Added Explorill Interface to <#{channel.id}>.", ephemeral=True)

        return

    async def give_explorill(self, interaction: discord.Interaction):

        explorill_role = interaction.guild.get_role(Var.explorill_role)
        unverified_role = interaction.guild.get_role(Var.mute_role)

        roles = interaction.user.roles

        if unverified_role in roles:
            await interaction.response.send_message(f"Unfortunately, you are still unverified. Please verify yourself at <#{Var.verification_channel}>.", ephemeral=True)
            return

        if explorill_role in roles:
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already an `Exporill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            await interaction.user.add_roles(explorill_role)
            await interaction.response.send_message(f"You are now officially an `Explorill`!", ephemeral=True)
            await interaction.user.remove_roles(interaction.guild.get_role(Var.muted_role))

        return


def validify_wallet(wallet: str):
    """Checks if the wallet ID is a valid web3 address.\nTODO: Change to FLR Address using FLR API."""
    return Web3.isAddress(wallet)


class PurmarillVerificationModal(ui.Modal, title='Purmarill Verification'):
    twitter_username = ui.TextInput(
        label="Twitter Username",
        placeholder="Enter your twitter username (without the handle)",
        style=discord.TextStyle.short
    )
    wallet_id = ui.TextInput(
        label="Wallet Address",
        placeholder='Enter your FLR wallet address',
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:

        # Checking if twitter / walled account / user already exists db
        role = interaction.guild.get_role(Var.purmarill_role)
        if role in interaction.user.roles:
            await interaction.response.send_message("Twitter account / Wallet ID already registered...", ephemeral=True)
            return

        # check if the twitter is valid
        if not Twitter(bot=None).validify_twitter(str(self.twitter_username)):
            await interaction.response.send_message("Twitter username does not exist.", ephemeral=True)
            return

        # checks if it is a valid wallet address
        if not validify_wallet(str(self.wallet_id)):
            await interaction.response.send_message("FLR address is not valid.", ephemeral=True)
            return

        db = Database("./data/data")
        db.insert("users", (interaction.user.id, interaction.user.name, str(
            self.twitter_username), str(self.wallet_id)))
        await interaction.response.send_message("You are now officially a Purmarill!", ephemeral=True)

        await interaction.user.add_roles(role)

        db.close()


class Purmarill(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.view = ui.View(timeout=None)

        button = ui.Button(
            label="Get Purmarill", style=discord.ButtonStyle.green, custom_id="purmarill:green")
        button.callback = self.give_purmarill

        self.view.add_item(button)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup", description="[MODS] Setup purmarill role interface")
    async def setup(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(
            title='Click the button to get your Purmarill role', color=Var.base_color)

        # Sending message
        await channel.send(embed=embed, view=self.view)
        await interaction.response.send_message(content=f"Added Explorill Interface to <#{channel.id}>.", ephemeral=True)

        return

    async def give_purmarill(self, interaction: discord.Interaction):

        if interaction.user.get_role(Var.purmarill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already a `Purmarill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        elif not interaction.user.get_role(Var.explorill_role):
            embed = discord.Embed(
                title="Required Role",
                description=f"First you have to <#{Var.explorill_channel}> role to be a `Purmarill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # send modal when link is called
        await interaction.response.send_modal(PurmarillVerificationModal())


async def setup(bot):
    bot.tree.add_command(
        Explorill(
            bot=bot,
            name="explorill",
            description="Commands related to Explorill Role")
    )

    bot.tree.add_command(
        Purmarill(
            bot=bot,
            name="purmarill",
            description="Commands related to Purmarill Role"
        )
    )
