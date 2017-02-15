import discord
from discord.ext import commands
import random
from DiceParser import DiceParser
from concurrent.futures import ProcessPoolExecutor
import asyncio, feedparser

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)


def processDice(dice):
    """A wrapper for running our DiceParser in a seperate procces"""
    DP = DiceParser()
    result = DP.evaluateInfix(dice)
    return result

executor = ProcessPoolExecutor()

@bot.command()
async def roll(dice : str):
    """Rolls a dice using the custom DiceParser."""
    try:
        coro = bot.loop.run_in_executor(executor, processDice, dice)
        result = await asyncio.wait_for(coro, timeout=10.0, loop=bot.loop)
    except asyncio.TimeoutError:
        result="Operation took longer than 10 seconds. Aborted."
    except ValueError as err:
        result = err
    except ZeroDivisionError as err:
        result = err
    except Exception as err:
        result = "An unhandled exception occured during operation."
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, the bot is cool.')


rssUrl="https://www.reddit.com/r/rational/new/.rss"
parsedFeed = feedparser.parse(rssUrl)
feedparser.USER_AGENT = "r/rational discord rss bot traverse.da@gmail.com"

async def parse_rss():
    global parsedFeed
    await bot.wait_until_ready()
    while True:
        kwargs = {}
        if hasattr(parsedFeed, 'modified'):
            kwargs['modified']=parsedFeed.modified
        if hasattr(parsedFeed, 'etags'):
            kwargs['etags']=parsedFeed.etags
        parsedFeed = feedparser.parse('https://www.reddit.com/r/rational/new/.rss', **kwargs)
        if parsedFeed.status != 304:
             print("feed has changed")
             print(parsedFeed.status)
        await asyncio.sleep(15)

import sys

if not len(sys.argv)==2:
    print("This program takes exactly one argument, the auth token you want to run it with")
else:
    bot.run(sys.argv[1])
