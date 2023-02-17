import discord
from discord.ext import commands
from discord import ui

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

    async def setup_collaborations(self, interaction: discord.interaction, channel: discord.TextChannel):
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
            role = await self.bot.guild.fetch_roles(Var.white_realm_space_role)
            await interaction.user.add_roles(role)
            # embed = discord.Embed(color=Var.base_color)

            # await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(
                description='Unfortunately, you are not eligible to claim the "White Realm Space” role.'
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def check_(self, user_id: int) -> bool:
        pass  # Rayan TODO
