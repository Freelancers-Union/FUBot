import disnake
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
import requests
import auraxium
import os
import census

from auraxium import ps2
from disnake.ext import commands

"""
Variables
LOGLEVEL
DISCORDTOKEN
INFLUXDB_TOKEN

"""
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError as err:
    """
    This is an expected error when not running locally using dotenv
    """
    logging.exception(err)



logging.basicConfig(level=logging.os.getenv('LOGLEVEL'))
discordClientToken = os.getenv('DISCORDTOKEN')
Botdescription = "The serious bot for the casual Discord."

"""
Discord Intents
"""
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

"""
Initialize the bot
"""
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

# @bot.slash_command()
# async def ping(inter):
#     await inter.response.send_message("Pong!")

@bot.slash_command()
async def playercard(inter, charactername):
    """Get character information for a given character"""

    await inter.response.send_message("Getting player stats for "+charactername+" ...")

    char, outfit = await census.getChar(charactername)
    if char is None:
        await inter.edit_original_message("Player "+charactername+" cannot be found.")
        raise ValueError("Player could not be found.", charactername)

    async with auraxium.Client(service_id=str(os.getenv('CENSUS_TOKEN'))) as client:

        faction = await client.get_by_id(ps2.Faction, char.faction_id)
        Message = disnake.Embed(
            title="__Player Card for "+str(char.name)+":__",
            color=3166138,
            description="[Fisu Stats](https://ps2.fisu.pw/player/?name="+str(char.name)+")\n\n \
            **Faction:** "+str(faction)+"\n \
            **Battle rank:** "+str(char.battle_rank.value)+"\n \
            **ASP level:** "+str(char.data.prestige_level)+"\n \
            **Played since:** "+str(char.times.creation_date)[:16]+"\n \
            **Last online:** "+str(char.times.last_save_date)[:16]+"\n \
            **Playtime:** "+str(round(char.times.minutes_played/60))+" Hours\n \
",
        )
        if outfit is not None:
            outfitName = await client.get_by_id(auraxium.ps2.Outfit, outfit.outfit_id)
            Message.add_field(
                name="Outfit",
                value="**"+str(outfitName)+"**\n \
                    **Rank:** "+str(outfit.rank)+"\n \
                    **Joined:** "+str(outfit.member_since_date)[:16]+" ",
                inline=True
            )

    try:
        await inter.edit_original_message(" ",embed=Message)
    except requests.exceptions.HTTPError as err:
        logging.exception(err)
        await inter.edit_original_message('Oops! Something went wrong.')

    logging.info("Playercard for "+charactername+" delivered successfully.")

@bot.slash_command()
async def outfit(inter, name, tag):
    """Get Outfit information for a given outfit"""
    await inter.response.send_message("Getting outfit details for "+name+" ...")
    outfit = await census.getOutfit(name)
    if outfit is not None:
        await inter.edit_original_message("Found sumfin")
    else:
        await inter.edit_original_message("Could not find outfit:"+name+".")

bot.run(discordClientToken)