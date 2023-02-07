from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import discord, random, os
from easy_pil import Editor, load_image_async, Font
from captcha.image import ImageCaptcha
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

        verify_button = Button(label="Verify", style=discord.ButtonStyle.green, custom_id="verification:green")
        verify_button.callback = self.discord_security # Verify function called when button clicked.

        self.views= View(timeout=None)
        self.views.add_item(verify_button)

    # This command is triggered everytime a user joins the server.
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        '''
            The aim of this function is to first mute the user on join, and then send
            the user a welcome message in the welcome channel.
        '''
        
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
        
        embed = discord.Embed(title="Welcome to The Mandrill's Server!", description=f"Hey {member.mention}, welcome to The Mandrills! Please make sure to <#{Var.verification_channel}> and <#{Var.explorill_channel}> role in order to interact with the server and community!", color=Var.base_color)
        embed.set_image(url="attachment://welcome.png")

        await channel.send(embed=embed, file=welcome_file)
        
        # Updating invites
        await update_invites(member, Var)

    # Sets up the interface for the Verification in a channel
    # Only for Moderators
    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-verification", description="[MODS] Create verification interface in specified channel.")
    @app_commands.describe(channel="The channel in which Verification should be set up")
    async def start_verification(self, interaction, channel: discord.TextChannel):
        
        # The Verify Embed
        embed = discord.Embed(title='Verify', description='Click the button to verify yourself.',color=Var.base_color)

        # Sending message
        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(f"Added `verification app`, to <#{channel.id}>")

    async def turn_off_dms_exponse(self, interaction):
        
        # Checking if the user is muted or not (if not, then already verified)
        role = interaction.guild.get_role(Var.mute_role)
        
        if role not in interaction.user.roles:
            await interaction.response.send_message("Already verified!", ephemeral=True)
            return

        embed = discord.Embed(title="Turn off DMs", description="To continue, you must turn off your DMs.", color=Var.base_color)
        embed.add_field(name="Why turn off DMs", value="This is to protect you from DM scams, DM advertisers, impersonators, etc.")
        embed.add_field(name="How to turn off DMs", value="1. Right-click on this server's icon\n2. Click on Privacy Settings\n3. Turn off direct messages\n4. Click on Done")

        view = View()
        proceed = Button(style=discord.ButtonStyle.green, label="Proceed")
        proceed.callback = self.discord_security
        view.add_item(proceed)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def discord_security(self, interaction):

        val = f"""  ㅤㅤ
        ➡️  The Mandrills will never DM you first. We recommend to Turn off "direct messages" from the server members

➡️  To navigate safe ONLY use <#{Var.official_links}> channel

➡️  Identify easily The Mandrills team members through our roles\n\n⚪ Liberators, 🔵 Guardrills & 🟠 Promdrills"""
        embed = discord.Embed(title="Discord Security", color=Var.base_color)
        embed.add_field(name="Please stay safe and take the time to review our security tips below.", value=val)

        view = View()
        proceed = Button(style=discord.ButtonStyle.green, label="Continue")
        proceed.callback = self.rules_exponse
        view.add_item(proceed)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def rules_exponse(self, interaction):
        embed = discord.Embed(title="Read the Rules", description="To continue, you must read and agree to the server rules.", color=Var.base_color)
        embed.add_field(name="Rules", value="1. Be respectful, civil, and welcoming.\n2. No inappropriate or unsafe content.\n3. Do not misuse or spam any of the channels.\n4. Do not join the server to promote your content.\n5. Any content that is NSFW is not allowed under any circumstances.\n6. Do not buy/sell/trade/give away anything.\n7. Do not use the server as a dating server.\n8. The primary language of this server is English.\n9. Discord names and avatars must be appropriate.\n10. Spamming in any form is not allowed.")

        view = View()
        proceed = Button(style=discord.ButtonStyle.green, label="Agree")
        proceed.callback = self.verify
        view.add_item(proceed)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def verify(self, interaction):
        '''
        This function takes care of all the Captcha verification process.
        It is called when user clicks the "Verify" Button. 
        '''

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
        embed = discord.Embed(title="Captcha Verification", description="Click the buttons in the correct sequence to verify.", color=Var.base_color)
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
        completed_embed = discord.Embed(title=f"{interaction.user.display_name} you have {'not ' if correct != cache[interaction.user.id] else ''}been verified! {'Please try again...' if correct != cache[interaction.user.id] else ''}", color=Var.base_color)
        completed_embed.set_image(url="attachment://captcha.png")

        await interaction.followup.edit_message(msg.id, embed=completed_embed, view=None)
        
        # Calling verified function if verified for timing out the user
        await self.verified(interaction.user, interaction.guild.get_role(Var.mute_role), interaction) if correct == cache[interaction.user.id] else None

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

    async def verified(self, user, role, inter):
        '''
            Giving roles after verification
        '''
        await user.remove_roles(role)
        await user.add_roles(inter.guild.get_role(Var.muted_role))

        await inter.followup.send(f"<#{Var.explorill_channel}> role in order to interact with the server and community.", ephemeral=True)

    # Syncing new commands
    @commands.command()
    async def sync(self, ctx):
        fmt = await ctx.bot.tree.sync()

        await ctx.send(f"Synced {len(fmt)} commands.")

# Setup call for cog
async def setup(bot):
    await bot.add_cog(Verification(bot))
