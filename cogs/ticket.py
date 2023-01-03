from discord.ext import commands
from discord.ui import View
from discord import app_commands
import discord

class TicketSettings(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close(self, interaction, _):
        await interaction.response.send_message("Ticket is being closed...", ephemeral=True)
        await interaction.channel.delete()



class CreateTicket(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction, _):

        await interaction.response.defer()

        msg = await interaction.followup.send(content="A ticket is being created!", ephemeral=True)
        other_role = interaction.guild.get_role(102939012093) #mods

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True)#,
            #other_role: discord.PermissionOverwrite(read_messages=True)
        }

        category = discord.utils.get(interaction.guild.categories, name='Tickets')
        channel = await interaction.guild.create_text_channel(f"[TICKET]-{interaction.user.name}",
                overwrites=overwrites, category=category)

        await interaction.followup.edit_message(msg.id, content=f"Channel created successfully! {channel.mention}")

        embed = discord.Embed(title="Ticket Created!", description=f"{interaction.user.mention} created a ticket! \nTo close the ticket, click the button below.")
        await channel.send(embed=embed, view=TicketSettings())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup-tickets", description="[MODS] Setup Ticket Interface")
    async def setup_tickets(self, interaction):
        embed = discord.Embed(title="Create a Ticket!", description="Click on the `Create Ticket` button below to create a ticket. The server's staff will be notified and shortly aid you with your problem.")
        await interaction.response.send_message(embed=embed, view=CreateTicket())


async def setup(bot):
    await bot.add_cog(Tickets(bot))