import random

import time
import json
import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
from easy_sqlite3 import *

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

        for i in range(10):
            spin_wheel = ui.Button(label="?", style=discord.ButtonStyle.blurple, custom_id=f"??{i}:blurple")
            spin_wheel.callback = self.spin_wheel
            self.views.add_item(spin_wheel)

    @app_commands.command(name="setup-mystery-box")
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    async def setup_mystery_box(self, interaction, channel:discord.TextChannel):
        embed = discord.Embed(title='Choose the Box Carefully...', color=Var.base_color)
        embed.add_field(name="Prizes", value='- Mineral\n- NFT Comics Series "Chronicles of the Ten Unique Flowers" (1/12)\n- 1,111 $LEF - Native coin of the "Wild Network"\n- One Full Set of Branded Merch & Physical Artwork (1/12)')
        
        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(f"Added `Mystery Box` interface, to <#{channel.id}>")

    async def spin_wheel(self, interaction):
        user = interaction.user
        if user.get_role(Var.rendrill_role) is None:
            embed = discord.Embed(
                title="Not Eligible",
                description=f"You will be eligible to open the Mystery Box after you <#{Var.rendrill_channel}> role.",
                color=Var.base_color
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
                    description=desc, color=Var.base_color
                )
                
                db = Database("./data/prizes")
                try:
                    if db.if_exists("prizes", {"winner":interaction.user.id}):
                        embed = discord.Embed(title="You have already won a prize!", description=desc, color=Var.base_color)
                        await interaction.response.send_message(embed=embed, ephemeral=True)

                        db.close()
                        return
                except:
                    return
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        prize = self.wheel.spin()

        if prize == 'Try Again in 4 Days':
            desc = "Unfortunately you have chosen the empty box, Try again in 4 days!"
        else:
            desc = f"**Congratulations!**\nYou have won the `{prize}`."
            db = Database("./data/prizes")
            db.create_table("prizes", {"winner":INT, "name":"TEXT", "prize":"TEXT"})

            db.insert("prizes", (interaction.user.id, interaction.user.name, prize))
            db.close()

        embed = discord.Embed(
            title="Mystery Box Reveal", 
            description=desc,
            color=Var.base_color)
        embed.add_field(name="ㅤ", value="Keep an eye on the <#1051064803025760346> channel, in order to be informed when you will get your prize(s)." if desc != "Unfortunately you have chosen the empty box, Try again in 4 days!" else '')

        await interaction.response.send_message(embed=embed, ephemeral=True)

        interaction_ = [now, interaction.user.id]
        interactions.append (interaction_)

        with open('./data/games/spin_wheel_interactions.json', 'w') as f:
            json.dump(interactions, f)

# Cog setup command
async def setup(bot):
    await bot.add_cog(Games(bot))
