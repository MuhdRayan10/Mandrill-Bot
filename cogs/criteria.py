from discord.ext import commands
from discord import app_commands
import discord
from easy_sqlite3 import *

# import stored variables
from helpers import StaticVariables

class Criteria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        db = Database("./data/criteria")
        db.create_table("role", {"user":INT, "a1":INT, "a2":INT, "a3":INT, "role":INT})

        db.close()

    @app_commands.command(name="criteria")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Help Exprorills", value=1),
        app_commands.Choice(name="Twitter", value=2),
        app_commands.Choice(name="Invite Members", value=3)
    ])
    @app_commands.choices(done=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
    ])
    async def criteria(self, interaction, user:discord.Member, activity:int, done:int):
        
        db = Database("./data/criteria")

        data = db.select("role", where={"user":user.id}, size=1)[0]
        
        a1 = 1 if (done and activity==1) or data[1] else 0
        a2 = 1 if (done and activity==2) or data[2] else 0
        a3 = 1 if (done and activity==3) or data[3] else 0

        role = True if a1 and a2 and a3 else False

        db.insert("role", (user.id, a1, a2, a3, role))

        role = interaction.guild.get_role(StaticVariables.rendrill_role)
        await user.add_roles(role)

        await interaction.response.send_message(f"Updated.")

        db.close()

async def setup(bot):
    await bot.add_cog(Criteria(bot))

