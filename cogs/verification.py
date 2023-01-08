from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import discord, random, os
from easy_pil import Editor, load_image_async, Font
from captcha.image import ImageCaptcha
from datetime import timedelta
from discord.ui import View
from functions import update_invites

# Import stored variables
from helpers import Var as V
Var = V()

# Dictionary of user input on captcha
cache = {}

# Some variables
style = discord.ButtonStyle.blurple

# The function to be called to create welcome banner image
async def create_image(user):
    '''    This function creates the Welcome Banner Image that gets shown in 
    the welcome channel.    '''

    bg = Editor("./data/images/bg.png")

    profile_image = await load_image_async(str(user.avatar.url))
    profile = Editor(profile_image).resize((150, 150)).circle_image()
    
    poppins = Font.poppins(size=30, variant="bold")
    poppins_small = Font.poppins(size=20, variant="light")

    bg.paste(profile, (225, 100))
    bg.ellipse((225, 100), 150, 150, outline="white", stroke_width=5)

    bg.text((300, 275), f"WELCOME TO {user.guild.name}", color="white", font=poppins, align="center")
    bg.text((300, 325), f"{user.display_name}", color="white", font=poppins_small, align="center")

    return bg.image_bytes # Returning the image as bytes

# The View of Buttons for the Captcha verification process
class Captcha(View):
    def __init__(self, userid):
        super().__init__(timeout=15)
        self.userid = userid

    @discord.ui.button(label="A", style=style)
    async def a(self, __, _):
        cache[self.userid] += "A"

    @discord.ui.button(label="B", style=style)
    async def b(self, __, _):
        cache[self.userid] += "B"

    @discord.ui.button(label="C", style=style)
    async def c(self, __, _):
        cache[self.userid] += "C"

    @discord.ui.button(label="D", style=style)
    async def d(self, __, _):
        cache[self.userid] += "D"


# Cog class
class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot   

    # This command is triggered everytime a user joins the server.
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        '''
            The aim of this function is to first mute the user on join, and then send
            the user a welcome message in the welcome channel.
        '''

        channel = discord.utils.get(member.guild.channels, id=Var.member_stats_channel)
        await channel.edit(name=f"👤 Members: {len(member.guild.members)}")
        
        # Getting the muted role / Creating if it doesn't exist
        role = member.guild.get_role(Var.mute_role)

        if not role:
            role = discord.utils.get(member.guild.roles, name="not verified")

        # Adding the muted role to the newly joined user
        await member.add_roles(role)

        # Sending welcome message to user in the welcome channel
        channel = self.bot.get_channel(Var.welcome_channel)
        img = await create_image(member)

        welcome_file = discord.File(fp=img, filename="welcome.png")
        
        embed = discord.Embed(title="Welcome to The Mandrill's Server!", description=f"Hello {member.mention}, we're glad to have you here! Go verify at <#{Var.verification_channel}>", color=Var.base_color)
        embed.set_image(url="attachment://welcome.png")
        await channel.send(embed=embed, file=welcome_file)

        # Updating invites
        await update_invites(member, Var)

    @commands.Cog.listener()
    async def on_member_leave(self, member:discord.Member):
        channel = discord.utils.get(member.guild.channels, id=Var.member_stats_channel)
        await channel.edit(name=f"👤 Members: {len(member.guild.members)}")

    # Sets up the interface for the Verification in a channel
    # Only for Moderators
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="setup-verification", description="[MODS] Create verification interface in specified channel.")
    @app_commands.describe(channel="The channel in which Verification should be set up")
    async def start_verification(self, interaction, channel: discord.TextChannel):
        
        # The Verify Embed
        embed = discord.Embed(title='Verify', description='Click the button to verify yourself.')
        verify_button = Button(label="Verify", style=discord.ButtonStyle.green)
        verify_button.callback = self.verify # Verify function called when button clicked.
        
        view = View()
        view.add_item(verify_button)

        # Sending message
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Added `verification app`, to <#{channel.id}>")

    async def verify(self, interaction):
        '''
        This function takes care of all the Captcha verification process.
        It is called when user clicks the "Verify" Button. 
        '''

        # Checking if the user is muted or not (if not, then already verified)
        role = interaction.guild.get_role(Var.mute_role)
        
        if role not in interaction.user.roles:
            await interaction.response.send_message("Already verified!", ephemeral=True)
            return

        await interaction.response.defer()

        # Generating correct captcha message
        cache[interaction.user.id] = ""
        correct = ''.join(random.choices(['A', 'B', 'C', 'D'], k=4))

        # Creating Image
        img = ImageCaptcha(width=280, height=90)
        img.generate(correct)

        img.write(correct, f"./data/captcha/{interaction.user.id}.png")
        f = discord.File(f"./data/captcha/{interaction.user.id}.png", filename="captcha.png")

        # Creating Embed
        embed = discord.Embed(title="Captcha Verification", description="Click the buttons in the correct seqence to verify.", color=discord.Color(Var.base_color))
        embed.set_image(url="attachment://captcha.png")

        msg = await interaction.followup.send(embed=embed, view=Captcha(interaction.user.id), file=f, ephemeral=True)

        # Check command to see if any Interaction is the correct button click
        def check(i):
            return i.data["component_type"] == 2 and "custom_id" in i.data.keys() and i.user.id == interaction.user.id

        embed = self.update_embed(embed, interaction.user.id)

        # Looping 4 times for getting 4 characters as user input for captcha verification
        count = 4
        while count != 0:
            
            #Waiting for button click
            result = await self.bot.wait_for("interaction", check=check, timeout=15)
            
            # If timed out
            if result is None:
                await interaction.followup.edit_message(msg.id, "Timeout", embed=None, view=None, ephemeral=True)
                return

            await result.response.defer()

            # Updating embed and sending message
            embed = self.update_embed(embed, interaction.user.id)
            await interaction.followup.edit_message(msg.id, embed=embed, view=Captcha(interaction.user.id))

            count -= 1
 
        # Embed once Captcha is completed
        completed_embed = discord.Embed(title=f"{interaction.user.display_name} has {'not' if correct != cache[interaction.user.id] else ''} been verified!", color=discord.Color(Var.base_color))
        completed_embed.set_image(url="attachment://captcha.png")

        await interaction.followup.edit_message(msg.id, embed=completed_embed, view=None)
        
        # Calling verified function if verified for timing out the user
        await self.verified(interaction.user, interaction.guild.get_role(Var.mute_role), interaction.guild.get_role(Var.exprorill_role)) if correct == cache[interaction.user.id] else None

        # Deleting cached memory
        del f, cache[interaction.user.id]
        os.remove(f"./data/captcha/{interaction.user.id}.png")
        
    def update_embed(self, embed:discord.Embed, user):
        '''
        Function for updating embed once user has clicked a button to show user input
        '''

        embed.clear_fields()
        embed.add_field(name="User Input", value=cache[user])

        return embed

    async def verified(self, user, role, role2):
        '''
            Timing out user for specified time after verification
        '''
        await user.timeout(timedelta(minutes=Var.mute_time))
        await user.remove_roles(role)

        await user.add_roles(role2)


    # Syncing new commands
    @commands.command()
    async def sync(self, ctx):
        fmt = await ctx.bot.tree.sync()

        await ctx.send(f"Synced {len(fmt)} commands.")

# Setup call for cog
async def setup(bot):
    await bot.add_cog(Verification(bot))
