from discord.ext import commands
from discord import app_commands
from helpers import Var as V
import discord

Var = V()

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roadmap", description="View our Roadmap!")
    async def roadmap(self, interaction):
        await interaction.response.defer()

        embed = discord.Embed(title="The Mandrills Roadmap", color=0x0000FF)
        lines = """Three Phases of minting Minerals:
- **1st Phase of Minting:** 1,111 Minerals Price: TBA
- **2nd Phase of Minting:** 1,111 Minerals Price: TBA
- **3rd Phase of Minting:** 1,111 Minerals Price: TBA
- **Minting ONLY 1 Mineral per transaction**
- **1,111 minerals** will be drawn in the various activities, where winners will be announced on the daily basis


__Exchange Minerals into the Mandrills:__
- **Exchange has a deadline:** TBA
- **Unexchanged Mandrills are burned forever**
- Minerals are gaining its progressive utility in the **'Wild Network's'** life."""

        embed.add_field(name="Stage 1: Minting Minerals", value=lines)
        
        file = discord.File(fp="./data/images/roadmap_stage1.jpg", filename="roadmap.jpg")
        embed.set_image(url="attachment://roadmap.jpg")
        embed.add_field(name="__Stage 2__", value="__Coming soon!__")

        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="rules", description="The Mandrill server rules")
    async def rules(self, interaction):
        embed = discord.Embed(title="Rules", color=Var.base_color)
        rules = """-Be respectful, civil, and welcoming.
-No inappropriate or unsafe content.
-Do not misuse or spam in any of the channels.
-Do not join the server to promote your content.
-Any content that is NSFW is not allowed under any circumstances.
-Do not buy/sell/trade/give away anything.
-Do not use the server as a dating server.
-The primary language of this server is English.
-Discord names and avatars must be appropriate.
-Spamming in any form is not allowed."""
        
        for rule in rules.split("\n"):
            embed.add_field(name=rule, value="a", inline=False)

        await interaction.response.send_message(embed=embed)
    



async def setup(bot):
    await bot.add_cog(Info(bot))
