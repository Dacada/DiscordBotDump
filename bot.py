import os
import io
import csv

import discord
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='%', intents=intents)

class SimpleTSVDialect(csv.Dialect):
    def __init__(self):
        self.delimiter = '\t'
        self.doublequote = False
        self.escapechar = None
        self.lineterminator = '\r\n'
        self.quoting = csv.QUOTE_NONE

@bot.command(name='dumpusers')
async def dumpusers(ctx):
    """Prepare a CSV file containing, for each user in the current server, the following fields: Server Name, Discord Name, Discord Name Discriminator, User ID, Join Date"""
    try:
        guild = ctx.guild
        management_roles = [role
                            for role in guild.roles
                            if role.name == "Management"]
        if not management_roles:
            await ctx.send("No role named 'Management' in this server.")
            return
        management = management_roles[0]
        if not any(role >= management for role in ctx.author.roles):
            await ctx.send("Author not Management or above role.")
            return
        channel = ctx.message.channel
        async with channel.typing():
            output_bin = io.BytesIO()
            output = io.TextIOWrapper(output_bin)
            writer = csv.writer(output, SimpleTSVDialect())
            writer.writerow(('nick', 'name', 'discriminator', 'id', 'joinDate'))
            for member in guild.members:
                nick = member.display_name
                name = member.name
                discriminator = member.discriminator
                user_id = member.id
                join_date = member.joined_at.strftime('%Y-%m-%d')
                writer.writerow((nick, name, discriminator, user_id, join_date))
        output.flush()
        output_bin.seek(0)
        f = discord.File(output_bin, filename="dump.csv")
        await ctx.send("Generated CSV file.", file=f)
    except Exception as e:
        await ctx.send("Could not process request. Exception: {}".format(e))

if __name__ == "__main__":
    bot.run(TOKEN)

