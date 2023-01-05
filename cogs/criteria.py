from discord.ext import commands
from discord import app_commands
from discord import ui
import discord
from easy_sqlite3 import *

# Import stored variables
from helpers import Var as V
Var = V()

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

        get_rendrill_button.callback = self.ask_rendrill_questions # Link function called when button clicked.
        
        view = ui.View()
        view.add_item(get_rendrill_button)

        # Sending message
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Added `get rendrill` app, to <#{channel.id}>")

    async def ask_rendrill_questions(self, interaction):
        # testing for now
        async def send_question(interaction, question, stroptions):
            options = []
            for option in stroptions:
                opt = discord.SelectOption(label=option)
                options.append(opt)
            menu = ui.Select(
                placeholder="Select the Correct Answer!"
            )

            view = ui.View()
            view.add_item(menu)

            await interaction.response.send_message(
                content=question,
                view=view, 
                ephemeral=True
            )
        await send_question(interaction, "Hello!", ['a', 'b', 'c', 'd'])


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

