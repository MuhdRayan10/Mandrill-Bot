from discord.ext import commands
from discord import app_commands
from easy_sqlite3 import *
import random
import discord

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        db = Database("./data/levels")
        db.create_table("levels", {"user":INT, "level":INT, "xp":INT, 'lim':INT, 'total':INT})

        db.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        auth_id = message.author.id

        db = Database("./data/levels")

        if not db.if_exists("levels", where={"user":auth_id}):
            db.insert("levels", (auth_id, 0, 0, 100))

        levels = db.select("levels", where={"user":auth_id}, size=1)
        addition = 5 + random.choice([-1, 0, 1])

        if levels[2] >= levels[-1]:

            db.update("levels", {"level":levels[1]+1, "xp":levels[2] + addition - levels[1], "lim":levels[3] * 1.5, "total": levels[4]+addition},
                 where={"user":auth_id})

        else:
            db.update("levels", information={"xp":levels[2]+addition, "total":levels[4]+addition}, where={"user":auth_id})

        print(f"[LOG] - {message.author.name} - {levels[4]} XP")
        db.close()

    @app_commands.command(name="level", description="View user's level in the server")
    @app_commands.describe(user="The user to be viewed")
    async def level(self, interaction, user:discord.Member=None):
        
        user = user if user else interaction.user
        db = Database("./data/levels")
        
        if not db.if_exists("levels", {"user":user.id}):
            db.insert("levels", (user.id, 0, 0, 100))

        data = db.select("levels", where={"user":user.id})

        embed = discord.Embed(title=user.name, description=f"XP: {data[2]} \Level: {data[1]}")
        await interaction.response.send_message(embed=embed)



        






        



async def setup(bot):
    await bot.add_cog(XP(bot))
            
        
