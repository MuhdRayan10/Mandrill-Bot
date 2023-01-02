import discord
from discord.ext import commands, tasks
from discord import app_commands
from easy_sqlite3 import *

# API STUFF
import requests
import os
from dotenv import load_dotenv
load_dotenv()

CHANNEL_ID = 1058732377087676480 #TODO: Rayan chagne this later to the other thing

#cog
class TwitterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Database stuff
        self.db = Database("data/data")
        self.db.create_table("users", {"user":INT, "name": STR, "twitter":STR, "wallet":STR})

        # API STUFF
        self.bearer_token = os.getenv('APIBEARER')
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'MyApp/1.0'
        }
        screen_name = 'NivedVenugopal1' # this is the name of the thing the other thing
        self.url = f'https://api.twitter.com/2/tweets/search/recent?query=from:{screen_name}'

        # vairables
        self.most_recent_tweet_id = 0

        # start the task
        #self.check_tweets.start()

    @tasks.loop(minutes=5)
    async def check_tweets(self):
        response = requests.get(self.url, headers=self.headers)

        try:
            tweets = response.json()['data']
        except KeyError:
            print("User has no posts!")
            return

        if tweets and tweets[0]['id'] != self.most_recent_tweet_id:
            self.most_recent_tweet_id = tweets[0]['id']

            # Get the tweet URL
            tweet_url = f'https://twitter.com/{self.screen_name}/status/{self.most_recent_tweet_id}'

            # Format the tweet link as a string
            tweet_link = f'New tweet from @{self.screen_name}: {tweet_url}'

            # Get the channel object
            channel = self.bot.get_channel(CHANNEL_ID)

            # Send the tweet link to the Discord channel
            await channel.send(tweet_link)
    
    @app_commands.command(name="connect", description="Connect your Discord Account to your Twitter and Wallet Adresses")
    @app_commands.describe(twitter="Your Twitter Username")
    @app_commands.describe(wallet="Your Crypto wallet Adress")
    async def connect(self, interaction, twitter:str, wallet:str):
        

        valid = self.validify_twitter(twitter)

        if not valid:
            await interaction.response.send_message("Twitter account not valid.")
            return

        # Checking if twitter / walled account / user already exists db
        if not self.db.if_exists("users", {"twitter":twitter, "wallet":wallet, "user":interaction.user.id}, separator="OR"):
            await interaction.response.send_message("Twitter account / Wallet ID already registered...")
            return

        # Adding name to db
        self.db.insert("users", (interaction.user.id, interaction.user.name, twitter, wallet))
        await interaction.response.send_message("Added")
    

    def validify_twitter(self, twitter):
        return True # TODO Nived

    

async def setup(bot):
    await bot.add_cog(TwitterCog(bot))
    