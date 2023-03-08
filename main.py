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

        super().__init__(intents=intents, command_prefix='+',
                         application_id="1059476420977504378")
        self.added = False

    async def on_ready(self) -> None:
        await load_cogs()
        print(f"Connected to discord as {bot.user}")
        await bot.change_presence(activity=discord.Game(name="Exploring..."))

        if not self.added:

            from cogs.verification import Verification
            from cogs.criteria import Criteria
            from cogs.twitter import TwitterCog
            from cogs.other_roles import Roles
            from cogs.games import Games
            from cogs.ticket import Tickets
            from cogs.collaborations import Collaborations
            from cogs.genesis import Genesis
            from cogs.giveaway import GiveawayCog

            views = (GiveawayCog(self), Genesis(self), Verification(self), Criteria(self), TwitterCog(self), Games(self),
                     Tickets(self), Collaborations(self), Roles(self))

            for view in views:
                self.add_view(view.views)

            self.add_view(views[-1].view2)  # roles 2
            self.add_view(views[-2].view2)  # collaborations 2
            self.add_view(views[-2].view3)  # collaborations 3
            self.add_view(views[-2].view4)

            del views


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
