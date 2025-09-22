import discord
from discord.ext import commands
import scraper
import keepAlive
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

keepAlive.keep_alive()

#giving perms to access messages
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='=', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("=help for all commands"))
    print(f'logged in as {bot.user}')

@bot.command()
@commands.is_owner()
async def terminate(ctx):
    exit()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandError):
        await ctx.send("problem")



@bot.command(help="Scrapes all added works, and returns their *name*, *last updated time*, *last updated chapter*. Arguments inputted = all - returns all works, OR URL or name of desired work", brief="Scrapes all added works.")
async def scrape(ctx, arg : str):
    if arg.lower() == "all":
        results_dict = scraper.scrape()
        result = ""
        for name in results_dict:
            await ctx.send(name + " | " + results_dict[name])
    else:
        result = scraper.scrape(name_or_URL = arg)
        await ctx.send(result)

@bot.command(help="Allows user to add a work to the list of works to be scraped. Argument inputted = URL of desired work.", brief="Add a work to the list of works to be scraped.")
async def add(ctx, arg):
    await ctx.send(scraper.add_to_scrape_list(arg))

@bot.command(help="Allows user to remove a work from the list of works to be scraped. Argumet inputted = URL OR name of desired work.", brief="Remove a work from the list of works to be scraped.")
async def remove(ctx, arg):
    await ctx.send(scraper.remove_from_scrape_list(arg))

@bot.command(help="Returns a list of all added works' titles.")
async def list(ctx):
    await ctx.send(scraper.return_readable_scrape_list())



bot.run(TOKEN)