from helpers import Var as V
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord import ui
from easy_sqlite3 import *
import asyncio

# API STUFF
import requests
import os
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

# import stored variables
Var = V()

# cog


class TwitterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Database stuff
        db = Database("data/data")
        db.create_table(
            "users", {"user": 'INTEGER', "name": 'TEXT', "twitter": 'TEXT', "wallet": 'TEXT'})

        # View stuff
        get_prumarill_button = ui.Button(
            label="Get Purmarill", style=discord.ButtonStyle.green, custom_id="purmarill:green")
        # Link function called when button clicked.
        get_prumarill_button.callback = self.partnership_embed

        self.views = ui.View(timeout=None)
        self.views.add_item(get_prumarill_button)

        db.close()
        # self.db.create_table("")

        # API STUFF
        self.bearer_token = os.getenv('APIBEARER')
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }
        # this is the name of the thing the other thing
        self.screen_name = Var.twitter_account

        # vairables
        self.most_recent_tweet_id = Var.most_recent_tweet_id

    @tasks.loop(minutes=Var.twitter_loop_time)
    async def check_tweets(self):
        print("TWITTER | CHECKING")
        url = f'https://api.twitter.com/2/tweets/search/recent?query=from:{self.screen_name}'
        response = requests.get(url, headers=self.headers)

        try:
            tweets = response.json()
        except:
            print(f"TWITTER | API ERROR {tweets}")
            return

        if tweets and tweets['meta']['newest_id'] != self.most_recent_tweet_id:
            print("TWITTER | INSIDE IF (after check if recent tweet id)")
            tweet_id = tweets['data'][0]['id']
            print(tweet_id, type(tweet_id))
            self.most_recent_tweet_id = tweet_id
            Var.most_recent_tweet_id = tweet_id

            # Get the tweet URL
            tweet_url = f'https://twitter.com/{self.screen_name}/status/{self.most_recent_tweet_id}'

            # Format the tweet link as a string
            tweet_link = f':loudspeaker: @everyone {tweet_url}'

            # Get the channel object
            channel = self.bot.get_channel(Var.tweet_channel_id)

            # Send the tweet link to the Discord channel
            msg = await channel.send(tweet_link)
            print(f"TWITTER | NEW TWEET {msg}")

    @app_commands.checks.has_any_role(Var.guardrill_role, Var.liberator_role)
    @app_commands.command(name="setup-purmarill", description="Setup the Purmarill Interface in the specified channel")
    async def setup_purmarill(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(
            title='Click the button to get your Purmarill role', color=Var.base_color)

        # Sending message
        await channel.send(embed=embed, view=self.views)
        await interaction.response.send_message(f"Added `get prumarill` app, to <#{channel.id}>")

    async def link(self, interaction):

        # if user already has role
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
                if not validify_twitter(str(self.twitter_username)):
                    await interaction.response.send_message("Twitter username does not exist.", ephemeral=True)
                    return

                # checks if it is a valid wallet address
                if not validify_wallet(str(self.wallet_id)):
                    await interaction.response.send_message("FLR address is not valid.", ephemeral=True)
                    return

                db = Database("./data/data")
                # Adding name to db ## TODO: HERE NIVED
                db.insert("users", (interaction.user.id, interaction.user.name, str(
                    self.twitter_username), str(self.wallet_id)))
                await interaction.response.send_message("You are now officially a Purmarill!", ephemeral=True)

                await interaction.user.add_roles(role)

                db.close()

        # send modal when link is called
        await interaction.response.send_modal(PurmarillVerificationModal())

        # Check if twitter account is valid
        def validify_twitter(twitter: str):
            url = f"https://api.twitter.com/2/users/by/username/{twitter}"
            response = requests.get(url, headers=self.headers)

            data = response.json()

            try:
                if data["data"]["id"].isdigit():  # checks if id exists, and id int
                    return True
            except KeyError:
                return False

        # Check if wallet adress is valid
        def validify_wallet(wallet: str):
            return Web3.isAddress(wallet)
        
    async def partnership_embed(self, interaction):
        desc = """This address will also be used to recognize our partner projects assets,
If you want to gain the partnership roles, you have to provide the address that you are using for holding relevant products of these projects."""
        
        embed = discord.Embed(title="Before you submit...", description=desc, color=Var.base_color)
        view = ui.View()
        btn = ui.Button(label="Continue", style=discord.ButtonStyle.green)
        btn.callback = self.link
        
        view.add_item(btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


        
    @app_commands.command(name='update-wallet', description='Update FLR Wallet Address')
    async def update_wallet(self, interaction, address:str):
        db = Database("./data/data")
        data = db.select("users", where={"user":interaction.user.id}, size=1)

        if not data:
            await interaction.response.send_message("Looks like there is no Wallet address currently linked to your account...", ephemeral=True)
            return
        
        db.update("users", information={"wallet":address}, where={"user":interaction.user.id})

        await interaction.response.send_message(f"Succesfully updated wallet address from `{data[3]}` to `{address}`!", ephemeral=True)



async def setup(bot):
    await bot.add_cog(TwitterCog(bot))
