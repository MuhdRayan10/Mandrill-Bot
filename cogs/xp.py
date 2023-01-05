from discord.ext import commands
from discord import app_commands
from easy_sqlite3 import *
import random
import discord
from easy_pil import Editor, Font, load_image_async, Canvas

from helpers import Var as V
Var = V()

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
            db.insert("levels", (auth_id, 0, 0, 100, 0))

        levels = db.select("levels", where={"user":auth_id}, size=1)
        xp = 5 + random.choice([-1, 0, 1])

        if levels[2] + xp >= levels[3]:
            db.update("levels", {"level":levels[1]+1, "xp":levels[2]+xp-levels[3], "lim":int(1.5*levels[3]), "total":levels[4]+xp},
                where={"user":auth_id})
            print(levels[2]+xp-levels[3])

        else:
            db.update("levels", {"xp":levels[2]+xp, "total":levels[4]+xp}, where={"user":auth_id})

        print(f"[LOG] - {message.author.name} - Lvl. {levels[1]} - {levels[2]+xp} XP")
        db.close()


    @app_commands.command(name="level", description="View user's level in the server")
    @app_commands.describe(user="The user to be viewed")
    async def level(self, interaction, user:discord.Member=None):
        
        user = user if user else interaction.user
        db = Database("./data/levels")
        
        if not db.if_exists("levels", {"user":user.id}):
            db.insert("levels", (user.id, 0, 0, 100, 0))

        data = db.select("levels", where={"user":user.id}, dict_format=True)
        db.close()

        bg = Editor(Canvas((900, 300), color="#141414"))
        profile_picture = await load_image_async(str(user.avatar.url))
        profile = Editor(profile_picture).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        card_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]
        bg.polygon(card_shape, color="#FFFFFF")
        bg.paste(profile, (30, 30))

        bg.rectangle((30, 220), width=650, height=40, color="#FFFFFF")
        bg.bar((30, 220), max_width=650, height=40, percentage=data["xp"]/data["lim"], color="#FFFFFF", radius=20)
        bg.text((200, 40), user.display_name, font=poppins, color="#FFFFFF")

        bg.rectangle((200, 100), width=350, height=2, fill="#FFFFFF")
        bg.text((200, 130), f"Level - {data['level']} | XP - {data['xp']}/{data['lim']}", font=poppins_small, color="#FFFFFF")

        file = discord.File(fp=bg.image_bytes, filename=f"{user.name}_level.png")
        await interaction.response.send_message(file=file)




        






        



async def setup(bot):
    await bot.add_cog(XP(bot))
            
        
