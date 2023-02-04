from requests import Session
import json
import os

from datetime import date, datetime

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
        if info:
            return round(info['data']['FLR']['quote']['USD']['price'], 7)
        
class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crypto_helper = CryptoToUsd()

        self.update_cryptos.start()
        self.mintdate_update.start()

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

    @tasks.loop(hours=3)
    async def mintdate_update(self):
        today_date = datetime.utcnow()
        today_date = today_date.strftime("%d-%m-%Y")
        today_date = [int(x) for x in today_date.split("-")]

        d1 = date(Var.mint_date[-1], Var.mint_date[-2], Var.mint_date[-3])
        d2 = date(today_date[-1], today_date[-2], today_date[-3])

        difference = d2 - d1
        
        channel = self.bot.get_channel(Var.mint_channel)
        await channel.edit(name=f"Days: {difference.days}")

    @tasks.loop(minutes=Var.crypto_update_time)
    async def update_cryptos(self):

        FLR = self.crypto_helper.get_current_flare()

        guild = self.bot.guilds()[0]

        flr_channel = await guild.fetch_channel(Var.flr_stats_channel)

        up, down = "🟢(↗)", "🔴(↘)"

        trend = self.calculate_trend(FLR)
        await flr_channel.edit(name=f"FLR {up if trend else down} {FLR}")


# Cog setup command
async def setup(bot):
    await bot.add_cog(ServerStats(bot))