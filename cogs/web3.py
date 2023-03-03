import discord
from discord import ui
from discord import app_commands

from easy_sqlite3 import *
import requests
from web3 import Web3
import os


from helpers import Var as V
Var = V()


class Web3_(app_commands.Group):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot = bot

        # Web3 API
        self.bearer_token = os.getenv('APIBEARER')
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }
        # this is the name of the thing the other thing
        self.screen_name = Var.twitter_account

        # vairables
        self.most_recent_tweet_id = Var.most_recent_tweet_id

    # Check if Web3 account is valid
    def validify_Web3(self, Web3: str):
        """Checks if the given Web3 handle is valid using the Web3 api"""
        url = f"https://api.Web3.com/2/users/by/username/{Web3}"
        response = requests.get(url, headers=self.headers)

        data = response.json()

        try:
            if data["data"]["id"].isdigit():  # checks if id exists, and id int
                return True
        except KeyError:
            return False

    @app_commands.command(name="update-wallet", description="Update your FLR Address")
    async def update_wallet(self, interaction, address: str):
        db = Database("./data/data")
        data = db.select("users", where={"user": interaction.user.id}, size=1)

        if not data:
            await interaction.response.send_message("Looks like there is no Wallet address currently linked to your account...", ephemeral=True)
            return

        if not Web3.isAddress(address):
            await interaction.response.send_message("Invalid Wallet Address", ephemeral=True)
            return

        db.update("users", information={"wallet": address}, where={
                  "user": interaction.user.id})

        await interaction.response.send_message(f"Succesfully updated wallet address from `{data[3]}` to `{address}`!", ephemeral=True)


async def setup(bot):
    bot.tree.add_command(
        Web3_(
            bot=bot,
            name="web3",
            description="Commands related to Web3 (Twitter and Wallet)"
        )
    )
