from discord.ext import commands
from discord import app_commands
import discord

class RoadMap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roadmap", description="View our Roadmap!")
    async def roadmap(self, interaction):
        embed = discord.Embed(title="The Mandrills Roadmap", color=0x0000FF)
        embed.add_field(name="Stage 1: Minting Minerals", value="Three Phases of minting Minerals:\n- **1st Phase of Minting:** 1,111 Minerals Price: TBA\n- **2nd Phase of Minting:** 1,111 Minerals Price: TBA\n- **3rd Phase of Minting:** 1,111 Minerals Price: TBA\n- **Minting ONLY 1 Mineral per transaction**\n- **1,111 minerals** will be drawn in the various activities, where winners will be announced on the daily basis\nExchange Minerals into the Mandrills:\n- **Exchange has a deadline:** TBA\n- **Unexchanged Mandrills are burned forever**\n- Minerals are gaining its progressive utility in the 'Wild Network's' life.")
        with open("./data/images/roadmap_stage1.png", "rb") as f:
            file = discord.File(fp=f, filename="roadmap.png")
        embed.set_image(url=r"attachment://roadmap.png")
        embed.add_field(name="__Stage 2__", value="__Coming soon!__")


        await interaction.response.send_message(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(RoadMap(bot))
