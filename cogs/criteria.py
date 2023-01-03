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

    async def req(self, interaction, user:discord.Member, activity:int, done:int):
        
        db = Database("./data/criteria")

        data = db.select("role", where={"user":user.id})

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user":user.id})

        data = data[0]
        
        a1 = 1 if (done and activity==1) or data[1] else 0
        a2 = 1 if (done and activity==2) or data[2] else 0
        a3 = 1 if (done and activity==3) or data[3] else 0

        role = 1 if a1 and a2 and a3 else 0

        print(a1, a2, a3, role)

        db.update("role", (user.id, a1, a2, a3, role))

        role = interaction.guild.get_role(1059870181096169503)
        await user.add_roles(role)

        await interaction.response.send_message(f"Updated.")

        db.close()

    @app_commands.command(name="view-req", description="View User's Criteria for Rendrill Role")
    async def view(self, interaction, user:discord.Member):
        db = Database("./data/criteria")
        data = db.select("role", where={"user":user.id})

        print(data)

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user":user.id})

        data = data[0]

        rc, wc = '❌', '✅'


        embed=discord.Embed(title="Rendrill Role Criteria", description="Complete all 3 tasks to get the Rendrill Role!", color=0xca4949)
        embed.add_field(name=f"{rc if not data[1] else wc} Help Exprorills", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc if not data[2] else wc} Support The Mandrills on Twitter", value="ㅤ", inline=False)
        embed.add_field(name=f"{rc if not data[3] else wc} Invite at least 2 users to the server", value="ㅤ", inline=False)
        
        await interaction.response.send_message(embed=embed)



        

        





async def setup(bot):
    await bot.add_cog(Criteria(bot))

