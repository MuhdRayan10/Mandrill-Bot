import discord
from discord.ext import commands, tasks
from discord import app_commands
from easy_sqlite3 import *

# API STUFF
import requests
import os
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

from helpers import StaticVariables

#cog
class TwitterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Database stuff
        self.db = Database("data/data")
        self.db.create_table("users", {"user":'INTEGER', "name": 'TEXT', "twitter":'TEXT', "wallet":'TEXT'})
        # self.db.create_table("")

        # API STUFF
        self.bearer_token = os.getenv('APIBEARER')
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }
        self.screen_name = 'TheMandrillsNFT' # this is the name of the thing the other thing

        # vairables
        self.most_recent_tweet_id = StaticVariables.most_recent_tweet_id

        # start the task
        self.check_tweets.start()

    @tasks.loop(minutes=5)
    async def check_tweets(self):
        url = f'https://api.twitter.com/2/tweets/search/recent?query=from:{self.screen_name}'
        response = requests.get(url, headers=self.headers)

        try:
            tweets = response.json()['data']
        except KeyError:
            print("User has no posts!")
            return
        
        print(type(self.bot))

        if tweets and tweets[0]['id'] != self.most_recent_tweet_id:
            tweet_id = tweets[0]['id']
            self.most_recent_tweet_id = tweet_id
            StaticVariables.most_recent_tweet_id = tweet_id

            # Get the tweet URL
            tweet_url = f'https://twitter.com/{self.screen_name}/status/{self.most_recent_tweet_id}'

            # Format the tweet link as a string
            tweet_link = f'New tweet from @{self.screen_name}: {tweet_url}'

            # Get the channel object
            channel = self.bot.get_channel(StaticVariables.tweet_channel_id)
            print(channel)

            # Send the tweet link to the Discord channel
            await channel.send(tweet_link)
    
    @app_commands.command(name="connect", description="Connect your Discord Account to your Twitter and Wallet Adresses")
    @app_commands.describe(twitter="Your Twitter Username")
    @app_commands.describe(wallet="Your Crypto wallet Adress")
    async def connect(self, interaction, twitter:str, wallet:str):
        
        # check if the twitter is valid
        if not self.validify_twitter(twitter):
            await interaction.response.send_message("Twitter account not valid.")
            return
        
        # checks if it is a valid wallet id
        if not self.validify_wallet(wallet):
            await interaction.response.send_message("Wallet ID not valid.")
            return

        # Checking if twitter / walled account / user already exists db
        if not self.db.if_exists("users", {"twitter":twitter, "wallet":wallet, "user":interaction.user.id}, separator="OR"):
            await interaction.response.send_message("Twitter account / Wallet ID already registered...")
            return

        # Adding name to db
        self.db.insert("users", (interaction.user.id, interaction.user.name, twitter, wallet))
        await interaction.response.send_message("Added")
    

    def validify_twitter(self, twitter):
        url = f"https://api.twitter.com/2/users/by/username/{twitter}"
        response = requests.get(url, headers=self.headers)

        data = response.json()
        print(data)

        try:
            if data["data"]["id"].isdigit(): # checks if id exists, and id int
                return True
        except KeyError:
            return False

    def validify_wallet(self, wallet):
        infra_url = f"https://mainnet.infura.io/v3/{os.getenv('INFRAAPIKEY')}"
        w3 = Web3(Web3.HTTPProvider(infra_url))
        return w3.isAddress(wallet)


    

async def setup(bot):
    await bot.add_cog(TwitterCog(bot))
    