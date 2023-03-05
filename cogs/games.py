import discord
from discord import ui
from discord.ext import commands, tasks
from discord import app_commands

from easy_sqlite3 import *
import random

import time
import json

import datetime
import pytz

from helpers import Var
Var = Var()


class MysteryBox:
    def __init__(self) -> None:
        self.items = [
            '1,111 $LEF - Native coin of the "Wild Network"',
            'Mineral',
            'NFT Comics Series "Chronicles of the Ten unique Flowers"',
            '"Wild Network" Branded Merch & Physical Artwork (First Edition)'
        ]

    def spin(self) -> str:
        return random.choice(self.items)


class Games(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot


class MysteryBoxGrp(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot
        self.parent = Games(self.bot)

        self.MysteryBox = MysteryBox()

        self.view = ui.View(timeout=None)

        for i in range(10):
            box = discord.ui.Button(
                label="?", style=discord.ButtonStyle.blurple, custom_id=f"??{i}:blurple")
            box.callback = self.pick
            self.view.add_item(box)

    @app_commands.command(name="setup", description="Sets up the mystery box in the desired channel")
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    async def setup(self, interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title='Choose the Box Carefully...', color=Var.base_color)

        await channel.send(embed=embed, view=self.view)
        await interaction.response.send_message(f"Added `Mystery Box` interface, to <#{channel.id}>")

    async def pick(self, interaction):
        user = interaction.user
        if user.get_role(Var.rendrill_role) is None:
            embed = discord.Embed(
                title="Required Role",
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
            if interaction_user_id == interaction.user.id and now - interaction_time < 7 * 24 * 60 * 60:

                time_left_in_seconds = 7 * 24 * 60 * \
                    60 - (now - interaction_time)
                time_left_in_days = time_left_in_seconds // (24 * 60 * 60)
                time_left_in_hours = (time_left_in_seconds %
                                      (24 * 60 * 60)) // (60 * 60)
                desc = f"Please try again in {time_left_in_days} days and {time_left_in_hours} hours."
                embed = discord.Embed(
                    title="You have already opened the box!",
                    description=desc, color=Var.base_color
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        prize = self.wheel.spin()

        if prize == 'Try Again in 7 Days':
            desc = "Unfortunately You chose the Empty Box"
        else:

            desc = f"**Congratulations!**\nYou have won the `{prize}`."

            db = Database("./data/prizes")
            db.create_table(
                "prizes", {"winner": INT, "name": "TEXT", "prize": "TEXT"})

            db.insert("prizes", (interaction.user.id,
                      interaction.user.name, prize))
            db.close()

        embed = discord.Embed(
            title="Mystery Box Reveal",
            description=desc,
            color=Var.base_color)

        embed.add_field(name="ㅤ", value="Keep an eye on the <#1051064803025760346> channel, in order to be informed when you will get your prize(s)." if prize !=
                        "Try Again in 7 Days" else 'Try again in 7 days')

        await interaction.response.send_message(embed=embed, ephemeral=True)

        interaction_ = [now, interaction.user.id]
        interactions.append(interaction_)

        with open('./data/games/spin_wheel_interactions.json', 'w') as f:
            json.dump(interactions, f)


class Giveaway:
    pass


# utc = pytz.UTC

# start_time = datetime.time(12)
# random_time = utc.localize(datetime.datetime.combine(datetime.date.today(
# ), start_time) + datetime.timedelta(seconds=random.randint(0, 43199)))

class GiveawayGrp(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot
        self.parent = Games(self.bot)

        self.view = ui.View(timeout=None)

    # @tasks.loop(time=random_time)
    @app_commands.command(name="giveaway")
    async def giveaway(self, interaction: discord.Interaction):
        pass


async def setup(bot):
    mysterybox = MysteryBoxGrp(
        bot=bot,
        name="mysterybox",
        description="Commands related to Mystery Box",
    )
    bot.tree.add_command(mysterybox)

    bot.tree.add_command(
        GiveawayGrp(
            bot=bot,
            name="giveaway",
            description="Commands related to Giveaway Box",
        ), override=True
    )
