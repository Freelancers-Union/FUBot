import os
import disnake
import logging
logging.basicConfig(level=logging.os.getenv('LOGLEVEL'),format='%(asctime)s %(funcName)s: %(message)s ' , datefmt='%m/%d/%Y %I:%M:%S %p')
import requests
import auraxium
import census

from auraxium import ps2
from disnake.ext import commands

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError as err:
    """
    This is an expected error when not running locally using dotenv
    """
    logging.warning(err)


"""
Discord Intents
"""
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

"""
Initialize the bot
"""
discordClientToken = os.getenv('DISCORDTOKEN')
Botdescription = "The serious bot for the casual Discord."
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("?"), 
    description=Botdescription, 
    intents=intents, 
    test_guilds=[914185528268689428,282514718445273089],
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
    await inter.response.send_message("Getting player stats for "+character_name+" ...")
    async with auraxium.Client(service_id=str(os.getenv('CENSUS_TOKEN'))) as client:
        char, outfit = await census.getChar(character_name, client)
        if char is None:
            await inter.edit_original_message("Player "+character_name+" cannot be found.")
            raise ValueError("Player could not be found.", character_name)

        Message = disnake.Embed(
            title="__Player Card for "+str(char[0].name)+":__",
            color=3166138,
            description="[Fisu Stats](https://ps2.fisu.pw/player/?name="+str(char[0].name)+")\n\n**Online:** "+str("<:red_circle:982747951006908456>" if char[1]==0 else "<:green_circle:982747951006908456>")+"\n**Faction:** `"+str(await client.get_by_id(ps2.Faction, char[0].faction_id))+"`\n**Battle rank:** `"+str(char[0].battle_rank.value)+"`\n**ASP level:** "+str(char[0].data.prestige_level)+"\n**Played since:** `"+str(char[0].times.creation_date)[:16]+"`\n**Last online:** `"+str(char[0].times.last_save_date)[:16]+"`\n**Playtime:** "+str(round(char[0].times.minutes_played/60))+" Hours\n",
            )
        if outfit is not None:
            Message.add_field(
                name="__Outfit__",
                value="**"+str(await client.get_by_id(auraxium.ps2.Outfit, outfit.outfit_id))+"**\n**Rank:** "+str(outfit.rank)+"\n**Joined:** "+str(outfit.member_since_date)[:16]+" ",
                inline=False
                )
        await inter.edit_original_message(" ",embed=Message)

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
    await inter.response.send_message("Getting outfit details ...")
    async with auraxium.Client(service_id=str(os.getenv('CENSUS_TOKEN'))) as client:
        outfit = await census.getOutfit(tag, name, client)
        if outfit is None:
            await inter.edit_original_message("Could not find outfit.")

        outfitLeader=await client.get_by_id(auraxium.ps2.Character, outfit[0].leader_character_id)
        Message = disnake.Embed(
            title="__Outfit details for "+str(outfit[0].name)+":__",
            color=3166138,
            description="   [Fisu Stats](https://ps2.fisu.pw/outfit/?name="+str(outfit[0].alias_lower)+")\n\n**Faction:** "+str(await client.get_by_id(ps2.Faction, outfitLeader.faction_id))+"\n**Leader:** "+str(outfitLeader.name)+"\n**Members:** "+str(outfit[0].member_count)+"\n**Online:** "+str(outfit[1])+"\n**Created:** "+str(outfit[0].time_created_date)[:10]+"\n",
            )
    await inter.edit_original_message("",embeds=[Message])
    inter.is_expired()


@bot.event
async def on_message(message: disnake.Message):
    """
    Do things when a message is sent in discord channel

    Parameters
    ----------
    message: Received Discord message

    """
    # all messages below this will be ignored by bot
    if message.author.id == bot.user.id:
        return
    # react to message if any line starts with "React With EMOJI"
    # if after "React with" does not fallow emoji, it will fail with warning in console
    for line in message.content.splitlines():
        if line.lower().startswith("react with"):
            emoji = line.split(" ")[2]
            await message.add_reaction(emoji)


bot.run(discordClientToken)
