from helpers import Var as V
import discord
from discord import ui
from discord.ext import commands, tasks
from discord import app_commands

import requests
import logging
logging.basicConfig(filename="./logs/genesis.log", filemode="w",
                    format="%(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)


Var = V()


class Genesis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        genesis_btn = discord.ui.Button(
            label="Get Genesis!", style=discord.ButtonStyle.blurple, custom_id="genesis:green")
        genesis_btn.callback = self.genesis_callback

        self.views = discord.ui.View(timeout=None)
        self.views.add_item(genesis_btn)

        self.guild = self.bot.guilds[0]
        self.role = self.guild.get_role(Var.genesis_role)

        self.check_genesis.start()

    @app_commands.checks.has_any_role(Var.liberator_role, Var.guardrill_role)
    @app_commands.command(name="setup-genesis", description="[MODS] Setup Genesis embed")
    async def setup_genesis(self, interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"Sending in {channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title="Click the button to get your Genesis role", color=Var.base_color)

        await channel.send(embed=embed, view=self.views)

    async def genesis_callback(self, interaction):

        # check if the user has the role Var.genisis_role
        if interaction.user.get_role(Var.genesis_role):
            embed = discord.Embed(title="Role already assigned", color=Var.base_color,
                                  description="Thank You for your interest!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        elif not interaction.user.get_role(Var.purmarill_role):
            embed = discord.Embed(
                title="Required Role",
                description=f"First you have to <#{Var.purmarill_channel}> role to be a `Genisis`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # redirect the user to the link
        embed = discord.Embed(
            title="Click the button to verify", color=Var.base_color)

        view = ui.View()
        btn1 = ui.Button(
            label="Connect", style=discord.ButtonStyle.green, url=f"https://www.themandrills.xyz/verify.php?discord={interaction.user.id}")
        btn = ui.Button(
            label="Get Genesis!", style=discord.ButtonStyle.blurple)
        btn.callback = self.verify_callback

        view.add_item(btn1)
        view.add_item(btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def verify_callback(self, interaction):

        bool_ = requests.get(
            url=f"https://www.themandrills.xyz/verified.php?action=getverified&discord={interaction.user.id}")
        bool_ = bool_.json()

        if not bool_:
            embed = discord.Embed(title="Genesis Role is not Assigned!", color=Var.base_color,
                                  description="Unfortunately, Blue Mineral is not found on your connected address")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            embed = discord.Embed(
                title="Now you have the Genesis role ^‿^", color=Var.base_color)
            await interaction.response.send_message(embed=embed, ephemeral=True)

            # add role to user

            await interaction.user.add_roles(self.role)

    @tasks.loop(minutes=5)
    async def check_genesis(self):
        members = self.role.members

        for member in members:
            bool_ = requests.get(
                url=f"https://www.themandrills.xyz/verified.php?action=getinfo&discord={member.id}"
            )
            bool_ = bool_.json()

            logging.debug(f"{member.id}, {member.name}, {bool_}")

            if not bool_:
                await member.remove_roles(self.role)


async def setup(bot):
    await bot.add_cog(Genesis(bot))
