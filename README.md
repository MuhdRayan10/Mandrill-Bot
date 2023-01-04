# Mandrills Bot
Mandrills Bot is a Discord bot that provides several features to assist in the management of a Discord server.

## Commands
`/start_verification [channel]`<br />
This command sets up the verification process for new members of the Discord server. When the command is run, a verification button is added to the specified channel. When a new member clicks the verify button, they will be presented with a captcha to solve. Once the captcha is solved, the user will be verified and granted access to the Discord server.
> Note: This command must be run every time the bot is restarted.

`/setup-tickets [channel]`<br />
This command sets up a ticketing system in the specified channel. With the ticketing system, users can create and track the progress of support requests or issues.

`/link [twitter username] [wallet id]`<br />
This command checks the validity of a given twitter username and Ethereum wallet id. The twitter username is checked using the Twitter API and the wallet id is checked using web3 to ensure it is a valid Ethereum address. If both the twitter username and wallet id are valid, the user is added to the database of valid users and verified.

`/view-req`<br />
This command allows users to view the criteria for acquiring the "rendrill" role. The "rendrill" role and the specific criteria for acquiring it are not specified.

`/req [user] [activity] [done]`<br />
This command allows moderators to update the criteria for a specific user to acquire the "rendrill" role. The user argument should be a Discord member, the activity argument should be one of the three activities specified, and the done argument should be either "true" or "false". This command is only available to moderators.

Features
1. Send a welcome message to new members upon joining the Discord server.
2. Check for tweets from the twitter handle "TheMandrillsNFT" and send them to a specific channel in the Discord server.

For more information or assistance with Mandrills Bot, please contact the developers, Nived (nivéd#5869) or Rayan (Rayan10#5701), via Discord.
