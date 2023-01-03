from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='+', application_id="1059476420977504378")

async def load_cogs():
    for file in os.listdir('./cogs'):
        if file.endswith('.py') and "twitter" not in file:
            await bot.load_extension(f'cogs.{file[:-3]}')

@bot.event
async def on_ready():
    await load_cogs()
    print(f"Connected to discord as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Exploring..."))
    
    
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)
