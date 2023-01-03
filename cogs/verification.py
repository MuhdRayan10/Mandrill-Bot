from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import discord, random, os
from var import mute_role, mute_time, base_color
from captcha.image import ImageCaptcha
from datetime import timedelta
from discord.ui import View


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

    # TODO: rayan add a permission check here
    @app_commands.command(name="start_verification")
    async def start_verification(self, interaction, channel: discord.TextChannel):
        await interaction.response.defer()
        
        embed = discord.Embed(title='Verify', description='Click the button to verify yourself.')
        verify_button = Button(
            label="Verify",
            style=discord.ButtonStyle.green
        )
        verify_button.callback = self.verify
        view = View()
        view.add_item(verify_button)

        await channel.send(embed=embed, view=view)
        await interaction.channel.send(f"Added verification app, to <#{channel.id}>")

    async def verify(self, interaction):
        # TODO: add exception to check if user is already verified

        await interaction.response.defer()

        cache[interaction.user.id] = ""
        correct = ''.join(random.choices(['A', 'B', 'C', 'D'], k=4))

        embed = discord.Embed(title="Captcha Verification", description="Click the buttons in the correct seqence to verify.", color=discord.Color(base_color))

        img = ImageCaptcha(width=280, height=90)
        img.generate(correct)

        img.write(correct, f"./data/captcha/{interaction.user.id}.png")

        f = discord.File(f"./data/captcha/{interaction.user.id}.png", filename="captcha.png")
        embed.set_image(url="attachment://captcha.png")

        msg = await interaction.followup.send(embed=embed, view=Captcha(interaction.user.id), file=f, ephemeral=True)

        def check(i):
            return i.data["component_type"] == 2 and "custom_id" in i.data.keys() and i.user.id == interaction.user.id

        embed = self.update_embed(embed, interaction.user.id)

        count = 4
        while count != 0:

            result = await self.bot.wait_for("interaction", check=check, timeout=30)
            
            if result is None:
                await interaction.followup.edit_message(msg.id, "Timeout", embed=None, view=None, ephemeral=True)
                return

            await result.response.defer()

            embed = self.update_embed(embed, interaction.user.id)

            await interaction.followup.edit_message(msg.id, embed=embed, view=Captcha(interaction.user.id))
            
            print(cache[interaction.user.id])

            count -= 1

        completed_embed = discord.Embed(title=f"{interaction.user.display_name} has {'not' if correct != cache[interaction.user.id] else ''} been verified!", color=discord.Color(base_color))
        completed_embed.set_image(url="attachment://captcha.png")

        if correct == cache[interaction.user.id]:
            del cache[interaction.user.id]
            await interaction.followup.edit_message(msg.id, view=None, embed=completed_embed)
        else:
            await interaction.followup.edit_message(msg.id, view=None, embed=completed_embed)
        
        del f
        os.remove(f"./data/captcha/{interaction.user.id}.png")
        
    def update_embed(self, embed:discord.Embed, user):
        embed.clear_fields()
        embed.add_field(name="User Input", value=cache[user])

        return embed

    async def verified(self, user):
        await user.timeout(timedelta(minutes=mute_time))
        await user.remove_roles(mute_role)

    @commands.command()
    async def sync(self, ctx):
        fmt = await ctx.bot.tree.sync()

        await ctx.send(f"Synced {len(fmt)} commands.")

async def setup(bot):
    await bot.add_cog(Verification(bot))
