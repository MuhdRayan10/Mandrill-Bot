from discord import app_commands
from discord.ext import commands
from discord import ui
import discord
import json
from helpers import Var as V
from easy_sqlite3 import *
from datetime import timedelta

Var = V()

cache = {}
style = discord.ButtonStyle.blurple


class QuestionnaireMenu(ui.View):
    def __init__(self, userid):
        super().__init__(timeout=None)
        self.userid = userid

    @discord.ui.button(label="A", style=style, custom_id='A')
    async def a(self, __, _):
        cache[self.userid].append("A")

    @discord.ui.button(label="B", style=style, custom_id='B')
    async def b(self, __, _):
        cache[self.userid].append("B")

    @discord.ui.button(label="C", style=style, custom_id='C')
    async def c(self, __, _):
        cache[self.userid].append("C")


class Roles(commands.Cog):
    def __init__(self, bot):

        self.bot = bot

        get_explorill_button = ui.Button(
            label="Get Explorill", style=discord.ButtonStyle.green, custom_id="explorill:green")
        get_explorill_button.callback = self.give_explorill

        self.views = ui.View(timeout=None)
        self.views.add_item(get_explorill_button)

        get_promdrill_button = ui.Button(
            label="Get Promdrill", style=discord.ButtonStyle.green, custom_id="promdrill:green")
        get_promdrill_button.callback = self.warning

        criteria = ui.Button(
            label="Criteria", style=discord.ButtonStyle.blurple, custom_id='requirements_prom:blurple')
        criteria.callback = self.view

        self.view2 = ui.View(timeout=None)
        self.view2.add_item(get_promdrill_button)
        self.view2.add_item(criteria)

    async def warning(self, interaction):

        await interaction.response.defer()

        # checks if user has filled the two criteria
        db = Database("./data/criteria")
        data = db.select("role", where={"user": interaction.user.id}, size=1)

        if not data:
            data = (interaction.user.id, 0, 0, 0, 0)
            db.insert("role", data)

        db.close()

        if not (data[1] >= 8 and data[2] >= 12):

            message = "Looks like you haven't completed all three tasks...  press the `Criteria` button!"
            await interaction.followup.send(message, ephemeral=True)
            return

        embed = discord.Embed(title="You are about to start the Quiz!")
        embed.add_field(name="Have in mind that:", value="""• You have to answer all questions correctly in order to get the Promdrill role
• You will have the second chance in 24 hours
• Read carefully, don’t rush and Good Luck!""")

        ready_button = ui.Button(
            label="I'm ready!", style=discord.ButtonStyle.green)
        ready_button.callback = self.promdrill

        view = ui.View(timeout=None)
        view.add_item(ready_button)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def give_explorill(self, interaction):

        explorill_role = interaction.guild.get_role(Var.explorill_role)
        unverified_role = interaction.guild.get_role(Var.mute_role)

        roles = interaction.user.roles

        if unverified_role in roles:
            await interaction.response.send_message(f"Unfortunately you are still unverified... Go verify yourself at <#{Var.verification_channel}>", ephemeral=True)
            return

        if explorill_role in roles:
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already an `Exporill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            await interaction.user.add_roles(explorill_role)
            await interaction.response.send_message(f"You are now officially an Explorill!", ephemeral=True)
            await interaction.user.remove_roles(interaction.guild.get_role(Var.muted_role))

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-explorill", description="[MODS] Setup explorill role interface")
    async def setup_explorill(self, interaction):
        embed = discord.Embed(
            title='Click the button to get your Explorill role', color=Var.base_color)

        channel = interaction.guild.get_channel(Var.explorill_channel)
        await channel.send(embed=embed, view=self.views)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-promdrill", description="[MODS] Sets up promdrill interface.")
    async def setup_promdrill(self, interaction):
        embed = discord.Embed(
            title='Click the button to get your Promdrill role', color=Var.base_color)

        channel = interaction.guild.get_channel(Var.promdrill_channel)
        await channel.send(embed=embed, view=self.view2)

    async def promdrill(self, interaction):
        user = interaction.user
        blurple_btn = discord.ButtonStyle.blurple

        # if user already has role
        if interaction.user.get_role(Var.promdrill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already a `Promdrill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        elif not interaction.user.get_role(Var.rendrill_role):
            embed = discord.Embed(
                title="Required Role",
                description=f"First you have to <#{Var.rendrill_channel}> role to be a `Promdrill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # checks if user has filled the two criteria
        db = Database("./data/criteria")
        data = db.select("role", where={"user": interaction.user.id}, size=1)

        if not data:
            data = (interaction.user.id, 0, 0, 0, 0)
            db.insert("role", data)

        db.close()

        if not (data[1] >= 8 and data[2] >= 12):

            message = "Looks like you haven't completed all three tasks...  press the `Criteria` button!"
            await interaction.followup.send(message, ephemeral=True)
            return

        questions = [
            'Who are the "Guardrills"?',
            'How many Income percentages are distributed to the "Mandrills" owners in total?',
            'What do you need to enter to out Metaverse?'
        ]
        options = [
            ['(A) They are "Supporters"', '(B) They are "Moderators"',
             '(C) They are "Newcomers"'],
            ['(A) 22.22%', '(B) 44.44%', '(C) 11.11%'],
            ['(A) Mineral', '(B) All the species', '(C) At least one species']
        ]
        correct_options = [
            'B',
            'B',
            'C'
        ]

        # Creating Embed
        q_embed = discord.Embed(
            title="Choose the answer carefully…",
            color=Var.base_color
        )

        def check(i) -> bool:
            return i.data['component_type'] == 2 and i.user.id == interaction.user.id

        score = 0
        for i, question in enumerate(questions):
            q_embed.remove_field(0)

            # Add question and options to the embed
            q_embed.add_field(name=question, value="\n".join(options[i]))

            # Create view with buttons for each option
            before_answer_view = ui.View()
            for j, _ in enumerate(options[i]):
                before_answer_view.add_item(ui.Button(
                    # Option letter, e.g. 'A', 'B', 'C'
                    custom_id=chr(ord('A') + j),
                    label=chr(ord('A') + j),
                    style=blurple_btn
                ))

            # Send question message and wait for button click
            question_message = await interaction.followup.send(embed=q_embed, view=before_answer_view, ephemeral=True)
            result = await self.bot.wait_for("interaction", check=check, timeout=None)
            await result.response.defer()

            # Create view with colored buttons
            question_wrong_view = ui.View()
            for j, _ in enumerate(options[i]):
                question_wrong_view.add_item(ui.Button(
                    custom_id=chr(ord('A') + j),
                    label=chr(ord('A') + j),
                    style=discord.ButtonStyle.grey,
                    disabled=True
                ))

            # Update message with colored buttons
            await question_message.edit(embed=q_embed, view=question_wrong_view)

            # Increment score if the selected option is correct
            if result.data['custom_id'] == correct_options[i]:
                score += 1

        # Create final result embed
        passed = score == len(questions)
        result_embed = None

        if passed:
            result_embed = discord.Embed(
                title="Rendrill Questionnaire Results",
                color=Var.base_color)

            result_embed.description = "Congratulations, you have passed the questionnaire!"
        else:
            result_embed = discord.Embed(
                title="We appreciate your efforts!", description="You didn't make it through this round")
            result_embed.add_field(
                name="ㅤ", value=f"Navigate to our website through <#{Var.official_links}>\nRead carefully “Path of the Wild Network”\nCome back in 24 hours and try again!")
        result_embed.add_field(
            name="Score", value=f"{score if passed else '?'}/{len(questions)}")

        # Send final result message
        await interaction.followup.send(embed=result_embed, ephemeral=True)

        if passed:
            result_embed.description = "Congratulations, you have passed the questionnaire!"
        else:
            result_embed.description = "Sorry, you have failed the questionnaire. Better luck next time."

        await interaction.followup.send(embed=result_embed, ephemeral=True)

        if passed:
            role = user.guild.get_role(Var.promdrill_role)
            await user.add_roles(role)

            await interaction.followup.send("You have been awarded the `Promdrill` Role!", ephemeral=True)
            return

        if score < 6:
            await user.timeout(timedelta(hours=24))
            return

    async def view(self, interaction):

        user = interaction.user
        # if user already has guardrill role
        if user.get_role(Var.promdrill_role):
            embed = discord.Embed(title="Role already assigned", color=Var.base_color,
                                  description="It looks like you already have the `Promdrill` role. Thank you for your interest!")

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

        rc, wc = '❌', '✅'

        # Embed
        embed = discord.Embed(title="Promdrill Role Criteria",
                              description="Complete all 3 tasks to get the Promdrill role!", color=Var.base_color)
        embed.add_field(
            name=f"{rc if data[1] < 8 else wc} Invite at least 8 users to the server", value="ㅤ", inline=False)
        embed.add_field(
            name=f"{rc if data[2] < 12 else wc} Reach Level - 12", value="ㅤ", inline=False)
        embed.add_field(
            name=f"{rc} Complete the Quiz (after 1st & 2nd tasks)", value="ㅤ", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.checks.has_any_role(Var.liberator_role, Var.guardrill_role)
    @app_commands.command(name="set-req-prom", description="[MODS] Set requirements for a user to obtain Promdrill role.")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Invite 8 Members", value=1),
        app_commands.Choice(name="Reach Lvl. 12", value=2),
        app_commands.Choice(name="Complete Quiz", value=3)
    ])
    @app_commands.choices(done=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
    ])
    async def set_req_prom(self, interaction, user: discord.Member, activity: int, done: int):

        # add to json file
        with open("./data/req.json", "r") as f:
            data__ = json.load(f)

        if user.id not in data__["promdrill"]:
            data__["promdrill"].append(user.id)
            with open("./data/req.json", "w") as f:
                json.dump(data__, f)

        db = Database("./data/criteria")
        data = db.select("role", where={"user": user.id})

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user": user.id})

        data = list(data[0])

        # Status of all 3 activites and whether role should be given and updating
        a1 = done if activity == 1 else data[1]
        a2 = done if activity == 2 else data[2]
        a3 = done if activity == 3 else data[3]

        if activity == 1 and done:
            a1 = 8
        elif activity == 2 and done:
            a2 = 12

        db.update("role", {"user": user.id, "a1": a1, "a2": a2, "a3": a3, "role": 0},
                  where={"user": user.id})
        db.close()

        await interaction.response.send_message(f"Updated.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Roles(bot))
