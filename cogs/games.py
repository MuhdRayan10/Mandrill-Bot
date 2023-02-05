import random

import time
import json
import discord
from discord import app_commands
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

        self.views = ui.View(timeout=None)

        for i in range(5):
            spin_wheel = ui.Button(label="??", style=discord.ButtonStyle.blurple, custom_id=f"??{i}:blurple")
            spin_wheel.callback = self.spin_wheel
            self.views.add_item(spin_wheel)

    @app_commands.command(name="setup-spin-wheel")
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    async def setup_spinwheel(self, interaction):
        embed = discord.Embed(title='Mystery Prize', description='Click the button to play.', color=Var.base_color)
        embed.add_field(
            name="Prizes", value='\n'.join(self.wheel.items)
        )

        channel = interaction.guild.get_channel(Var.spinwheel_channel)
        await channel.send(embed=embed, view=self.view)

    async def spin_wheel(self, interaction):
        now = int(time.time())

        with open('./data/games/spin_wheel_interactions.json', 'r') as f:
            interactions = json.load(f)

        for interaction_ in interactions:
            interaction_time, interaction_user_id = interaction_
            if interaction_user_id == interaction.user.id and now - interaction_time < 7 * 24 * 60 * 60:
                desc = f"You have already interacted in the past 7 days. Please try again later."
                embed = discord.Embed(
                    title="Spin the Wheel Prize",
                    description=desc
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        prize = self.wheel.spin()

        if prize == 'Try Again in 7 Days':
            desc = "You have not received any prize. Try again in 7 days!"
        else:
            desc = f"You have won {prize}!"

        embed = discord.Embed(
            title="Spin the Wheel Prize",
            description=desc
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        interaction_ = [now, interaction.user.id]
        interactions.append(interaction_)

        with open('./data/games/spin_wheel_interactions.json', 'w') as f:
            json.dump(interactions, f)

# Cog setup command
async def setup(bot):
    await bot.add_cog(Games(bot))
