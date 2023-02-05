from discord import app_commands
from discord.ext import commands
from discord import ui
import discord
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

        get_exprorill_button = ui.Button(label="Get Exprorill", style=discord.ButtonStyle.green, custom_id="exprorill:green")
        get_exprorill_button.callback = self.give_exprorill

        self.views = ui.View(timeout=None)
        self.views.add_item(get_exprorill_button)

        get_promdrill_button = ui.Button(label="Get Promdrill", style=discord.ButtonStyle.green, custom_id="promdrill:green")
        get_promdrill_button.callback = self.promdrill

        criteria = ui.Button(label="Criteria", style=discord.ButtonStyle.blurple, custom_id='requirements_prom:blurple')
        criteria.callback = self.view

        self.view2 = ui.View(timeout=None)
        self.view2.add_item(get_promdrill_button)
        self.view2.add_item(criteria)

        
    async def give_exprorill(self, interaction):

        exprorill_role = interaction.guild.get_role(Var.exprorill_role)
        unverified_role = interaction.guild.get_role(Var.mute_role)

        if unverified_role in interaction.user.roles:
            await interaction.response.send_message(f"Unfortunately you are still unverified... Go verify yourself at <#{Var.verification_channel}>", ephemeral=True)
        
        else:
            await interaction.user.add_roles(exprorill_role)
            await interaction.response.send_message(f"You are now officially an `Exprorill`!", ephemeral=True)


    @app_commands.command(name="setup-exprorill", description="[MODS] Setup exprorill role interface")    
    async def setup_exprorill(self, interaction):
        embed = discord.Embed(title='Get Exprorill', description='Click the button to get your Exprorill role.', color=Var.base_color)
        
        channel = interaction.guild.get_channel(Var.exprorill_channel)
        await channel.send(embed=embed, view=self.views)

    @app_commands.command(name="setup-promdrill", description="[MODS] Sets up promdrill interface.")
    async def setup_promdrill(self, interaction):
        embed = discord.Embed(title='Get Promdrill', description='Click the button to get your Promdrill role.', color=Var.base_color)
        
        channel = interaction.guild.get_channel(Var.promdrill_channel)
        await channel.send(embed=embed, view=self.view2)


    async def promdrill(self, interaction):
        user = interaction.user
        blurple_btn = discord.ButtonStyle.blurple

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

        if not(data[1] >= 8 and data[2] >= 8):

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
            title="Promdrill Questionnaire",
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
            result_embed.description = "Congratulations, you have passed the questionnaire!"
        else:
            result_embed.description = "Sorry, you have failed the questionnaire. Better luck next time."
        result_embed.add_field(name="Score", value=f"{score}/{len(questions)}")

        await interaction.followup.send(embed=result_embed, ephemeral=True)

        if passed:
            role = user.guild.get_role(Var.promdrill_role)
            await user.add_roles(role)

            await interaction.followup.send("You have been awarded the `Promdrill` Role!", ephemeral=True)
            return

        if score < 6:
            await user.timeout(timedelta(minutes=5))
            await interaction.followup.send("Due to a low score, you have been timed out for 5 minutes. Please try again later.", ephemeral=True)
            return

    async def view(self, interaction): 

        user = interaction.user
        # if user already has guardrill role
        if user.get_role(Var.promdrill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you already have the `promdrill` role. Thank you for your interest!"
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
        embed.add_field(name=f"{rc if data[1] < 8 else wc} Invite at least 8 users to the server", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc if data[2] < 8 else wc} Reach Lvl. 8 XP", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc} Complete the Quiz (after 1 & 2)", value="ㅤ", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

        if data[1] >= 2 and data[2] >= 4 and not data[3]:
            await interaction.followup.send(content=f"Looks like you are almost eligible for obtaining the `Rendrill` role! To complete the quiz, go to <#{Var.rendrill_channel}> and click on the `GET RENDRILL` button and start the quiz!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Roles(bot))

