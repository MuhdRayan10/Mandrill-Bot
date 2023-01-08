import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord import ui
from easy_sqlite3 import *

# API STUFF
import requests
import os
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

# import stored variables
from helpers import Var as V
Var = V()

#cog
class TwitterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Database stuff
        db = Database("data/data")
        db.create_table("users", {"user":'INTEGER', "name": 'TEXT', "twitter":'TEXT', "wallet":'TEXT'})
        
        db.close()
        # self.db.create_table("")

        # API STUFF
        self.bearer_token = os.getenv('APIBEARER')
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }
        self.screen_name = Var.twitter_account # this is the name of the thing the other thing

        # vairables
        self.most_recent_tweet_id = Var.most_recent_tweet_id

        # start the task
        self.check_tweets.start()

    @tasks.loop(minutes=Var.twitter_loop_time)
    async def check_tweets(self):
        url = f'https://api.twitter.com/2/tweets/search/recent?query=from:{self.screen_name}'
        response = requests.get(url, headers=self.headers)

        try:
            tweets = response.json()['data']
        except KeyError:
            print("User has no posts!")
            return


        if tweets and tweets[0]['id'] != self.most_recent_tweet_id:
            tweet_id = tweets[0]['id']
            self.most_recent_tweet_id = tweet_id
            Var.most_recent_tweet_id = tweet_id

            # Get the tweet URL
            tweet_url = f'https://twitter.com/{self.screen_name}/status/{self.most_recent_tweet_id}'

            # Format the tweet link as a string
            tweet_link = f'New tweet from @{self.screen_name}: {tweet_url}'

            # Get the channel object
            channel = self.bot.get_channel(Var.tweet_channel_id)

            # Send the tweet link to the Discord channel
            await channel.send(tweet_link)
    
    @app_commands.command(name="setup-purmarill", description="Setup the Purmarill Interface in the specified channel")
    async def setup_purmarill(self, interaction, channel: discord.TextChannel):
        # The Verify Embed
        embed = discord.Embed(title='Get Purmarill', description='Click the button to get your purmarill role.')
        get_prumarill_button = ui.Button(label="Get Purmarill", style=discord.ButtonStyle.green)

        get_prumarill_button.callback = self.link # Link function called when button clicked.
        
        view = ui.View()
        view.add_item(get_prumarill_button)

        # Sending message
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Added `get prumarill` app, to <#{channel.id}>")

    async def link(self, interaction):
        class PurmarillVerificationModal(ui.Modal, title='Purmarill Verification'):
            twitter_username = ui.TextInput(
                label="Twitter Username",
                placeholder="Enter your twitter username (without the handle)",
                style=discord.TextStyle.short
            )
            wallet_id = ui.TextInput(
                label="Wallet Address",
                placeholder='Enter your ETH wallet address',
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
                    await interaction.response.send_message("Twitter account not valid.", ephemeral=True)
                    return
                
                # checks if it is a valid wallet address
                if not validify_wallet(str(self.wallet_id)):
                    await interaction.response.send_message("Wallet ID not valid.", ephemeral=True)
                    return


                db = Database("./data/data")
                # Adding name to db ## TODO: HERE NIVED
                db.insert("users", (interaction.user.id, interaction.user.name, str(self.twitter_username), str(self.wallet_id)))
                await interaction.response.send_message("Added", ephemeral=True)

                await interaction.user.add_roles(role)


                db.close()

        # send modal when link is called
        await interaction.response.send_modal(PurmarillVerificationModal())

        # Check if twitter account is valid
        def validify_twitter(twitter:str):
            url = f"https://api.twitter.com/2/users/by/username/{twitter}"
            response = requests.get(url, headers=self.headers)

            data = response.json()

            try:
                if data["data"]["id"].isdigit(): # checks if id exists, and id int
                    return True
            except KeyError:
                return False
 
        # Check if wallet adress is valid
        def validify_wallet(wallet:str):
            return Web3.isAddress(wallet)


async def setup(bot):
    await bot.add_cog(TwitterCog(bot))
    