from easy_sqlite3 import *
import discord

async def update_criteria(inviter, guild, V):
    
    db2 = Database("./data/invites")
    data = db2.select("invites", where={"inviter":inviter.id})

    db2.close()

    count = 0
    for d in data:
        count += d[2]

    db = Database("./data/criteria")
    if not db.if_exists("role", where={"user":inviter.id}):
        db.insert("role", (inviter.id, 0, 0, 0, 0))

    db.update("role", {"a1": count}, where={"user":inviter.id})
    data = db.select("role", where={"user":inviter.id}, size=1)
    db.close()

    if data[1] >= 2 and data[2] == 1 and not data[3]:
        channel = guild.get_channel(V.rendrill_channel)
        await inviter.send(f"Looks like you are almost eligible for the `Rendrill` role! To complete the quiz, go to {channel.mention} and click on the `GET RENDRILL` button to start the quiz!")
    


def find_invite(li, code):
    for inv in li:
        if str(inv.code) == str(code):
            return inv

async def update_invites(member, V):
    db = Database("./data/invites")
    db.create_table("invites", {"inviter": INT, "code": STR, "uses": INT})

    invites = await member.guild.invites()
    old_invites = db.select("invites")

    db.close()

    inviter_ = []

    for old_invite in old_invites:
        new_invite = find_invite(invites, old_invite[1])
        if old_invite[2] < new_invite.uses:
            embed = discord.Embed(title="Invite", description="Information about the invite", color=V.base_color)
            embed.add_field(name="Inviter", value=new_invite.inviter.name)
            embed.add_field(name="Uses", value=f"`{new_invite.uses}`")
            embed.add_field(name="Invited", value=member.name)

            inviter_.append(new_invite.inviter)

            channel = member.guild.get_channel(V.log_channel)
            await channel.send(embed=embed)

    db = Database("./data/invites")
    db.clear_table('invites')

    codes = [o[1] for o in old_invites]

    for invite in invites:
        if invite.code not in codes:
            embed = discord.Embed(title="Invite", description="Information about the invite", color=V.base_color)
            embed.add_field(name="Inviter", value=invite.inviter.name)
            embed.add_field(name="Uses", value=f"`{invite.uses}`")
            embed.add_field(name="Invited", value=member.name)

            inviter_.append(invite.inviter)

            channel = member.guild.get_channel(V.log_channel)
            await channel.send(embed=embed)

        db.insert("invites", (invite.inviter.id, invite.code, invite.uses))

    db.close()

    await update_criteria(inviter_[0], member.guild, V)
