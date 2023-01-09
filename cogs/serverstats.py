import discord
from discord.ext import commands

from helpers import Var as V
Var = V()

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # server stats
        for guild in self.bot.guilds:
            # members
            channel = discord.utils.get(guild.channels, id=Var.member_stats_channel)
            await channel.edit(name=f"👤 Members: {len(guild.members)}")

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        channel = discord.utils.get(member.guild.channels, id=Var.member_stats_channel)
        await channel.edit(name=f"👤 Members: {len(member.guild.members)}")

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        channel = discord.utils.get(member.guild.channels, id=Var.member_stats_channel)
        await channel.edit(name=f"👤 Members: {len(member.guild.members)}")

# Cog setup command
async def setup(bot):
    await bot.add_cog(ServerStats(bot))