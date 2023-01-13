from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

from helpers import Var as V
Var = V()

# Getting required intents
intents = discord.Intents.all()
intents.message_content = True

class MandrillBot(commands.Bot):
    def __init__(self):

        super().__init__(intents=intents, command_prefix='+', application_id="1059476420977504378")
        self.added = False

    async def on_ready(self) -> None:
        await load_cogs()
        print(f"Connected to discord as {bot.user}")
        await bot.change_presence(activity=discord.Game(name="Exploring..."))

        if not self.added:

            from cogs.verification import Verification
            from cogs.criteria import Criteria
            from cogs.twitter import TwitterCog

            v, c, t = Verification(self), Criteria(self), TwitterCog(self)
            
            self.add_view(v.views)
            self.add_view(c.views)
            self.add_view(t.views)

            del v, c, t

bot = MandrillBot()

# Loading the cog files from cogs folder
async def load_cogs():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')


# Getting the token and runnning the bot
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)
