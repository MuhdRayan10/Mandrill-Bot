from discord.ext import commands
from discord import app_commands
import discord

class RoadMap(commands.Cog):
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
        
        file = discord.File(fp="./data/images/roadmap_stage1.png", filename="roadmap.png")
        embed.set_image(url=r"attachment://roadmap.png")
        embed.add_field(name="__Stage 2__", value="__Coming soon!__")

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(RoadMap(bot))
