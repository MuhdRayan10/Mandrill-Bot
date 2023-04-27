import discord
from discord import ui, app_commands
from discord.ext import commands

from easy_sqlite3 import *
import random


# Modals
class AddGiveawayModal(ui.Modal, title="Add Giveaway Question"):
    # write all the inputs for adding a question to the database
    question = ui.TextInput(
        label="Question",
        placeholder="Enter the question for the giveaway",
        style=discord.TextStyle.long,
    )
    opt1 = ui.TextInput(
        label="Option 1 (A)",
        placeholder="Enter the option 1 for the giveaway",
        style=discord.TextStyle.long,
    )

    opt2 = ui.TextInput(
        label="Option 2 (B)",
        placeholder="Enter the option 2 for the giveaway",
        style=discord.TextStyle.long,
    )

    opt3 = ui.TextInput(
        label="Option 3 (C)",
        placeholder="Enter the option 3 for the giveaway",
        style=discord.TextStyle.long,
    )

    correct_opt = ui.TextInput(
        label="Correct Option",
        placeholder="Enter the correct option for the giveaway",
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        print(interaction.data)


# Cog class
class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # persistance views
        self.dashboard = ui.View(timeout=None)

        self.db = Database("./data/giveaway.db")
        self.db.create_table(
            "questions",
            {
                "ID": INT,
                "question": "TEXT",
                "options": "TEXT",
                "answer": "TEXT",
                "winner": "TEXT",
                "done": INT,
            },
        )

        # self.db.create_table()

    @app_commands.command(name="giveaway-dashboard")
    async def giveaway_dashboard(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        """Shows the giveaway dashboard, in the preceesd channel. Only to be used once, as the dashboard is persisted.

        Dashboard contains:
        1. Add Giveaway (Button) -> Generates a modal with fields Question, opt1,2,3 and correct opt.
        2. Current Giveaway (Info)
        3. End Current Giveaway (Button) -> this declared the winner too
        4. Start Next Giveaway (Button) -> starts the next giveaway in the list, if no giveaway is present, show error
        """

        add_giveaway_button = ui.Button(
            label="Add Giveaway", style=discord.ButtonStyle.green
        )
        add_giveaway_button.callback = self.add_giveaway

        end_current_giveaway_button = ui.Button(
            label="End Current Giveaway", style=discord.ButtonStyle.red
        )
        end_current_giveaway_button.callback = self.end_current_giveaway

        start_next_giveaway_button = ui.Button(
            label="Start Next Giveaway", style=discord.ButtonStyle.blurple
        )
        start_next_giveaway_button.callback = self.start_next_giveaway

        self.dashboard.add_item(add_giveaway_button)
        self.dashboard.add_item(end_current_giveaway_button)
        self.dashboard.add_item(start_next_giveaway_button)

        # embed containning information
        embed = discord.Embed(
            title="Giveaway Dashboard",
            description="Control all giveaway related functions.",
            color=discord.Color.blue(),
        )

        # get the latest value from the database that is currently running, i.e. the  one that is not done
        current_giveaway = self.db.execute(
            "SELECT * FROM questions WHERE done = 0"
        )  # TODO RAYAN

        await channel.send(view=self.dashboard)

        await interaction.response.send_message(
            f"Dashboard sent to the <#{channel.id}>", ephemeral=True
        )

    async def add_giveaway(self, interaction: discord.Interaction):
        # add giveaway by sending the modal
        await interaction.response.send_modal(AddGiveawayModal())

    async def end_current_giveaway(self, interaction: discord.Interaction):
        pass

    async def start_next_giveaway(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(Var.giveaway_channel)

        db = Database("./data/giveaway.json")
        question = db.select("giveaway", {"done": 0}, size=1)

        db.close()

        letters = {1: "A", 2: "B", 3: "C", 4: "D"}
        correct = random.randint(0, 3)

        options = eval(question[2])
        options.insert(correct, question[2])

        options = [f"{letters[i]}) {x}" for i, x in enumerate(options)]
        giveaway_embed = discord.Embed(title="Giveaway", description="Giveaway stuff")
        giveaway_embed.add_field(name=question[1], value="\n".join(options))

        question_view = ui.View()

        for letter in letters.values():
            btn = ui.Button(label=letter, style=discord.ButtonStyle.green)
            question_view.add_item(btn)

            btn.callback = lambda l=letter: self.option_clicked(correct, l)

        await channel.send(embed=giveaway_embed, view=question_view)


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
