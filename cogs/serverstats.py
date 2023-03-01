from requests import Session
import json
import asyncio
import pytz
import os

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
            'X-CMC_PRO_API_KEY': os.getenv("COINMARKETCAPKEY")
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

        self.update_mint_date.start()
        self.update_crypto.start()

    @tasks.loop(minutes=5)
    async def update_crypto(self):
        FLR, trend = self.crypto_helper.flare()

        flr_channel = await self.guild.fetch_channel(Var.flr_stats_channel)

        up, down = "🟢 (↗)", "🔴 (↘)"
        await flr_channel.edit(name=f"FLR {up if trend == 1 else down} {FLR}")


    @tasks.loop(minutes=1)
    async def update_mint_date(self):

        mint_channel = await self.guild.fetch_channel(Var.mint_date_channel)

        timezone = pytz.timezone('Etc/GMT-5')

        def time_remaining():
            now = datetime.datetime.now(tz=timezone)
            end_of_day = datetime.datetime(now.year, 2, 28, 21, 0, 0, tzinfo=timezone)
            end_of_day += datetime.timedelta(hours=5, minutes=21)
            delta = end_of_day - now

            if delta.seconds < 0:
                return "MINT is LIVE"
            return f"MINT In {delta.days} Days, {delta.seconds//3600:02}:{(delta.seconds//60)%60:02}"

        await mint_channel.edit(name=f"{time_remaining()}")

# Cog setup command
async def setup(bot):
    await bot.add_cog(ServerStats(bot))