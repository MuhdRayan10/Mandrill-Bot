from discord.ext import commands
from discord import app_commands
from discord import ui
import discord
from easy_sqlite3 import *

# Import stored variables
from helpers import Var as V
Var = V()

# chache for questionnaire
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

# Cog class
class Criteria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        db = Database("./data/criteria")
        db.create_table("role", {"user":INT, "a1":INT, "a2":INT, "a3":INT, "role":INT})

        db.close()

    @app_commands.command(name="setup-rendrill")
    async def setup_rendrill(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(title='Get Rendrill', description='Click the button to get your rendrill role.')
        get_rendrill_button = ui.Button(label="Get Rendrill", style=discord.ButtonStyle.green)

        get_rendrill_button.callback = self.rendrill_questionnaire # Link function called when button clicked.
        
        view = ui.View()
        view.add_item(get_rendrill_button)

        # Sending message
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Added `get rendrill` app, to <#{channel.id}>")

    async def rendrill_questionnaire(self, interaction):
        await interaction.response.defer()
    
        # TODO: check if user is eligible for CRITERIA ONE AND TWO
        questions = ['Who are the "Guardrills"?', 'How many Income percentages are distributed to the "Mandrills" owners in total?', 'What do you need to enter to out Metaverse?']
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

        # generate chache for user
        cache[interaction.user.id] = []

        # Creating Embed
        embed = discord.Embed(
            title="Rendrill Questionnaire",
            description="Answer the questions, accurately.",
            color=discord.Color(Var.base_color)
            )
        embed.add_field(
            name=questions[0], 
            value="\n".join(options[0]),
            )
        print()

        msg = await interaction.followup.send(embed=embed, view=QuestionnaireMenu(interaction.user.id), ephemeral=True)

        def check(i) -> True or False:
            return i.data['component_type'] == 2 and i.user.id == interaction.user.id

        # results of the questionare
        results = []

        # loop 3 times for 3 questions
        questionno = 1
        while questionno <= 3:
            # wait for button click
            result = await self.bot.wait_for("interaction", check=check, timeout=None)
            print(result)
            print(result.data)

            results.append(result.data['custom_id'])

            await result.response.defer()

            if questionno == 3:
                break

            # Updating embed and sending message
            embed.remove_field(0)
            embed.add_field(
                name=questions[questionno], 
                value="\n".join(options[questionno]),
            )
            await interaction.followup.edit_message(msg.id, embed=embed, view=QuestionnaireMenu(interaction.user.id))

            questionno += 1

        mark = sum([1 for i, opt in enumerate(results) if opt == correct_options[i]])

        result_embed = discord.Embed(
            title="Rendrill Questionnaire Results",
            description=f"""Marks: {mark}/3
            Passed: {True if mark == 3 else False}"""
        )

        await interaction.followup.edit_message(msg.id, embed=result_embed)


    # Command for Moderator to update user's criteria stats
    @app_commands.command(name="req", description="[MODS] Update user's criteria for acquiring Rendrill Role")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Help Exprorills", value=1),
        app_commands.Choice(name="Twitter", value=2),
        app_commands.Choice(name="Invite Members", value=3)
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


        if_role = 1 if a1 and a2 and a3 else 0

        db.update("role", {"user":user.id, "a1":a1, "a2":a2, "a3":a3, "role":if_role},
             where={"user":user.id})
        db.close()

        # Giving Rendrill role if criteria satisfied
        if if_role:
            role = interaction.guild.get_role(Var.rendrill_role)
            await user.add_roles(role)

        await interaction.response.send_message(f"Updated.", ephemeral=True)

    # Command to view user's criteria
    @app_commands.command(name="view-req", description="View User's Criteria for Rendrill Role")
    @app_commands.describe(user="The user whose criterias is to be viewed")
    async def view(self, interaction, user:discord.Member):
        
        # Retrieving data from database
        db = Database("./data/criteria")
        data = db.select("role", where={"user":user.id})

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user":user.id})

        data = data[0]

        rc, wc = '❌', '✅'

        # Embed
        embed=discord.Embed(title="Rendrill Role Criteria", description="Complete all 3 tasks to get the Rendrill Role!", color=0xca4949)
        embed.add_field(name=f"{rc if not data[1] else wc} Help Exprorills", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc if not data[2] else wc} Support The Mandrills on Twitter", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc if not data[3] else wc} Invite at least 2 users to the server", value="ㅤ", inline=False)
        
        await interaction.response.send_message(embed=embed)

# Cog setup command
async def setup(bot):
    await bot.add_cog(Criteria(bot))

