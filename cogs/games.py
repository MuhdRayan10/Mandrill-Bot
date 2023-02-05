import random

import discord
from discord.ext import commands
from discord import ui

from helpers import Var as V
Var = V()

class wheel:
    def __init__(self) -> None:
        self.items = [
            '1,111 $LEF - Native coin of the "Wild Network"',
            'Try Again in 7 Days',
            'Mineral',
            'Try Again in 7 Days',
            'NFT Comics Series "Chronicles of the Ten unique Flowers',
            'Try Again in 7 Days',
            '"Wild Network" Branded Merch & Physical Artwork (First Edition)',
            'Try Again in 7 Days',
        ]
        

    def spin(self) -> str:
        return random.choice(self.items)

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # wheel
        self.wheel = wheel()
        spin_wheel = ui.Button(label="Spin", style=discord.ButtonStyle.green, custom_id="games:spin_wheel")
        spin_wheel.callback = self.spin_wheel

        self.views= ui.View(timeout=None)
        self.views.add_item(spin_wheel)

    def spin_wheel(self):
        prize = self.wheel.spin()

        if prize == 'Try Again in 7 Days':
            desc = "You have not recieved any prize. Try again in 7 days!"
        else:
            desc = f"You have recieved {prize}! [CONTACT A MOD TO CLAIM]"

        embed = discord.Embed(
            title="Spin the Wheel Prize",
            description=desc
        )

# Cog setup command
async def setup(bot):
    await bot.add_cog(Games(bot))
