import discord
from discord import app_commands
from discord.ext import commands
from discord import ui

from easy_sqlite3 import *
import random

from helpers import Var as V
Var = V()



class GiveawayCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

        db = Database("./data/giveaway.json")
        db.create_table("questions", {"ID":INT, "question":"TEXT", "options": "TEXT", "answer":"TEXT",
                                      "winner": "TEXT", "done":INT})

        db.close()

    async def send_giveaway(self):

        channel = self.bot.get_channel(Var.giveaway_channel)

        db = Database("./data/giveaway.json")
        question = db.select("giveaway", {"done":0}, size=1)

        db.close()

        letters = {1:'A', 2:'B', 3:'C', 4:'D'}
        correct = random.randint(0, 3)

        options = eval(question[2])
        options.insert(correct, question[2])
        
        options = [f'{letters[i]}) {x}' for i, x in enumerate(options)] 
        giveaway_embed = discord.Embed(title="Giveaway", description="Giveaway stuff")
        giveaway_embed.add_field(name=question[1], value='\n'.join(options))

        question_view = ui.View()

        for letter in letters.values():
            btn = ui.Button(label=letter, style=discord.ButtonStyle.green)
            question_view.add_item(btn)

            btn.callback = lambda l=letter:self.option_clicked(correct, l)

        await channel.send(embed=giveaway_embed, view=question_view)

    def option_clicked(self, correct, letter):
        pass
            





async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))
