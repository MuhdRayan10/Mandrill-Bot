import pygsheets
import pandas as pd
from pandas import Timestamp
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord import ui

from helpers import Var as V
Var = V()


class GiveawayDB:
    def __init__(self) -> None:
        # change this to /data/credentials.json
        gc = pygsheets.authorize(service_file='./credentials.json')

        sh = gc.open("Mandrills Discord Server: Giveaway")

        self.wsh = sh.sheet1
        self.refresh_local()

    def refresh_local(self):
        self.df = pd.DataFrame(self.wsh.get_all_records())
        self.raw_df = self.df.copy(deep=True)

    def retrive_question(self, id_: int):
        try:
            return self.df.loc[self.df['ID'] == id_].to_dict('records')[0]
        except IndexError:
            return -1


class GiveawayCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = GiveawayDB()

        self.views = ui.View(timeout=None)

        button_data = [("A", "giveaway:A"), ("B", "giveaway:B"),
                       ("C", "giveaway:C"), ("D", "giveaway:D")]

        for label, custom_id in button_data:
            button = ui.Button(label=label, custom_id=custom_id,
                               style=discord.ButtonStyle.green)
            button.callback = self.giveaway_interaction
            self.views.add_item(button)

    @app_commands.command(name="giveaway", description="Send giveaway of latest (most upcoming) one in database.")
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    async def giveaway(self, interaction: discord.Interaction, question_id: int, channel: discord.TextChannel):
        previous_giveaway = self.db.retrive_question(question_id-1)
        newest_giveaway = self.db.retrive_question(question_id)

        embed1 = discord.Embed(
            title="Top 8 Participants",
            description=f"{previous_giveaway['User']} **Winner**", color=Var.base_color
        )  # TODO: Rayan

        embed = discord.Embed(
            title="Reward: 1 Mineral",
            description="First User Who Will Choose The Right Answer", color=Var.base_color
        )
        embed.add_field(
            name=f"Question #{newest_giveaway['ID']}",
            value=newest_giveaway['Question'],
            inline=False
        )
        embed.add_field(
            name=f"Choose your answer carefully...",
            value=f"(A) {newest_giveaway['A']}\n(B) {newest_giveaway['B']}\n(C) {newest_giveaway['C']}\n(D) {newest_giveaway['D']}",
            inline=False
        )

        await channel.send(embeds=[embed1, embed], view=self.views)

    async def giveaway_interaction(self, interaction: discord.Interaction):
        # get correct answer of latest sent giveaway
        newest_giveaway = self.db.get_upcoming_occurance()
        correct_answer = newest_giveaway['Correct']
        chosen_answer = interaction.data['custom_id']

        # check if answer has been responded correctly
        if chosen_answer == f"giveaway:{correct_answer}":
            # answer is correct
            self.db.update_winner(
                newest_giveaway['ID'], interaction.user.display_name)

        # TODO: implement top 8

        embed = discord.Embed(
            title="Thank You for participating", color=Var.base_color
        )
        embed.add_field(
            name="Your answer has been submitted", value=f"Keep an eye on the <#1081900787795496970> channel. The winner and new question will appear at a random time in this range: 12:00-12:00 UTC", inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))
