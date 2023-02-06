from discord.ext import commands
from discord import app_commands
from easy_sqlite3 import *
import random, discord, mplcyberpunk, io
import matplotlib.pyplot as plt
from easy_pil import Editor, Font, load_image_async, Canvas
from time import strftime

from helpers import Var as V
Var = V()


async def level_up_message(message, levels):
    embed = discord.Embed(title="Level UP!", color=Var.base_color)
    embed.set_thumbnail(url=message.author.avatar.url)
    embed.add_field(name="User", value=message.author.mention)
    embed.add_field(name="Level", value=f"`{levels[1]+1}`")

    channel = message.guild.get_channel(Var.levelup_channel)
    await channel.send(embed=embed)


class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.spam_cache = {}

        db = Database("./data/levels")
        db.create_table("levels", {"user":INT, "level":INT, "xp":INT, 'lim':INT, 'total':INT})

        plt.style.use("cyberpunk")
        plt.rcParams["font.family"] = "monospace"

        db.close()
    
    def spam(self, user, time_):
        if user in self.spam_cache:
            return True if self.spam_cache[user][0] == time_ and self.spam_cache[user][1] >= 3 else False

        else:
            self.spam_cache[user] = (time_, 0)
            return True


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        auth_id = message.author.id
        time_ = strftime("%Y-%m-%d%H:%M")

        if self.spam(auth_id, time_): return

        new_time = self.spam_cache[auth_id][1] + 1 if time_ == self.spam_cache[auth_id][0] == time_ else 1
        self.spam_cache[auth_id] = (time_, new_time)

        db = Database("./data/levels")

        if not db.if_exists("levels", where={"user":auth_id}):
            db.insert("levels", (auth_id, 0, 0, 100, 0))

        levels = db.select("levels", where={"user":auth_id}, size=1)
        xp = 5 + random.choice([-1, 0, 1])

        if levels[2] + xp >= levels[3]:
            db.update("levels", {"level":levels[1]+1, "xp":levels[2]+xp-levels[3], "lim":int(Var.level_difficult_factor*levels[3]), "total":levels[4]+xp},
                where={"user":auth_id})
            
            db2 = Database("./data/criteria")
            if not db2.if_exists("role", where={"user":auth_id}):
                db2.insert("role", (auth_id, 0, 0, 0, 0))

            db2.update("role", {"a2":levels[1]+1}, {"user":auth_id})
            current_data = db2.select("role", where={"user":auth_id}, size=1)

            db2.close()

            await level_up_message(message, levels)
            
            if current_data[1] >=2 and current_data[2] >= 4 and not current_data[3]:
                await message.reply(f"Looks like you are almost eligible for the `Rendrill` role! To complete the quiz, go to <#{Var.rendrill_channel}> and click on the `GET RENDRILL` button to start the quiz!")

            
        else:
            db.update("levels", {"xp":levels[2]+xp, "total":levels[4]+xp}, where={"user":auth_id})

        print(f"[LOG] - {message.author.name} - Lvl. {levels[1]} - {levels[4]+xp} XP")
        db.close()


    @app_commands.command(name="level", description="View user's level in the server")
    @app_commands.describe(user="The user to be viewed")
    async def level(self, interaction, user:discord.Member=None):

        if interaction.channel.id != Var.command_channel:
            await interaction.response.send_message(f"Please use <#{Var.command_channel}> here", ephemeral=True)
            return
        
        user = user if user else interaction.user
        db = Database("./data/levels")
        
        if not db.if_exists("levels", {"user":user.id}):
            db.insert("levels", (user.id, 0, 0, 100, 0))

        data = db.select("levels", where={"user":user.id})[0]
        print(data)
        db.close()

        bg = Editor(Canvas((900, 300), color="#141414"))
        profile_picture = await load_image_async(str(user.avatar.url))
        profile = Editor(profile_picture).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        card_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]
        bg.polygon(card_shape, color=Var.hex1)
        bg.paste(profile, (30, 30))

        bg.bar((30, 220), max_width=650, height=40, color="#FFFFFF", radius=20, percentage=100)
        bg.bar((30, 220), max_width=650, height=40, percentage=data[2]*100/data[3], color=Var.hex2, radius=20)
        bg.text((200, 40), user.display_name, font=poppins, color="#FFFFFF")

        bg.rectangle((200, 100), width=350, height=2, fill="#FFFFFF")
        bg.text((200, 130), f"Level - {data[1]} | XP - {data[2]}/{data[3]}", font=poppins_small, color="#FFFFFF")

        file = discord.File(fp=bg.image_bytes, filename=f"{user.name}_level.png")
        await interaction.response.send_message(file=file)

    @app_commands.command(name="leaderboard", description="View the server's Top 10 Users")
    async def leaderboard(self, interaction):

        if interaction.channel.id != Var.command_channel:
            await interaction.response.send_message(f"Please use <#{Var.command_channel}> here", ephemeral=True)
            return
            
        db = Database("./data/levels")
        data = db.select("levels", selected=("user", "total"))
        data.sort(reverse=True, key= lambda x: x[1])

        if len(data) > 10: data = data[:10]

        def get_mem(member, xp):
            m = interaction.guild.get_member(member)
            return m if not m else (m.name, xp)

        data = [get_mem(d[0], d[1]) for d in data]
        data = [d for d in data if d is not None]

        plt.pie([d[1] for d in data], labels=[f"#{i} {d[0]}" for i,d in enumerate(data, start=1)], autopct='%1.2f%%',
            explode=[0.05 for _ in range(len(data))], shadow=True, textprops={'color': 'white', 'weight': 'bold', 'fontsize':14})
        plt.legend(title="Top 10 Users", loc='upper left', bbox_to_anchor=(-0.7, 1.12), prop={'size': 12, 'weight':'bold'})

        with io.BytesIO() as image_binary:
            plt.savefig(image_binary, format='png', bbox_inches='tight')
            image_binary.seek(0)

            embed = discord.Embed(title="Mandrill XP Leaderboard", color=Var.base_color)
            embed.set_image(url="attachment://image.png")
            
            await interaction.response.send_message(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        plt.close()
      
async def setup(bot):
    await bot.add_cog(XP(bot))