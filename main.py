from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

from helpers import Var as V
Var = V()

# Getting required intents
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='+', application_id="1059476420977504378")

# Loading the cog files from cogs folder
async def load_cogs():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')

@bot.event
async def on_ready():
    await load_cogs()
    print(f"Connected to discord as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Exploring..."))

    # server stats
    for guild in bot.guilds:
        # members
        channel = discord.utils.get(guild.channels, id=Var.member_stats_channel)
        await channel.edit(name=f"👤 Members: {len(guild.members)}")

# Getting the token and runnning the bot
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)
