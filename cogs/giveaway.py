import pygsheets
import pandas as pd
import discord
from discord import app_commands
from discord.ext import commands
from discord import ui

import json

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

    def retrive_question(self, id_: int):
        self.refresh_local()
        try:
            return self.df.loc[self.df['ID'] == id_].to_dict('records')[0]
        except IndexError:
            return -1

    def get_CIP(self):
        self.refresh_local()

        return self.df.loc[self.df['CIP'] == 1].to_dict('records')[0]

    def update_CIP(self, question_id, val=1 or 0):
        self.refresh_local()

        # Find the row with the specified question_id
        row_index = self.df.index[self.df['ID'] == question_id].tolist()

        if not row_index:
            return -1

        row_index = row_index[0]  # Take the first index (should be unique)

        # Update the value of the 'CIP' column for that row
        self.raw_df.at[row_index, 'CIP'] = val

        # Save the changes to the Google Sheet
        self.wsh.set_dataframe(self.raw_df, start='A1',
                               copy_index=False, copy_head=True)

    def update_winner(self, questionid: int, winner_user: str):
        """Updates the winners username in the google sheet. (given the question id)"""
        self.refresh_local()

        self.raw_df.loc[self.df['ID'].astype(
            str) == str(questionid), "User"] = winner_user

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

    def generate_question_embed(self, newest_giveaway) -> discord.Embed:
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

        return embed

    @app_commands.command(name="giveaway", description="Send giveaway of latest (most upcoming) one in database.")
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    async def giveaway(self, interaction: discord.Interaction, question_id: int, channel: discord.TextChannel):
        await interaction.response.defer()

        # get cip
        previous_giveaway = self.db.get_CIP()
        self.db.update_CIP(previous_giveaway['ID'], 0)

        newest_giveaway = self.db.retrive_question(question_id)
        self.db.update_CIP(newest_giveaway['ID'], 1)

        with open("./data/giveaway.json", "r") as f:
            d = json.load(f)
        print(d)
        users = d[str(previous_giveaway['ID'])]['correct'][1:]

        embed = self.generate_question_embed(newest_giveaway)

        str_ = f"""{previous_giveaway['User']} **Winner**"""
        for i, user in enumerate(users):
            str_ += "\n" + f"{user}"

            if i == 7:
                break

        if (type(previous_giveaway) == dict) and (previous_giveaway['ID'] != 0):
            embed1 = discord.Embed(
                title="Top 8 Participants",
                description=str_, color=Var.base_color
            )  # TODO: Rayan

            await channel.send(embeds=[embed1, embed], view=self.views)

        else:
            await channel.send(embed=embed, view=self.views)

    # command to send same giveaway, without the buttons in #chat
    @app_commands.command(name="giveaway_chat", description="Send giveaway of latest (most upcoming) one in database.")
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    async def giveaway_chat(self, interaction: discord.Interaction, question_id: int):
        await interaction.response.defer()

        # get cip
        previous_giveaway = self.db.get_CIP()
        self.db.update_CIP(previous_giveaway['ID'], 0)

        newest_giveaway = self.db.retrive_question(question_id)
        self.db.update_CIP(newest_giveaway['ID'], 1)

        embed = self.generate_question_embed(newest_giveaway)

        embed.add_field(
            name=f"Go to <#{Var.giveaway_channel}> to answer!"
        )

        # get channel from Var.chat
        channel = self.bot.get_channel(Var.chat_channel)
        await channel.send(embed=embed)

    async def giveaway_interaction(self, interaction: discord.Interaction):

        # get correct answer of latest sent giveaway
        current_giveaway = self.db.get_CIP()

        with open("./data/giveaway.json", "r") as f:
            d = json.load(f)
        d.setdefault(str(current_giveaway['ID']), {
                     "interacted": [], "correct": []})
        print(d, d[str(current_giveaway['ID'])])

        if interaction.user.id in d[str(current_giveaway['ID'])]['interacted']:
            embed = discord.Embed(
                title="Your answer is already submitted", color=Var.base_color
            )
            embed.add_field(
                name="Thank You for your interest",
                value=f"Keep an eye on the <#1081900787795496970> and <#{Var.general}> channels. The Winner and new question will appear at a random time in this range: 12:00-12:00 UTC"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            return

        correct_answer = current_giveaway['Correct']
        chosen_answer = interaction.data['custom_id']

        # check if answer has been responded correctly
        if (chosen_answer == f"giveaway:{correct_answer}") and (len(d[str(current_giveaway['ID'])]) == 0):
            # answer is correct
            self.db.update_winner(
                current_giveaway['ID'], interaction.user.display_name)
            d[str(current_giveaway['ID'])]['correct'].append(
                interaction.user.id)

        print(d)
        d[str(current_giveaway['ID'])]['interacted'].append(interaction.user.id)

        with open("./data/giveaway.json", "w") as f:
            json.dump(d, f)

        embed = discord.Embed(
            title="Thank You for participating", color=Var.base_color
        )
        embed.add_field(
            name="Your answer has been submitted", value=f"Keep an eye on the <#1081900787795496970> and <#{Var.general}> channels. The Winner and new question will appear at a random time in this range: 12:00-12:00 UTC", inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.checks.has_any_role(Var.liberator_role, Var.guardrill_role)
    @app_commands.command(name="giveaway-copy", description="Inform users about the Giveaway")
    async def giveaway_copy(self, interaction, question_id: int):
        newest_giveaway = self.db.retrive_question(question_id)

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

        embed.add_field(name="Answer the question in",
                        value="<#1081900787795496970>")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))
