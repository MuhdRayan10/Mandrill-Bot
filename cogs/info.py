from discord.ext import commands
from discord import app_commands
from discord import ui
import discord

from helpers import Var as V
Var = V()

menu_pages = [
    {
        'title': 'Page 1',
        'fields': [
            {
                'name': '/req',
                'value': 'View your criteria for gaining the **Rendrill** role',
                'inline': False
            },
            {
                'name': '/level',
                'value': 'Get your XP level card for the server',
                'inline': False
            },
            {
                'name': '/leaderboard',
                'value': 'Get the server\'s XP Leaderboard (Top 10 Users)',
                'inline': False
            }
        ]
    },
    {
        'title': 'Page 2',
        'fields': [
            {
                'name': '/roadmap',
                'value': 'View the Mandrill roadmap',
                'inline': False
            },
            {
                'name': '/rules',
                'value': 'View the server rules',
                'inline': False
            },
            {
                'name': '/role-info',
                'value': 'Get information about the different roles in the server',
                'inline': False
            }
        ]
    }
]

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roadmap", description="Our Roadmap!")
    async def roadmap(self, interaction):

        if interaction.channel.id != Var.command_channel:
            await interaction.response.send_message(f"Please only use commands in <{Var.command_channel}>")
            return

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

        await interaction.followup.send(embed=embed, file=file, ephemeral=True)

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
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name='role-info', description="Info about the custom roles.")
    async def role_info(self, interaction):

        if interaction.channel.id != Var.command_channel:
            await interaction.response.send_message(f"Please only use commands in <{Var.command_channel}>")
            return

        embed = discord.Embed(title="Role Information", color=Var.base_color)

        explorills_description = f"<#{Var.exprorill_channel}>\nExprorills are the members who have not received any kind of role yet and are able to interact with the server and community."
        purmarills_description = f"<#{Var.purmarill_channel}>\nPurmarills are the members who have met the criteria to purchase the Mineral."
        rendrills_description = f"""<#{Var.rendrill_channel}>\nRendrills are the members who already gained Purmarill role and met the criteria to participate in the "#wheel-of-fortune" for the chance to win one of the prize from the list: 

1)  1,111 $LEF - Native coin of the "Wild Network" 
2)  Mineral 
3) "Wild Network" NFT Comics Series "Chronicles of the Ten unique Flowers" (First Edition) 
4)  "Wild Network" Branded Merch & Physical Artwork (First Edition) 
or Try Again in 7 Days 

The First 50 person who gains the role of the Rendrill, have a choice to take guaranteed Mineral or Spin the Wheel 
"""
        promdrills_description = f"""<#{Var.promdrill_channel}>\nPromdrills are the members who already got the all three roles and became supporters of the project. 
Helping new members, keeping chats active and secure, sharing new pieces of information and taking care of the project in general. 

Rewards and Benefits:
1) Stable monthly salary from the project
2) Bonus from every phase of successful minting
3) Guaranteed 5 Mineral during each phase 
4) 44,444 $LEF - Native coin of the "Wild Network" 
"""
        guardrills_description = "Guardrills are the Admins of the Discord, protectors and the most necessary figures."
        liberators_description = "The Liberators will lead the project for the rest of the journey."

        embed.add_field(name="Exprorills", value=explorills_description, inline=False)
        embed.add_field(name="Purmarills", value=purmarills_description, inline=False)
        embed.add_field(name="Rendrills", value=rendrills_description, inline=False)
        embed.add_field(name="Promdrills", value=promdrills_description, inline=False)
        embed.add_field(name="Guardrills", value=guardrills_description, inline=False)
        embed.add_field(name="Liberators", value=liberators_description, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    def create_help_menu_embed(self, page) -> discord.Embed:
        embed = discord.Embed(title="Commands Info", description=page['title'], color=Var.base_color)
        for field in page['fields']:
            embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
        return embed

    @app_commands.command(name="help", description="List of all the server commands")
    async def help(self, interaction):

        if interaction.channel.id != Var.command_channel:
            await interaction.response.send_message(f"Please only use commands in <{Var.command_channel}>")
            return

        await interaction.response.defer()

        # Set the current page to the first page of the menu
        current_page = 0
        

        menu_view = ui.View()
        prev = ui.Button(style=discord.ButtonStyle.blurple, emoji="⬅️", custom_id="previous")
        menu_view.add_item(prev)
        nxt = ui.Button(style=discord.ButtonStyle.blurple, emoji="➡️", custom_id="next")
        menu_view.add_item(nxt)

        def check(i) -> bool:
            return i.data['component_type'] == 2 and i.user.id == interaction.user.id

        # Create the embed for the current page
        embed = self.create_help_menu_embed(menu_pages[current_page])

        # Send the embed message
        helpmsg = await interaction.followup.send(embed=embed, view=menu_view, ephemeral=True)

        for _ in range(100): # buffer of 100 interactions
            # Create the embed for the current page
            embed = self.create_help_menu_embed(menu_pages[current_page])

            await interaction.followup.edit_message(helpmsg.id, embed=embed, view=menu_view)

            btn = await self.bot.wait_for("interaction", check=check, timeout=None)

            if btn.data["custom_id"] == 'next':
                if current_page == len(menu_pages)-1:
                    interaction.response.defer()

                current_page += 1
            elif btn.data["custom_id"] == "previous":
                if current_page == 0:
                    interaction.response.defer()

                current_page -= 1
        
        return interaction

    @app_commands.command(name="official-links", description="List of all the official links")
    async def link(self, interaction):

        if interaction.channel.id != Var.command_channel:
            await interaction.response.send_message(f"Please only use commands in <{Var.command_channel}>")
            return

        embed = discord.Embed(title="Official Links")
        embed.add_field(name="YouTube", value="[@TheMandrillsNFT](https://youtube.com/@TheMandrillsNFT)")
        embed.add_field(name="Discord", value="[Join the server](https://discord.gg/3mpVeVyRJD)")
        embed.add_field(name="Twitter", value="[@TheMandrillsNFT](https://twitter.com/TheMandrillsNFT)")
        embed.add_field(name="Website", value="[themandrills.xyz](https://www.themandrills.xyz)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        return


async def setup(bot):
    await bot.add_cog(Info(bot))

