from discord.ext import commands
from discord import app_commands
import discord
import asyncio
from helpers import Var as V

Var = V()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.command(name="kick", descriptions="[MODS] Kick a user from the server")
    @app_commands.describe(user="User to be kicked from the server")
    @app_commands.describe(reason="The reason for kicking the user")
    async def kick(self, interaction, user:discord.Member, reason:str):
        
        await user.kick(reason=reason)
        await interaction.response.send_message(f"{user.name} has been kicked by {interaction.user.mention} for the reason: `{reason}`!")

    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.command(name="ban", descriptions="[MODS] Ban a user from the server")
    @app_commands.describe(user="User to be kicked from the server")
    @app_commands.describe(reason="The reason for kicking the user")
    async def ban(self, interaction, user:discord.Member, reason:str):

        await user.ban(reason=reason)
        await interaction.response.send_message(f"{user.name} has been banned by {interaction.user.mention} for the reason: `{reason}`!")

    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.command(name="softban", descriptions="[MODS] Softbans (resets) a user from the server")
    @app_commands.describe(user="User to be softbanned from the server")
    @app_commands.describe(reason="The reason for softbanning the user")
    async def softban(self, interaction, user:discord.Member, reason:str):

        await user.ban(reason=reason)
        await user.unban(reason="Softban done")

        await interaction.response.send_message(f"{user.name} has been softbanned by {interaction.user.mention} for the reason: `{reason}`!")

    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.command(name="tempban", descriptions="[MODS] Temp ban  a user from the server")
    @app_commands.describe(user="User to be temp banned from the server")
    @app_commands.describe(reason="The reason for temp banning the user")
    @app_commands.describe(time="How long the temp ban should last in minutes")
    async def tempban(self, interaction, user:discord.Member, reason:str, time:int=5):
        
        await user.ban(reason=reason)
        asyncio.sleep(time*60)

        await user.unban(reason="Temp ban time over")

        await interaction.response.send_message(f"{user.name} has been softbanned by {interaction.user.mention} for the reason: `{reason}` for {time} minutes!")

    @app_commands.checks.has_role(Var.guardrill_role)
    @app_commands.command(name="purge", description="[MODS] Purge messages")
    @app_commands.describe(limit="Amount of messages to be deleted")
    async def purge(self, interaction, limit:int):
        pass
        