from discord.ext import commands
from discord import app_commands
from helpers import Var as V
import discord

Var = V()

class Genesis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        genesis_btn = discord.ui.Button(label="Get Genesis!", style=discord.ButtonStyle.blurple, custom_id="genesis:green")
        genesis_btn.callback = self.genesis_callback

        self.views = discord.ui.View(timeout=None)
        self.views.add_item(genesis_btn)

    @app_commands.checks.has_any_role(Var.liberator_role, Var.guardrill_role)
    @app_commands.command(name="setup-genesis", description="[MODS] Setup Genesis embed")
    async def setup_genesis(self, interaction, channel:discord.TextChannel):
        await interaction.response.send_message(f"Sending in {channel.mention}", ephemeral=True)

        embed = discord.Embed(title="Click the button to get your Genesis role", color=Var.base_color)

        await channel.send(embed=embed, view=self.views)
        
    async def genesis_callback(self, interaction):
        await interaction.response.send_message(embed=discord.Embed(title="Verifying Genesis role soon will be available", color=Var.base_color),
                                                ephemeral=True)


async def setup(bot):
    await bot.add_cog(Genesis(bot))