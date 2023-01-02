from discord.ext import commands
from discord import app_commands
import discord, random
from var import verification_channel
from captcha.image import ImageCaptcha
from datetime import timedelta

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        
        await member.timeout(until=timedelta(minutes=5))
        channel = await self.bot.get_channel(verification_channel)
        


async def setup(bot):
    await bot.add_cog(Verification(bot))
