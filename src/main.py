import os
import disnake
import logging
import auraxium
import census
import commands.get_player as get_player
import commands.get_outfit as get_outfit
from auraxium import ps2
from disnake.ext import commands

logging.basicConfig(level=logging.os.getenv('LOGLEVEL'),format='%(asctime)s %(funcName)s: %(message)s ' , datefmt='%m/%d/%Y %I:%M:%S %p')
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError as err:
    # This is an expected error when not running locally using dotenv
    logging.warning(err)



# Discord Intents

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True


# Initialize the bot

discordClientToken = os.getenv('DISCORDTOKEN')
Botdescription = "The serious bot for the casual Discord."
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("?"), 
    description=Botdescription, 
    intents=intents, 
    test_guilds=[914185528268689428],
    sync_commands_debug=False
    )

@bot.event
async def on_ready():
    logging.info("Logged in as "+str(bot.user)+" (ID: "+str(bot.user.id)+")" )
    logging.info("FUBot is ready!")

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.slash_command()
async def player_card(
    inter: disnake.CommandInteraction, 
    character_name: str,
    ):
    """Get character information for a given character

    Parameters
    ----------
    character_name: character name to search for
    """
    await inter.response.defer()
    try:
        await inter.edit_original_message(" ",embed=await get_player.get_player(character_name))
    except Exception as e:
        await inter.edit_original_message("Hmm, looks like something went wrong.")
        logging.exception(e)

@bot.slash_command()
async def outfit(
    inter: disnake.ApplicationCommandInteraction, 
    tag: str = 0, 
    name: str = 0,
    ):
    """Get Outfit information for a given outfit

    Parameters
    ----------
    name: Full outfit name
    tag: Outfit tag
    """
    await inter.response.defer()
    try:
        await inter.edit_original_message("",embed=await get_outfit.get_outfit(tag, name))
    except Exception as e:
        await inter.edit_original_message("Hmm, looks like something went wrong.")
        logging.exception(e)


bot.run(discordClientToken)