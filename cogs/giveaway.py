import pygsheets
import pandas as pd
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
        gc = pygsheets.authorize(service_file='./data/credentials.json')

        sh = gc.open("Mandrills Discord Server: Giveaway")

        self.wsh = sh.sheet1
        self.refresh_local()

    def refresh_local(self):
        self.df = pd.DataFrame(self.wsh.get_all_records())
        self.raw_df = self.df.copy(deep=True)

        # Convert Date and Time columns to datetime format
        self.df['Date'] = pd.to_datetime(self.df['Date'], format=r'%d/%m/%Y')
        self.df['Time'] = pd.to_datetime(
            self.df['Time'][:6], format=r'%H:%M:%S').dt.time

        # Combine Date and Time columns into a single datetime column
        self.df['datetime'] = pd.to_datetime(
            self.df['Date'].astype(str) + ' ' + self.df['Time'].astype(str))

        print(self.df)

    def get_upcoming_occurance(self):
        """Gets the latest upcoming occurance of the giveaway from the google sheet."""

        # Get the current UTC time
        current_time = datetime.utcnow()

        # Filter the DataFrame to include only rows with datetime values after the current time
        future_df = self.df[self.df['datetime'] > current_time]

        # If there are no rows with datetime values after the current time, return -1
        if future_df.empty:
            result = -1

        else:
            # Get the row with the smallest datetime value (i.e., the most upcoming datetime)
            upcoming_row = future_df.loc[future_df['datetime'].idxmin()]

            # Convert the row to a dictionary
            result = upcoming_row.to_dict()

        return result

    def get_previous_occurrence(self):
        """Gets the most recent occurrence of the giveaway from the Google Sheet."""

        # Get the current UTC time
        current_time = datetime.utcnow()

        # Filter the DataFrame to include only rows with datetime values before the current time
        past_df = self.df[self.df['datetime'] < current_time]

        # If there are no rows with datetime values before the current time, return -1
        if past_df.empty:
            result = -1

        else:
            # Get the row with the largest datetime value (i.e., the most recent datetime)
            previous_row = past_df.loc[past_df['datetime'].idxmax()]

            # Convert the row to a dictionary
            result = previous_row.to_dict()

        return result

    def update_winner(self, questionid: int, winner_user: str):
        """Updates the winners username in the google sheet. (given the question id)"""
        self.raw_df.loc[self.df['ID'].astype(
            int) == questionid, "User"] = winner_user

        # TODO: fix small error -> remove datetime column from db

        self.wsh.set_dataframe(self.raw_df, start='A1')

        self.refresh_local()


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
    async def giveaway(self, interaction: discord.Interaction):
        previous_giveaway = self.db.get_previous_occurrence()

        if not previous_giveaway['User']:
            await interaction.response.send_message("The previous giveaway has not been responded to.", ephemeral=True)
            return

        newest_giveaway = self.db.get_upcoming_occurance()

        if newest_giveaway == -1:
            await interaction.response.send_message("No new giveaway in google sheet", ephemeral=True)
            return

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

        await interaction.channel.send(embeds=[embed1, embed], view=self.views)

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
            name="Your answer has been submitted", value=f"Keep an eye on the #<1081900787795496970> channel. The winner and new question will appear at a random time in this range: 12:00-12:00 UTC", inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))
