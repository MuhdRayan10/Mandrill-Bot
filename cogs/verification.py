from discord.ext import commands
from discord import app_commands
import discord, random
from var import verification_channel
from captcha.image import ImageCaptcha

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands(name="member-join")
    async def member_join(self, interaction):


        member = interaction.user
        channel = await self.bot.get_channel(verification_channel)

        img = ImageCaptcha(width=280, height=90)
        #img = img.generate(str(random.randint(1000, 9999)))

        img.write("")
        await channel.send()

        

async def setup(bot):
    await bot.add_cog(Verification(bot))
