from discord.ext import commands
from discord import app_commands
from helpers import Var as V
import discord

Var = V()

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roadmap", description="Our Roadmap!")
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

    @app_commands.command(name="rules", description="Our server rules.")
    async def rules(self, interaction):
        embed = discord.Embed(title="Rules", color=Var.base_color)
        rules = """- **Be respectful, civil, and welcoming.**
- **No inappropriate or unsafe content.**
- **Do not misuse or spam in any of the channels.**
- **Do not join the server to promote your content.**
- **Any content that is NSFW is not allowed under any circumstances.**
- **Do not buy/sell/trade/give away anything.**
- **Do not use the server as a dating server.**
- **The primary language of this server is English.**
- **Discord names and avatars must be appropriate.**
- **Spamming in any form is not allowed.**"""
        
        embed.add_field(name="The rules of our server.", value=rules, inline=True)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='role-info', description="Info about the custom roles.")
    async def role_info(self, interaction):
        embed = discord.Embed(title="Role Information", color=Var.base_color)

        explorills_description = "Explorills are members who have not completed any development steps. They only watch the march and share the ecosystem."
        purmarills_description = "Purmarills are members who have met the criteria, passed the # get purmarill graph, and have permission to purchase the project's product."
        rendrills_description = "Rendrills are members who have completed both #get purmarill and #get rendrill and are eligible to purchase a mineral and also spin the #wheel of fortune where they can drop a free mineral and other exciting prizes."
        promdrills_description = "Promdrills are members who have gone through all areas of development graphs and they are helping new members, keeping chats active, sharing new pieces of information, and helping the project for more population."
        guardrills_description = "Guardrills are members who are developers of the project, protectors and the most necessary figures."
        liberators_description = "The Liberators will lead the project for the rest of the journey."

        embed.add_field(name="Explorills", value=explorills_description, inline=False)
        embed.add_field(name="Purmarills", value=purmarills_description, inline=False)
        embed.add_field(name="Rendrills", value=rendrills_description, inline=False)
        embed.add_field(name="Promdrills", value=promdrills_description, inline=False)
        embed.add_field(name="Guardrills", value=guardrills_description, inline=False)
        embed.add_field(name="Liberators", value=liberators_description, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
    
