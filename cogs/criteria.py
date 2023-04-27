import json
from discord.ext import commands
from discord import app_commands
from discord import ui
from datetime import timedelta
import discord
from easy_sqlite3 import *

# Import stored variables
from helpers import Var as V

Var = V()


cache = {}
style = discord.ButtonStyle.blurple


def update_criterias(user_id, db: Database):
    db2 = Database("./data/invites")
    data = db2.select("invites", where={"inviter": user_id})
    db2.close()

    count = 0
    for d in data:
        count += d[2]

    db.update("role", information={"a1": count}, where={"user": user_id})


# questionnaire
class QuestionnaireMenu(ui.View):
    def __init__(self, userid):
        super().__init__(timeout=None)
        self.userid = userid

    @discord.ui.button(label="A", style=style, custom_id="A")
    async def a(self, __, _):
        cache[self.userid].append("A")

    @discord.ui.button(label="B", style=style, custom_id="B")
    async def b(self, __, _):
        cache[self.userid].append("B")

    @discord.ui.button(label="C", style=style, custom_id="C")
    async def c(self, __, _):
        cache[self.userid].append("C")

    @discord.ui.button(label="D", style=style, custom_id="D")
    async def d(self, __, _):
        cache[self.userid].append("D")


# chache for questionnaire
blurple_btn = discord.ButtonStyle.blurple


# Cog class
class Criteria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        db = Database("./data/criteria")
        db.create_table(
            "role", {"user": INT, "a1": INT, "a2": INT, "a3": INT, "role": INT}
        )

        get_rendrill_button = ui.Button(
            label="Get Rendrill",
            style=discord.ButtonStyle.green,
            custom_id="rendrill:green",
        )
        # Link function called when button clicked.
        get_rendrill_button.callback = self.warning

        criteria = ui.Button(
            label="Criteria",
            style=discord.ButtonStyle.blurple,
            custom_id="requirements:blurple",
        )
        criteria.callback = self.view

        self.views = ui.View(timeout=None)
        self.views.add_item(get_rendrill_button)
        self.views.add_item(criteria)

        db.close()

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(
        name="setup-rendrill",
        description="[MODS] Setup the rendrill button in the channel specified",
    )
    async def setup_rendrill(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(
            title="Click the button to get your Rendrill role", color=Var.base_color
        )

        # Sending message
        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(
            f"Added `Rendrill` role interface, to <#{channel.id}>"
        )

    async def warning(self, interaction):
        await interaction.response.defer()

        db = Database("./data/criteria")
        data = db.select("role", where={"user": interaction.user.id}, size=1)

        with open("./data/req.json") as f:
            data__ = json.load(f)
        if interaction.user.id not in data__["rendrill"]:
            update_criterias(interaction.user.id, db)

        if not data:
            data = (interaction.user.id, 0, 0, 0, 0)
            db.insert("role", data)

        db.close()

        if not (data[1] >= 4 and data[2] >= 6):
            message = "Looks like you haven't completed all 3 tasks...  press the `Criteria` button!"
            await interaction.followup.send(message, ephemeral=True)
            return

        embed = discord.Embed(
            title="You are about to start the Quiz!", color=Var.base_color
        )
        embed.add_field(
            name="Have in mind that:",
            value="""- You have to answer all questions correctly in order to get the Rendrill role
- You will have the second chance in 8 hours
- Read carefully, don’t rush and Good Luck!""",
        )

        ready_button = ui.Button(label="I'm ready!", style=discord.ButtonStyle.green)
        ready_button.callback = self.rendrill_questionnaire

        view = ui.View(timeout=None)
        view.add_item(ready_button)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def rendrill_questionnaire(self, interaction):
        user = interaction.user

        # if user already has role
        if interaction.user.get_role(Var.rendrill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already a `Rendrill`!",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # checks if user has filled the two criteria
        db = Database("./data/criteria")
        data = db.select("role", where={"user": interaction.user.id}, size=1)

        with open("./data/req.json") as f:
            data__ = json.load(f)
        if interaction.user.id not in data__["rendrill"]:
            update_criterias(interaction.user.id, db)

        if not data:
            data = (interaction.user.id, 0, 0, 0, 0)
            db.insert("role", data)

        db.close()

        questions = [
            "How did The Mandrills come into being?",
            "Why are the Minerals so important elements in the Wild Network's Life?",
            'How many Minerals and Mandrills must the user HOLD in order to get free Copy of the "Wild Network" NFT Comics Series "Chronicles of the Ten unique Flowers" every month based on the snapshot?',
            "How many comics series will be there in total and copies in each month?",
        ]
        options = [
            [
                "(A) With a spaceship from the Galaxy",
                "(B) Through minerals evolution over time",
                '(C) They are just generated NFTs - "You\'re quite wrong"',
                "(D) They just spawned from nowhere",
            ],
            [
                '(A) They are expensive due to scarcity - "It\'s true, but the reason for that is their usefulness"',
                '(B) Minerals are so magical and enchanting, you want to hold them all the time - "It\'s also true, but importance comes from their actual daily use cases, therefore progressive demand and value is guaranteed."',
                "(C) They are gaining progressive utility in the Wild Network's life because they hold vitality power. Minerals are the ONE and ONLY source of Metaverse energy",
                '(D) I can awaken mandrills with the help of minerals, but the mineral will be melted in that case - "Now that is the question! To be or not to be! It is up to you to decide what is more important to you, keep the mineral or use it to awaken the mandrill! BTW did you know that to join the Metaverse or buy land there, you must hold at least one species of the Wild Network, for example, the mandrill. Each species is eligible to purchase one land."',
            ],
            [
                "(A) 4 Minerals and 4 Mandrills",
                "(B) 5 Minerals and 5 Mandrills",
                "(C) 8 Minerals and 8 Mandrills",
                "(D) 21 Minerals and 21 Mandrills",
            ],
            [
                "(A) Total 12 series with 555 copies of NFT in each month",
                "(B) Total 4 series with 444 copies of NFT in each month",
                "(C) Total 8 series with 888 copies of NFT in each month",
                "(D) Total 21 series with 1,111 copies of NFT in each month",
            ],
        ]
        correct_options = ["B", "C", "B", "A"]

        # Creating Embed
        q_embed = discord.Embed(
            title="Choose the answer carefully…", color=Var.base_color
        )

        def check(i) -> bool:
            return i.data["component_type"] == 2 and i.user.id == interaction.user.id

        score = 0
        for i, question in enumerate(questions):
            q_embed.remove_field(0)

            # Add question and options to the embed
            q_embed.add_field(name=question, value="\n".join(options[i]))

            # Create view with buttons for each option
            before_answer_view = ui.View()
            for j, _ in enumerate(options[i]):
                before_answer_view.add_item(
                    ui.Button(
                        # Option letter, e.g. 'A', 'B', 'C'
                        custom_id=chr(ord("A") + j),
                        label=chr(ord("A") + j),
                        style=blurple_btn,
                    )
                )

            # Send question message and wait for button click
            question_message = await interaction.followup.send(
                embed=q_embed, view=before_answer_view, ephemeral=True
            )
            result = await self.bot.wait_for("interaction", check=check, timeout=None)
            await result.response.defer()

            # Create view with colored buttons
            question_wrong_view = ui.View()
            for j, _ in enumerate(options[i]):
                question_wrong_view.add_item(
                    ui.Button(
                        custom_id=chr(ord("A") + j),
                        label=chr(ord("A") + j),
                        style=discord.ButtonStyle.grey,
                        disabled=True,
                    )
                )

            # Update message with colored buttons
            await question_message.edit(embed=q_embed, view=question_wrong_view)

            # Increment score if the selected option is correct
            if result.data["custom_id"] == correct_options[i]:
                score += 1

        # Create final result embed
        passed = score == len(questions)
        result_embed = None
        if passed:
            result_embed = discord.Embed(title="Marvelous!", color=Var.base_color)

            result_embed.description = "You passed the Quiz…"
        else:
            result_embed = discord.Embed(
                title="We appreciate your efforts!",
                description="**You didn't make it through this round**",
            )
            result_embed.add_field(
                name="ㅤ",
                value=f"- Navigate to our website through <#{Var.official_links}>\n- Read carefully “Path of the Wild Network”\n- Come back in 8 hours and try again!",
            )

        result_embed.add_field(
            name="Score",
            value=f"{score if passed else '?'}/{len(questions)}",
            inline=False,
        )

        # Send final result message
        await interaction.followup.send(embed=result_embed, ephemeral=True)

        if passed:
            role = user.guild.get_role(Var.rendrill_role)
            await user.add_roles(role)

            db = Database("./data/criteria")
            db.update("role", {"a3": 1}, where={"user": interaction.user.id})

            db.close()

            await interaction.followup.send(
                f"Congratulations ! You are now officially a Rendrill !\nGo to the <#{Var.spinwheel_channel}>, you've earned this success ^‿^",
                ephemeral=True,
            )
            return

        if score < 2:
            await user.timeout(timedelta(hours=8))
            return

    # Command for Moderator to update user's criteria stats

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(
        name="set-req",
        description="[MODS] Update user's criteria for acquiring Rendrill Role",
    )
    @app_commands.choices(
        activity=[
            app_commands.Choice(name="Invite 4 Members", value=1),
            app_commands.Choice(name="Reach Lvl. 6", value=2),
            app_commands.Choice(name="Complete Quiz", value=3),
        ]
    )
    @app_commands.choices(
        done=[
            app_commands.Choice(name="True", value=1),
            app_commands.Choice(name="False", value=0),
        ]
    )
    @app_commands.describe(activity="What the user has done")
    @app_commands.describe(
        done="Whether the user was successful in completing the task"
    )
    async def req(self, interaction, user: discord.Member, activity: int, done: int):
        """
        This function allows the mods to update a user's criteria stats
        """

        # add to json file
        with open("./data/req.json", "r") as f:
            data__ = json.load(f)

        if user.id not in data__["rendrill"]:
            data__["rendrill"].append(user.id)
            with open("./data/req.json", "w") as f:
                json.dump(data__, f)

        # Getting data from database
        db = Database("./data/criteria")
        data = db.select("role", where={"user": user.id})
        print(data)

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user": user.id})

        data = list(data[0])
        print("SET REQ |", data)

        # Status of all 3 activites and whether role should be given and updating
        a1 = done if activity == 1 else data[1]
        a2 = done if activity == 2 else data[2]
        a3 = done if activity == 3 else data[3]

        print("SET REQ |", a1, a2, a3)

        if activity == 1 and done:
            a1 = 4
        elif activity == 2 and done:
            a2 = 6

        print("SET REQ |", a1, a2, a3)
        db.update(
            "role",
            {"user": user.id, "a1": a1, "a2": a2, "a3": a3, "role": 0},
            where={"user": user.id},
        )
        db.close()

        await interaction.response.send_message(f"Updated.", ephemeral=True)

    async def view(self, interaction):
        user = interaction.user
        # if user already has guardrill role
        if user.get_role(Var.rendrill_role):
            embed = discord.Embed(
                title="Role already assigned",
                color=Var.base_color,
                description="It looks like you already have the `Rendrill` role. Thank you for your interest!",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # Retrieving data from database
        db = Database("./data/criteria")
        data = db.select("role", where={"user": user.id})

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user": user.id})

        db.close()

        data = data[0]
        print("Criteria| ", data)

        rc, wc = "❌", "✅"

        # Embed
        embed = discord.Embed(
            title="Rendrill Role Criteria",
            description="Complete all 3 tasks to get the Rendrill role!",
            color=Var.base_color,
        )
        embed.add_field(
            name=f"{rc if data[1] < 4 else wc} Invite at least 4 users to the server",
            value="ㅤ",
            inline=False,
        )
        embed.add_field(
            name=f"{rc if data[2] < 6 else wc} Reach Level - 6", value="ㅤ", inline=False
        )
        embed.add_field(
            name=f"{rc if not data[3] else wc} Complete the Quiz (after 1st & 2nd Tasks)",
            value="ㅤ",
            inline=False,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)


# Cog setup command


async def setup(bot):
    await bot.add_cog(Criteria(bot))
