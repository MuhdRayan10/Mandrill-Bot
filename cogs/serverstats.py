from requests import Session
import json
import asyncio

import datetime

import discord
from discord.ext import commands, tasks

from helpers import Var as V
Var = V()

class CryptoToUsd:
    def __init__(self) -> None:
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'  # Coinmarketcap API url

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': "d61d9d58-eb85-45a0-854e-a4765400d8e1"
        }

        self.session = Session()
        self.session.headers.update(headers)

    def flare(self):
        parameters = {'symbol': 'FLR', 'convert': 'USD'}

        response = self.session.get(self.url, params=parameters)

        info = json.loads(response.text)
        print(info)

        if info:
            if info['data']['FLR']['quote']['USD']['percent_change_1h'] > 0: # other available options: percent_change_24h,percent_change_7d upto 90d 
                trend = 1
            else:
                trend = 0

            return round(info['data']['FLR']['quote']['USD']['price'], 7), trend
        
class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.guilds[0]
        self.crypto_helper = CryptoToUsd()

        self.update_cryptos.start()
        self.update_mint_date.start()

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

        FLR, trend = self.crypto_helper.flare()

        flr_channel = await self.guild.fetch_channel(Var.flr_stats_channel)

        up, down = "🟢 (↗)", "🔴 g(↘)"
        await flr_channel.edit(name=f"FLR {up if trend == 1 else down} {FLR}")

    @tasks.loop(minutes=1)
    async def update_mint_date(self):
        print("Updating Mint")
        mint_channel = await self.guild.fetch_channel(Var.mint_date_channel)

        def time_remaining():
            now = datetime.datetime.now()
            end_of_day = datetime.datetime(now.year, 2, 28, 23, 0, 0)
            delta = end_of_day - now
            return f"{delta.days} Days & {delta.seconds//3600:02}:{(delta.seconds//60)%60:02}:{delta.seconds%60:02}"

        x = await mint_channel.edit(name=f"In {time_remaining()}")
        print(x)


# Cog setup command
async def setup(bot):
    await bot.add_cog(ServerStats(bot))