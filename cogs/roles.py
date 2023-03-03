import discord
from discord import ui
from discord import app_commands
from discord.ext import commands

from easy_sqlite3 import *
from cogs.web3 import Web3

from functions import update_criterias
import json
from datetime import timedelta

# global config variables
from helpers import Var
Var = Var()


class Explorill(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.view = ui.View(timeout=None)
        button = ui.Button(
            label="Get Explorill", style=discord.ButtonStyle.green, custom_id="explorill:green")
        button.callback = self.give_explorill

        self.view.add_item(button)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup", description="[MODS] Setup explorill role interface")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        embed = discord.Embed(
            title='Click the button to get your Explorill role', color=Var.base_color)

        await channel.send(embed=embed, view=self.view)
        await interaction.response.send_message(content=f"Added Explorill Interface to <#{channel.id}>.", ephemeral=True)

        return

    async def give_explorill(self, interaction: discord.Interaction):

        explorill_role = interaction.guild.get_role(Var.explorill_role)
        unverified_role = interaction.guild.get_role(Var.mute_role)

        roles = interaction.user.roles

        if unverified_role in roles:
            await interaction.response.send_message(f"Unfortunately, you are still unverified. Please verify yourself at <#{Var.verification_channel}>.", ephemeral=True)
            return

        if explorill_role in roles:
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already an `Exporill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        else:
            await interaction.user.add_roles(explorill_role)
            await interaction.response.send_message(f"You are now officially an `Explorill`!", ephemeral=True)
            await interaction.user.remove_roles(interaction.guild.get_role(Var.muted_role))

        return


def validify_wallet(wallet: str):
    """Checks if the wallet ID is a valid web3 address.\nTODO: Change to FLR Address using FLR API."""
    return Web3.isAddress(wallet)


class PurmarillVerificationModal(ui.Modal, title='Purmarill Verification'):
    twitter_username = ui.TextInput(
        label="Twitter Username",
        placeholder="Enter your twitter username (without the handle)",
        style=discord.TextStyle.short
    )
    wallet_id = ui.TextInput(
        label="Wallet Address",
        placeholder='Enter your FLR wallet address',
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:

        # Checking if twitter / walled account / user already exists db
        role = interaction.guild.get_role(Var.purmarill_role)
        if role in interaction.user.roles:
            await interaction.response.send_message("Twitter account / Wallet ID already registered...", ephemeral=True)
            return

        # check if the twitter is valid
        if not Web3(bot=None).validify_twitter(str(self.twitter_username)):
            await interaction.response.send_message("Twitter username does not exist.", ephemeral=True)
            return

        # checks if it is a valid wallet address
        if not validify_wallet(str(self.wallet_id)):
            await interaction.response.send_message("FLR address is not valid.", ephemeral=True)
            return

        db = Database("./data/data")
        db.insert("users", (interaction.user.id, interaction.user.name, str(
            self.twitter_username), str(self.wallet_id)))
        await interaction.response.send_message("You are now officially a Purmarill!", ephemeral=True)

        await interaction.user.add_roles(role)

        db.close()


class Purmarill(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.view = ui.View(timeout=None)

        button = ui.Button(
            label="Get Purmarill", style=discord.ButtonStyle.green, custom_id="purmarill:green")
        button.callback = self.give_purmarill

        self.view.add_item(button)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup", description="[MODS] Setup purmarill role interface")
    async def setup(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(
            title='Click the button to get your Purmarill role', color=Var.base_color)

        # Sending message
        await channel.send(embed=embed, view=self.view)
        await interaction.response.send_message(content=f"Added Explorill Interface to <#{channel.id}>.", ephemeral=True)

        return

    async def give_purmarill(self, interaction: discord.Interaction):

        if interaction.user.get_role(Var.purmarill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already a `Purmarill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        elif not interaction.user.get_role(Var.explorill_role):
            embed = discord.Embed(
                title="Required Role",
                description=f"First you have to <#{Var.explorill_channel}> role to be a `Purmarill`!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # send modal when link is called
        await interaction.response.send_modal(PurmarillVerificationModal())


cache = {}


class QuestionnaireMenu(ui.View):
    def __init__(self, userid):
        super().__init__(timeout=None)
        self.userid = userid

    @discord.ui.button(label="A", style=discord.ButtonStyle.blurple, custom_id='A')
    async def a(self, __, _):
        cache[self.userid].append("A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.blurple, custom_id='B')
    async def b(self, __, _):
        cache[self.userid].append("B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.blurple, custom_id='C')
    async def c(self, __, _):
        cache[self.userid].append("C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.blurple, custom_id='D')
    async def d(self, __, _):
        cache[self.userid].append("D")


class Rendrill(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.view = ui.View(timeout=None)

        # create table in db
        db = Database("./data/criteria")
        db.create_table("role", {"user": INT, "a1": INT,
                        "a2": INT, "a3": INT, "role": INT})
        db.close()

        button = ui.Button(
            label="Get Rendrill", style=discord.ButtonStyle.green, custom_id="rendrill:green")
        button.callback = self.alert

        criteria = ui.Button(
            label="Criteria", style=discord.ButtonStyle.blurple, custom_id='requirements:blurple')
        criteria.callback = self.view_criteria

        self.view.add_item(button)
        self.view.add_item(criteria)

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup", description="[MODS] Setup the rendrill button in the channel specified")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Sets up the Rendrill interface in the particular channel."""

        # The Verify Embed
        embed = discord.Embed(
            title='Click the button to get your Rendrill role', color=Var.base_color)

        # Sending message
        await channel.send(embed=embed, view=self.view)
        await interaction.response.send_message(f"Added `Rendrill` role interface, to <#{channel.id}>", ephemeral=True)

    async def alert(self, interaction: discord.Interaction):
        """Alerts the user on details about the quiz."""
        if interaction.user.get_role(Var.rendrill_role):
            embed = discord.Embed(
                title="Role already assigned",
                description="It looks like you are already a `Rendrill`!", color=Var.base_color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        elif not interaction.user.get_role(Var.purmarill_role):
            embed = discord.Embed(
                title="Required Role",
                description=f"First you have to <#{Var.purmarill_channel}> role to be a `Rendrill`!", color=Var.base_color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # check if user is eligible
        eligiblity = self.eligibility_check(interaction.user.id)

        if not eligiblity:
            embed = discord.Embed(
                description="It seems that you haven't finished all three tasks. Please click on the \"Criteria\" button.")

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="You are about to start the Quiz!", color=Var.base_color)
        embed.add_field(name="Have in mind that:", value="""- You have to answer all questions correctly in order to get the Rendrill role
- You will have the second chance in 24 hours
- Read carefully, don’t rush and Good Luck!""")

        ready_button = ui.Button(
            label="I'm ready!", style=discord.ButtonStyle.green)
        ready_button.callback = self.questionare

        view = ui.View(timeout=None)
        view.add_item(ready_button)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def questionnaire(self, interaction: discord.Interaction):
        """Questionnaire for the rendrill role."""

        # question data
        questions = [
            'How did The Mandrills come into being?',
            'Why are the Minerals so important elements in the Wild Network\'s Life?',
            'How many Minerals and Mandrills must the user HOLD in order to get free Copy of the "Wild Network" NFT Comics Series "Chronicles of the Ten unique Flowers" every month based on the snapshot?',
            'How many comics series will be there in total and copies in each month?'
        ]
        options = [
            ['(A) With a spaceship from the Galaxy', '(B) Through minerals evolution over time',
             '(C) They are just generated NFTs - "You\'re quite wrong"', '(D) They just spawned from nowhere'],

            ['(A) They are expensive due to scarcity - "It\'s true, but the reason for that is their usefulness"', '(B) Minerals are so magical and enchanting, you want to hold them all the time - "It\'s also true, but importance comes from their actual daily use cases, therefore progressive demand and value is guaranteed."', '(C) They are gaining progressive utility in the Wild Network\'s life because they hold vitality power. Minerals are the ONE and ONLY source of Metaverse energy',
             '(D) I can awaken mandrills with the help of minerals, but the mineral will be melted in that case - "Now that is the question! To be or not to be! It is up to you to decide what is more important to you, keep the mineral or use it to awaken the mandrill! BTW did you know that to join the Metaverse or buy land there, you must hold at least one species of the Wild Network, for example, the mandrill. Each species is eligible to purchase one land."'],

            ['(A) 4 Minerals and 4 Mandrills', '(B) 5 Minerals and 5 Mandrills',
             '(C) 8 Minerals and 8 Mandrills', '(D) 21 Minerals and 21 Mandrills'],

            ['(A) Total 12 series with 555 copies of NFT in each month', '(B) Total 4 series with 444 copies of NFT in each month',
             '(C) Total 8 series with 888 copies of NFT in each month', '(D) Total 21 series with 1,111 copies of NFT in each month']
        ]
        correct_options = [
            'B',
            'C',
            'B',
            'A'
        ]

        q_embed = discord.Embed(
            title='Choose the answer carefully.', color=Var.base_color
        )

        def _check(i) -> bool:
            return i.data['component_type'] == 2 and i.user.id == interaction.user.id

        score = 0
        for i, question in enumerate(questions):
            q_embed.remove_field(0)

            # Add question and options to the embed
            q_embed.add_field(name=question, value="\n".join(options[i]))

            # Create view with buttons for each option
            before_answer_view = ui.View()
            for j, _ in enumerate(options[i]):
                before_answer_view.add_item(ui.Button(
                    # Option letter, e.g. 'A', 'B', 'C'
                    custom_id=chr(ord('A') + j),
                    label=chr(ord('A') + j),
                    style=discord.ButtonStyle.blurple
                ))

            # Send question message and wait for button click
            question_message = await interaction.followup.send(embed=q_embed, view=before_answer_view, ephemeral=True)
            result = await self.bot.wait_for("interaction", check=_check, timeout=None)
            await result.response.defer()

            # Create view with colored buttons
            question_wrong_view = ui.View()
            for j, _ in enumerate(options[i]):
                question_wrong_view.add_item(ui.Button(
                    custom_id=chr(ord('A') + j),
                    label=chr(ord('A') + j),
                    style=discord.ButtonStyle.grey,
                    disabled=True
                ))

            # Update message with colored buttons
            await question_message.edit(embed=q_embed, view=question_wrong_view)

            # Increment score if the selected option is correct
            if result.data['custom_id'] == correct_options[i]:
                score += 1

        # Create final result embed
        passed = score == len(questions)
        result_embed = None
        if passed:
            result_embed = discord.Embed(
                title="Marvelous!", color=Var.base_color)

            result_embed.description = "You passed the Quiz…"
        else:
            result_embed = discord.Embed(
                title="We appreciate your efforts!", description="**You didn't make it through this round**")
            result_embed.add_field(
                name="ㅤ", value=f"- Navigate to our website through <#{Var.official_links}>\n- Read carefully “Path of the Wild Network”\n- Come back in 24 hours and try again!")

        result_embed.add_field(
            name="Score", value=f"{score if passed else '?'}/{len(questions)}", inline=False)

        # Send final result message
        await interaction.followup.send(embed=result_embed, ephemeral=True)

        if passed:
            role = interaction.user.guild.get_role(Var.rendrill_role)
            await interaction.user.add_roles(role)

            db = Database("./data/criteria")
            db.update("role", {"a3": 1}, where={"user": interaction.user.id})

            db.close()

            await interaction.followup.send(f"Congratulations! You are now officially a Rendrill !\nGo to the <#{Var.spinwheel_channel}>, you've earned this success ^‿^", ephemeral=True)
            return

        if score < 2:
            await interaction.user.timeout(timedelta(hours=24))
            return

    def eligibility_check(self, user_id: int):
        """Checks if the user is eligible for the Rendrill role."""
        db = Database("./data/criteria")
        data = db.select("role", where={"user": user_id}, size=1)

        # i dont understand what this is for, but rayan said so this exists
        with open("./data/req.json") as f:
            data__ = json.load(f)
        if user_id not in data__['rendrill']:
            update_criterias(user_id, db)

        if not data:
            data = (user_id, 0, 0, 0, 0)
            db.insert("role", data)

        db.close()

        if not (data[1] >= 4 and data[2] >= 8):
            return False
        else:
            return True

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="set-criteria", description="[MODS] Update user's criteria for acquiring Rendrill Role")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Invite 4 Members", value=1),
        app_commands.Choice(name="Reach Lvl. 8", value=2),
        app_commands.Choice(name="Complete Quiz", value=3)
    ])
    @app_commands.choices(done=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
    ])
    @app_commands.describe(activity="What the user has done")
    @app_commands.describe(done="Whether the user was successful in completing the task")
    async def set_criteria(self, interaction, user: discord.Member, activity: int, done: int):
        """
        This function allows the mods to update a user's criteria stats
        """

        # add to json file
        with open("./data/req.json", "r") as f:
            data__ = json.load(f)

        if user.id not in data__["rendrill"]:
            data__["rendrill"].append(user.id)
            with open("./data/req.json", "w") as f:
                json.dump(data__, f)

        # Getting data from database
        db = Database("./data/criteria")
        data = db.select("role", where={"user": user.id})
        print(data)

        if not data:
            db.insert("role", (user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user": user.id})

        data = list(data[0])
        print("SET REQ |", data)

        # Status of all 3 activites and whether role should be given and updating
        a1 = done if activity == 1 else data[1]
        a2 = done if activity == 2 else data[2]
        a3 = done if activity == 3 else data[3]

        print("SET REQ |", a1, a2, a3)

        if activity == 1 and done:
            a1 = 4
        elif activity == 2 and done:
            a2 = 8

        print("SET REQ |", a1, a2, a3)
        db.update("role", {"user": user.id, "a1": a1, "a2": a2, "a3": a3, "role": 0},
                  where={"user": user.id})
        db.close()

        await interaction.response.send_message(f"Updated.", ephemeral=True)

    async def view_criteria(self, interaction: discord.Interaction):

        # if user already has guardrill role
        if interaction.user.get_role(Var.rendrill_role):
            embed = discord.Embed(title="Role already assigned", color=Var.base_color,
                                  description="It looks like you already have the `Rendrill` role. Thank you for your interest!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # Retrieving data from database
        db = Database("./data/criteria")
        data = db.select("role", where={"user": interaction.user.id})

        if not data:
            db.insert("role", (interaction.user.id, 0, 0, 0, 0))
            data = db.select("role", where={"user": interaction.user.id})

        db.close()

        data = data[0]
        print("Criteria| ", data)

        rc, wc = '❌', '✅'

        # Embed
        embed = discord.Embed(title="Rendrill Role Criteria",
                              description="Complete all 3 tasks to get the Rendrill role!", color=Var.base_color)
        embed.add_field(
            name=f"{rc if data[1] < 4 else wc} Invite at least 4 users to the server", value="ㅤ", inline=False)
        embed.add_field(
            name=f"{rc if data[2] < 8 else wc} Reach Level - 8", value="ㅤ", inline=False)
        embed.add_field(
            name=f"{rc if not data[3] else wc} Complete the Quiz (after 1st & 2nd Tasks)", value="ㅤ", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    bot.tree.add_command(
        Explorill(
            bot=bot,
            name="explorill",
            description="Commands related to Explorill Role")
    )

    bot.tree.add_command(
        Purmarill(
            bot=bot,
            name="purmarill",
            description="Commands related to Purmarill Role"
        )
    )

    bot.tree.add_command(
        Rendrill(
            bot=bot,
            name="rendrill",
            description="Commands related to Rendrill Role"
        )
    )
