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

# questionnaire
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

# chache for questionnaire
blurple_btn = discord.ButtonStyle.blurple


# Cog class
class Criteria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        db = Database("./data/criteria")
        db.create_table("role", {"user":INT, "a1":INT, "a2":INT, "a3":INT, "role":INT})

        get_rendrill_button = ui.Button(label="Get Rendrill", style=discord.ButtonStyle.green, custom_id="rendrill:green")
        get_rendrill_button.callback = self.rendrill_questionnaire # Link function called when button clicked.

        criteria = ui.Button(label="Criteria", style=discord.ButtonStyle.blurple, custom_id='requirements:blurple')
        criteria.callback = self.view
        
        self.views = ui.View(timeout=None)
        self.views.add_item(get_rendrill_button)
        self.views.add_item(criteria)

        db.close()

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-rendrill", description="[MODS] Setup the rendrill button in the channel specified")
    async def setup_rendrill(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(title='Click the button to get your Rendrill role', color=Var.base_color)
        

        # Sending message
        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(f"Added `get rendrill` interface, to <#{channel.id}>")

    async def rendrill_questionnaire(self, interaction):
        user = interaction.user

        # if user already has guardrill role
        if user.get_role(Var.guardrill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you already have the `guardrill` role. Thank you for your interest!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # checks if user has filled the two criteria
        db = Database("./data/criteria")
        data = db.select("role", where={"user":interaction.user.id}, size=1)

        if not data:
            data = (interaction.user.id, 0, 0, 0, 0)
            db.insert("role", data)
            
        db.close()

        if not(data[1] >= 2 and data[2] == 1):

            message = "Looks like you haven't completed the first two criteria yet...  press the Criteria button!"
            await interaction.followup.send(message, ephemeral=True)
            return

        questions = [
            'Who are the "Guardrills"?', 
            'How many Income percentages are distributed to the "Mandrills" owners in total?', 
            'What do you need to enter to out Metaverse?'
        ]
        options = [
            ['(A) They are "Supporters"', '(B) They are "Moderators"', '(C) They are "Newcomers"'],
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
            title="Rendrill Questionnaire",
            description="Answer the questions, accurately.",
            color=discord.Color(Var.base_color)
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
                    custom_id=chr(ord('A') + j),  # Option letter, e.g. 'A', 'B', 'C'
                    label=chr(ord('A') + j),
                    style=blurple_btn
                ))

            # Send question message and wait for button click
            question_message = await interaction.followup.send(embed=q_embed, view=before_answer_view, ephemeral=True)
            result = await self.bot.wait_for("interaction", check=check, timeout=None)
            await result.response.defer()

            # Set color of selected option to green or red based on whether it is correct
            color_map = {chr(ord('A') + j): discord.ButtonStyle.red for j in range(len(options[i]))}
            color_map[correct_options[i]] = discord.ButtonStyle.green

            # Create view with colored buttons
            question_wrong_view = ui.View()
            for j, _ in enumerate(options[i]):
                question_wrong_view.add_item(ui.Button(
                    custom_id=chr(ord('A') + j),
                    label=chr(ord('A') + j),
                    style=color_map[chr(ord('A') + j)]
                ))

            # Update message with colored buttons
            await question_message.edit(embed=q_embed, view=question_wrong_view)

            # Increment score if the selected option is correct
            if result.data['custom_id'] == correct_options[i]:
                score += 1

        # Create final result embed
        result_embed = discord.Embed(
            title="Rendrill Questionnaire Results",
            color=discord.Color(Var.base_color)
        )
        passed = score == len(questions)
        if passed:
            result_embed.description = "Congratulations, you have passed the questionnaire!"
        else:
            result_embed.description = "Sorry, you have failed the questionnaire. Better luck next time."
        result_embed.add_field(name="Score", value=f"{score}/{len(questions)}")

        # Send final result message
        await interaction.followup.send(embed=result_embed, ephemeral=True)

        if passed:
            role = user.guild.get_role(Var.rendrill_role)
            await user.add_roles(role)

            db = Database("./data/criteria")
            db.update("role", {"a3":1}, where={"user":interaction.user.id})

            db.close()

            await interaction.followup.send("You have been awarded the `Rendrill` Role!", ephemeral=True)
            return

        if score < 2:
            await user.timeout(timedelta(minutes=5))
            return

        


    # Command for Moderator to update user's criteria stats
    @app_commands.checks.has_any_role(Var.rendrill_role, Var.liberator_role)
    @app_commands.command(name="set-req", description="[MODS] Update user's criteria for acquiring Rendrill Role")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Invite 4 Members", value=1),
        app_commands.Choice(name="Reach Lvl. 4", value=2),
        app_commands.Choice(name="Complete Quiz", value=3)
    ])
    @app_commands.choices(done=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
    ])
    @app_commands.describe(activity="What the user has done")
    @app_commands.describe(done="Whether the user was successful in completing the task")

    async def req(self, interaction, user:discord.Member, activity:int, done:int):
        """
        This function allows the mods to update a user's criteria stats
        """

        # Getting data from database 
        db = Database("./data/criteria")
        data = db.select("role", where={"user":user.id})

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user":user.id})

        data = data[0]
        
        # Status of all 3 activites and whether role should be given and updating
        a1 = done if activity == 1 else data[1]
        a2 = done if activity == 2 else data[2]
        a3 = done if activity == 3 else data[3]

        if a1 == 1 and done == 1:
            a1 += 3

        if_role = 1 if a1 and a2 and a3 else 0

        db.update("role", {"user":user.id, "a1":a1, "a2":a2, "a3":a3, "role":if_role},
             where={"user":user.id})
        db.close()

        # Giving Rendrill role if criteria satisfied
        if if_role:
            role = interaction.guild.get_role(Var.rendrill_role)
            await user.add_roles(role)

        await interaction.response.send_message(f"Updated.", ephemeral=True)

    async def view(self, interaction): 

        user = interaction.user
        # if user already has guardrill role
        if user.get_role(Var.rendrill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you already have the `rendrill` role. Thank you for your interest!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # Retrieving data from database
        db = Database("./data/criteria")
        data = db.select("role", where={"user":user.id})

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user":user.id})

        db.close()

        data = data[0]

        rc, wc = '❌', '✅'

        # Embed
        embed=discord.Embed(title="Rendrill Role Criteria", description="Complete all 3 tasks to get the Rendrill Role!", color=0xca4949)
        embed.add_field(name=f"{rc if data[1] < 4 else wc} Invite at least 4 users to the server", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc if data[2] < 4 else wc} Reach Lvl. 4 XP", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc if not data[3] else wc} Complete the Quiz (after 1 & 2)", value="ㅤ", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

        if data[1] >= 2 and data[2] >= 4 and not data[3]:
            await interaction.followup.send(content=f"Looks like you are almost eligible for obtaining the `Rendrill` role! To complete the quiz, go to <#{Var.rendrill_channel}> and click on the `GET RENDRILL` button and start the quiz!", ephemeral=True)

# Cog setup command
async def setup(bot):
    await bot.add_cog(Criteria(bot))