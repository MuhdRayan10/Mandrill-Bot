from requests import Request, Session
import json
import os

import discord
from discord.ext import commands, tasks

from helpers import Var as V
Var = V()

class CryptoToUsd:

	def __init__(self) -> None:
		self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'  # Coinmarketcap API url

		headers = {
		 'Accepts': 'application/json',
		 'X-CMC_PRO_API_KEY': os.getenv('COINMARKETCAPKEY')
		}

		self.session = Session()
		self.session.headers.update(headers)

	def get_current_flare(self) -> int:
		parameters = {'symbol': 'FLR', 'convert': 'USD'}

		response = self.session.get(self.url, params=parameters)

		info = json.loads(response.text)

		return round(info['data']['FLR']['quote']['USD']['price'], 7)

	def get_current_songbird(self) -> int:
		parameters = {'symbol': 'SGB', 'convert': 'USD'}

		response = self.session.get(self.url, params=parameters)

		info = json.loads(response.text)

		return round(info['data']['SGB']['quote']['USD']['price'], 7)

        

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crypto_helper = CryptoToUsd()

        self.update_cryptos.start()

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

    @tasks.loop(minutes=Var.crypto_update_time)
    async def update_cryptos(self):
        FLR, SGB = self.crypto_helper.get_current_flare(), self.crypto_helper.get_current_songbird()

        guild = self.bot.guilds()[0]

        flr_channel = await guild.fetch_channel(Var.flr_stats_channel)
        sbg_channel = await guild.fetch_channel(Var.sgb_stats_channel)

        # TODO: Rayan fix

# Cog setup command
async def setup(bot):
    await bot.add_cog(ServerStats(bot))