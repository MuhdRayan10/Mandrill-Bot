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
    @app_commands.command(name="kick", description="[MODS] Kick a user from the server")
    @app_commands.describe(user="User to be kicked from the server")
    @app_commands.describe(reason="The reason for kicking the user")
    async def kick(self, interaction, user:discord.Member, reason:str):
        
        await user.kick(reason=reason)
        await interaction.response.send_message(f"{user.name} has been kicked by {interaction.user.mention} for the reason: `{reason}`!")

    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.command(name="ban", description="[MODS] Ban a user from the server")
    @app_commands.describe(user="User to be kicked from the server")
    @app_commands.describe(reason="The reason for kicking the user")
    async def ban(self, interaction, user:discord.Member, reason:str):

        await user.ban(reason=reason)
        await interaction.response.send_message(f"{user.name} has been banned by {interaction.user.mention} for the reason: `{reason}`!")

    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.command(name="softban", description="[MODS] Softbans (resets) a user from the server")
    @app_commands.describe(user="User to be softbanned from the server")
    @app_commands.describe(reason="The reason for softbanning the user")
    async def softban(self, interaction, user:discord.Member, reason:str):

        await user.ban(reason=reason)
        await user.unban(reason="Softban done")

        await interaction.response.send_message(f"{user.name} has been softbanned by {interaction.user.mention} for the reason: `{reason}`!")

    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.command(name="tempban", description="[MODS] Temp ban  a user from the server")
    @app_commands.describe(user="User to be temp banned from the server")
    @app_commands.describe(reason="The reason for temp banning the user")
    @app_commands.describe(time="How long the temp ban should last in minutes")
    async def tempban(self, interaction, user:discord.Member, reason:str, time:int=5):
        
        await user.ban(reason=reason)
        asyncio.sleep(time*60)

        await user.unban(reason="Temp ban time over")

        await interaction.response.send_message(f"{user.name} has been softbanned by {interaction.user.mention} for the reason: `{reason}` for {time} minutes!")

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="purge", description="[MODS] Purge messages")
    @app_commands.describe(limit="Amount of messages to be deleted")
    async def purge(self, interaction, limit:int):

        await interaction.channel.purge(limit=limit+1)
        await interaction.response.send_message(content=f"Purged **{limit}** Messages!")

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="block", description="[MODS] Block user from messaging in this channel")
    @app_commands.describe(user="The user to be blocked")
    async def block(self, interaction, user:discord.Member):

        await interaction.channel.set_permissions(user, send_messages=False)
        await interaction.response.send_message(f"{user.mention} blocked from {interaction.channel.mention}!")

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="unblock", description="[MODS] Unblock user from messaging in this channel")
    @app_commands.describe(user="The user to be unblocked")
    async def unblock(self, interaction, user:discord.Member):

        await interaction.channel.set_permissions(user, send_messages=True)
        await interaction.response.send_message(f"{user.mention} unblocked from {interaction.channel.mention}!")

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="mute", description="[MODS] Mute a user")
    @app_commands.describe(user="The user to be muted")
    async def mute(self, interaction, user:discord.Member):

        muted_role = interaction.guild.get_role(Var.muted_role)
        await user.add_roles(muted_role)

        await interaction.response.send_message(f"Muted {user.mention}!")

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="unmute", description="[MODS] Unmute a user")
    @app_commands.describe(user="The user to be unmuted")
    async def mute(self, interaction, user:discord.Member):

        muted_role = interaction.guild.get_role(Var.muted_role)
        await user.remove_roles(muted_role)

        await interaction.response.send_message(f"Unmuted {user.mention}!")
    


# Cog setup command
async def setup(bot):
    await bot.add_cog(Moderation(bot))