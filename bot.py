import discord
from discord.ext import commands
import os
import sys, traceback


"""Rewrite Documentation:
http://discordpy.readthedocs.io/en/rewrite/api.html
Rewrite Commands Documentation:
http://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html
Familiarising yourself with the documentation will greatly help you in creating your bot and using cogs.
"""

def get_prefix(bot, message):
    prefixes = ['?']
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = [
    'cogs.fydo'
    ,'cogs.admin'
]

bot = commands.Bot(command_prefix=get_prefix, description='A Translating Bot')

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'Loaded {extension}.')
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_ready():
    #http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready
    await bot.change_presence(activity=discord.Activity(name="Fyd0", type=discord.ActivityType.watching))
    print('Successfully logged in and booted...!')


bot.run(os.environ['token'])
