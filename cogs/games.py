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
            'Try Again in 4 Days',
            'Mineral',
            'Try Again in 4 Days',
            'NFT Comics Series "Chronicles of the Ten unique Flowers"',
            'Try Again in 4 Days',
            '"Wild Network" Branded Merch & Physical Artwork (First Edition)',
            'Try Again in 4 Days',
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
            spin_wheel = ui.Button(label="?", style=discord.ButtonStyle.blurple, custom_id=f"??{i}:blurple")
            spin_wheel.callback = self.spin_wheel
            self.views.add_item(spin_wheel)

    @app_commands.command(name="setup-spin-wheel")
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    async def setup_spinwheel(self, interaction):
        embed = discord.Embed(title='Choose the Box Carefully...', color=Var.base_color)
        embed.add_field(
            name="Prizes", value='1,111 $LEF - Native coin of the "Wild Network"\nMineral\nNFT Comics Series "Chronicles of the Ten unique Flowers"\n"Wild Network" Branded Merch & Physical Artwork (First Edition)\n\n or **Try Again in 4 Days**')
        

        channel = interaction.guild.get_channel(Var.spinwheel_channel)
        await channel.send(embed=embed, view=self.views)

    async def spin_wheel(self, interaction):
        user = interaction.user
        if user.get_role(Var.rendrill_role) is None:
            embed = discord.Embed(
                title="Not Eligible",
                description=f"You will be eligible to open the Mystery Box after you the <@{Var.rendrill_role}> from <#{Var.rendrill_channel}>."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        now = int(time.time())
    
        with open('./data/games/spin_wheel_interactions.json', 'r') as f:
            interactions = json.load(f)

        for interaction_ in interactions:
            interaction_time, interaction_user_id = interaction_
            if interaction_user_id == interaction.user.id and now - interaction_time < 4 * 24 * 60 * 60:
                time_left_in_seconds = 4 * 24 * 60 * 60 - (now - interaction_time)
                time_left_in_days = time_left_in_seconds // (24 * 60 * 60)
                time_left_in_hours = (time_left_in_seconds % (24 * 60 * 60)) // (60 * 60)
                desc = f"You have already interacted in the past 4 days. Please try again in {time_left_in_days} days and {time_left_in_hours} hours."
                embed = discord.Embed(
                    title="Spin the Wheel Prize",
                    description=desc
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        prize = self.wheel.spin()

        if prize == 'Try Again in 4 Days':
            desc = "Unfortunately you have chosen the empty box, Try again in 4 days!"
        else:
            desc = f"**Congratulations!**\nYou have won the `{prize}`."

        embed = discord.Embed(
            title="Prize Info",
            description="Keep an eye on <#1051064803025760346> channel, in order to be informed when you will get your prize(s)." if desc is not "Unfortunately you have chosen the empty box, Try again in 4 days!" else None
        )
        embed.add_field(name="Result", value=desc)

        await interaction.response.send_message(embed=embed, ephemeral=True)

        interaction_ = [now, interaction.user.id]
        interactions.append (interaction_)

        with open('./data/games/spin_wheel_interactions.json', 'w') as f:
            json.dump(interactions, f)

# Cog setup command
async def setup(bot):
    await bot.add_cog(Games(bot))
