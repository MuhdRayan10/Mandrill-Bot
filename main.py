from dotenv import load_dotenv
from discord.ext import commands
import discord
import os

# Getting required intents
intents = discord.Intents.all()
intents.message_content = True


class MandrillBot(commands.Bot):
    def __init__(self):

        super().__init__(intents=intents, command_prefix='+',
                         application_id="933686254250389535")
        self.added = False

    async def on_ready(self) -> None:
        print(f"Connected to discord as {bot.user}")
        await bot.change_presence(activity=discord.Game(name="Exploring..."))

        for file in os.listdir('./cogs'):
            if file.endswith('.py'):
                print(file)
                await bot.load_extension(f'cogs.{file[:-3]}')
                print(bot.cogs)

        from cogs.roles import Explorill, Purmarill
        views = [
            Explorill(self).view,
            Purmarill(self).view
        ]

        for view in views:
            self.add_view(view)

        del views


bot = MandrillBot()

load_dotenv()
TOKEN = os.getenv("TESTINGBOTTOKEN")
bot.run(TOKEN)
