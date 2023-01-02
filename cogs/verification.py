from discord.ext import commands
from discord import app_commands
import discord, random
from var import verification_channel, mute_role
from captcha.image import ImageCaptcha
from datetime import timedelta
from discord.ui import View
import asyncio

cache = {}


class Captcha(View):
    def __init__(self, userid):
        super().__init__(timeout=15)
        self.userid = userid

    @discord.ui.button(label="A", style=discord.ButtonStyle.blurple)
    async def a(self, __, _):
        cache[self.userid] += "A"

    @discord.ui.button(label="B", style=discord.ButtonStyle.blurple)
    async def b(self, __, _):
        cache[self.userid] += "B"

    @discord.ui.button(label="C", style=discord.ButtonStyle.blurple)
    async def c(self, __, _):
        cache[self.userid] += "C"

    @discord.ui.button(label="D", style=discord.ButtonStyle.blurple)
    async def d(self, __, _):
        cache[self.userid] += "D"

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True



class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        
        await member.add_roles(mute_role)


    @app_commands.command(name="verify")
    async def verify(self, interaction):
        cache[interaction.user.id] = ""
        correct = ''.join(random.choices(['A', 'B', 'C', 'D'], k=4))

        embed = discord.Embed(title="Embed", description=correct)
        
        await interaction.response.send_message(embed=embed, view=Captcha(interaction.user.id))

        def check(m):
            return True

        print(cache[interaction.user.id])

        count = 3
        while count != 0:
            result = await self.bot.wait_for("button", check=check, timeout=15)
            if result is None:
                await interaction.response.edit_message("Timeout", embed=None, view=None)
                return
            await interaction.response.edit_message(embed=embed, view=Captcha(interaction.user.id))
            print(cache[interaction.user.id])
            count -= 1

        if correct == cache[interaction.user.id]:
            del cache[interaction.user.id]
            await interaction.response.edit_message("Verified", view=None, embed=None)
        else:
            await interaction.response.edit_message("Not Verified", view=None, embed=None)

    @commands.command()
    async def sync(self, ctx):
        fmt = await ctx.bot.tree.sync()

        await ctx.send(f"Synced {len(fmt)} commands.")

        


async def setup(bot):
    await bot.add_cog(Verification(bot))
