from discord.ext import commands
from discord import app_commands
import discord
import asyncio
from helpers import Var as V

Var = V()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # mandrills guild
        self.guild = self.bot.guilds[0]

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
        await interaction.response.send_message(f"{user.name} has been temp banned by {interaction.user.mention} for the reason: `{reason}` for {time} minutes!")

        await asyncio.sleep(time*60)
        await user.unban(reason="Temp ban time over")

        

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="purge", description="[MODS] Purge messages")
    @app_commands.describe(limit="Amount of messages to be deleted")
    async def purge(self, interaction, limit:int):
        
        await interaction.response.send_message("Purging....")
        await interaction.channel.purge(limit=limit)
        await interaction.channel.send(content=f"Purged **{limit}** Messages!")

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
    async def unmute(self, interaction, user:discord.Member):

        muted_role = interaction.guild.get_role(Var.muted_role)
        await user.remove_roles(muted_role)

        await interaction.response.send_message(f"Unmuted {user.mention}!")

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="tempmute", description="[MODS] Temporarily a user")
    @app_commands.describe(user="The user to be temp muted")
    @app_commands.describe(time="Time in minutes")
    async def tempmute(self, interaction, user:discord.Member, time:int):

        muted_role = interaction.guild.get_role(Var.muted_role)
        await interaction.response.send_message(f"Temp Muted {user.mention} for {time} minutes!")
        await asyncio.sleep(time*60)
        await user.remove_roles(muted_role)

    @commands.Cog.listener()
    async def on_member_leave(self, member:discord.Member):
        # get channel
        channel = await self.guild.fetch_channel(Var.past_members_channel)

        joined_at = member.joined_at.strftime(r"%m/%d/%Y, %H:%M:%S")

        embed = discord.Embed(title="Membed Left", description=f"**Member ID**: {member.id}\n**Joined At**: {joined_at}")
        
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # if it is message sent by bot

        if message.author.bot is True:
            return

        # if person is liberator
        user = message.author
        member = self.guild.get_member(user.id)
        if member.get_role(Var.liberator_role) is not None:
            return

        # check for links and gifs
        keywords = ["https://", "http://", "tenor.com", "discord.gg/"]

        for keyword in keywords:
            if keyword in message.content:

                await message.reply(content="**⛔ Sorry. Links and Embeds are not allowed in our Server!**", delete_after=10)
                await message.delete()

                return

# Cog setup command
async def setup(bot):
    await bot.add_cog(Moderation(bot))