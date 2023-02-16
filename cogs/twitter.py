import discord
from discord import ui
from discord import app_commands

import requests
import os


from helpers import Var as V
Var = V()


class Twitter(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        # Twitter API
        self.bearer_token = os.getenv('APIBEARER')
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }
        # this is the name of the thing the other thing
        self.screen_name = Var.twitter_account

        # vairables
        self.most_recent_tweet_id = Var.most_recent_tweet_id

    # Check if twitter account is valid
    def validify_twitter(self, twitter: str):
        """Checks if the given twitter handle is valid using the twitter api"""
        url = f"https://api.twitter.com/2/users/by/username/{twitter}"
        response = requests.get(url, headers=self.headers)

        data = response.json()

        try:
            if data["data"]["id"].isdigit():  # checks if id exists, and id int
                return True
        except KeyError:
            return False


async def setup(bot):
    bot.tree.add_command(
        Twitter(
            bot=bot,
            name="twitter",
            description="Commands related to twitter"
        )
    )
