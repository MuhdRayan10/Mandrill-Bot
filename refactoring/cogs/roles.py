import discord
from discord import ui
from discord import app_commands
from discord.ext import commands

class Explorill(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.view = ui.View(timeout=None)
        button = ui.Button(label="Get Explorill", style=discord.ButtonStyle.green, custom_id="explorill:green")
        button.callback = self.give_role

        self.view.add_item(button)

    ## @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup", description="[MODS] Setup explorill role interface")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        # embed = discord.Embed(title='Click the button to get your Explorill role', color=Var.base_color)
        embed = discord.Embed(title='Click the button to get your Explorill role')

        await channel.send(embed=embed, view=self.view)

        return
    
    async def give_role(self, interaction: discord.Interaction):
        self.bot.send("x")
        
        return

async def setup(bot):
    bot.tree.add_command(
        Explorill(
            bot=bot,
            name="explorill",
            description="Commands related to Explorill Role")
    )