from discord.ext import commands
from discord.ui import View
from discord import app_commands
import discord

from helpers import Var

# Ticket settings Interface buttons
class TicketSettings(View):
    def __init__(self):
        super().__init__(timeout=None)

    # To close the ticket and delete channel
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close(self, interaction, _):
        await interaction.response.send_message("Ticket is being closed...", ephemeral=True)
        await interaction.channel.delete()


# Ticket Creation Interface buttons
class CreateTicket(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction, _):

        await interaction.response.defer()

        msg = await interaction.followup.send(content="A ticket is being created!", ephemeral=True)
        other_role = interaction.guild.get_role(Var.guardrill_role) # Mod Role

        # What permissions to keep
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            other_role: discord.PermissionOverwrite(read_messages=True)
        }

        # Get Tickets category and create a new channel
        category = discord.utils.get(interaction.guild.categories, name='Tickets')
        channel = await interaction.guild.create_text_channel(f"[TICKET]-{interaction.user.name}",
                overwrites=overwrites, category=category)

        await interaction.followup.edit_message(msg.id, content=f"Channel created successfully! {channel.mention}")

        embed = discord.Embed(title="Ticket Created!", description=f"{interaction.user.mention} created a ticket! \nTo close the ticket, click the button below.")
        await channel.send(embed=embed, view=TicketSettings())

# Cog class
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Setup Ticket Interface in given text channel
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="setup-tickets", description="[MODS] Setup Ticket Interface")
    @app_commands.describe(channel="The channel where the Ticket Interface is to be set up")
    async def setup_tickets(self, _, channel: discord.TextChannel):
        
        embed = discord.Embed(title="Create a Ticket!", description="Click on the `Create Ticket` button below to create a ticket. The server's staff will be notified and shortly aid you with your problem.")
        await channel.send(embed=embed, view=CreateTicket())

# Cog setup function
async def setup(bot):
    await bot.add_cog(Tickets(bot))