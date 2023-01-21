from discord.ext import commands, tasks
from discord.ui import View
from discord import app_commands
import discord

from helpers import Var as V

Var = V()

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
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            other_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Get Tickets category and create a new channel
        category = discord.utils.get(interaction.guild.categories, name='TICKETS')
        channel = await interaction.guild.create_text_channel(f"[TICKET]-{interaction.user.name}",
                overwrites=overwrites, category=category)

        await interaction.followup.edit_message(msg.id, content=f"Channel created successfully! {channel.mention}")

        embed = discord.Embed(title="Ticket Created!", description=f"{interaction.user.mention} created a ticket! \nTo close the ticket, click the button below.")
        await channel.send(embed=embed, view=TicketSettings())

# Cog class
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.active.start()

    # Setup Ticket Interface in given text channel
    @app_commands.checks.has_any_role(Var.rendrill_role, Var.liberator_role)
    @app_commands.command(name="setup-tickets", description="[MODS] Setup Ticket Interface")
    @app_commands.describe(channel="The channel where the Ticket Interface is to be set up")
    async def setup_tickets(self, interaction, channel: discord.TextChannel):
        
        embed = discord.Embed(title="Create a Ticket!", description="Click on the `Create Ticket` button below to create a ticket. The server's staff will be notified and shortly aid you with your problem.")
        await interaction.response.send_message(channel.mention)
        
        await channel.send(embed=embed, view=CreateTicket())

    @tasks.loop(seconds=15)
    async def active(self):
        li = []
        for i in range(0, 30000000):
            li.append(i)

        print('E')

        del li

        

# Cog setup function
async def setup(bot):
    await bot.add_cog(Tickets(bot))