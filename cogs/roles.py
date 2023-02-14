import discord
from discord import ui
from discord import app_commands
from discord.ext import commands

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

    # @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup", description="[MODS] Setup explorill role interface")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        embed = discord.Embed(
            title='Click the button to get your Explorill role', color=Var.base_color)

        await channel.send(embed=embed, view=self.view)

        return

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-purmarill", description="Setup the Purmarill Interface in the specified channel")
    async def setup_purmarill(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(
            title='Click the button to get your Purmarill role', color=Var.base_color)

        # Sending message
        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(f"Added `get prumarill` app, to <#{channel.id}>")

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


class Purmarill(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.view = ui.View(timeout=None)

        button = ui.Button(
            label="Get Purmarill", style=discord.ButtonStyle.green, custom_id="purmarill:green")
        button.callback = self.give_purmarill

        self.view.add_item(button)

    async def give_purmarill(self):
        pass


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
