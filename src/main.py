import os
import logging
import datetime
from typing import List
import disnake
from disnake.ext import commands
import auraxium
from auraxium import ps2
import census
import commands.get_player as get_player
import commands.get_outfit as get_outfit
import commands.ops as ops
import emoji
import re

logging.basicConfig(level=logging.os.getenv('LOGLEVEL'), format='%(asctime)s %(funcName)s: %(message)s ',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
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

if os.getenv('TEST_GUILD_ID') is not None:
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or("?"),
        description=Botdescription,
        intents=intents,
        test_guilds=[int(os.getenv('TEST_GUILD_ID'))],
        sync_commands_debug=False
    )
else:
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or("?"),
        description=Botdescription,
        intents=intents,
        sync_commands_debug=False
    )


@bot.event
async def on_ready():
    logging.info("Logged in as " + str(bot.user) + " (ID: " + str(bot.user.id) + ")")
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
    """
    Get character information for a given character

    Parameters
    ----------
    character_name: character name to search for
    """
    await inter.response.defer()
    try:
        player_card = await get_player.get_player(character_name)
        if player_card is not None:
            await inter.edit_original_message(" ", embed=player_card)
        else:
            await inter.edit_original_message("Could not find character: " + str(character_name))
    except Exception as e:
        await inter.edit_original_message("Hmm, looks like something went wrong.")
        logging.exception(e)


@bot.slash_command()
async def outfit(
        inter: disnake.ApplicationCommandInteraction,
        tag: str = 0,
        name: str = 0,
):
    """
    Get Outfit information for a given outfit

    Parameters
    ----------
    name: Full outfit name
    tag: Outfit tag
    """
    await inter.response.defer()
    try:
        outfit_card = await get_outfit.get_outfit(tag, name)
        if outfit_card is not None:
            await inter.edit_original_message("", embed=outfit_card)
        else:
            await inter.edit_original_message("Could not find outfit: " + str(name) + str(tag))
    except Exception as e:
        await inter.edit_original_message("Hmm, looks like something went wrong.")
        logging.exception(e)




EVENTS = ["Drill", "Casual", "FUAD", "FUBG", "FUEL", "FUGG", "Huntsmen", "ArmaOps"]

async def autocomplete_event(inter, string: str) -> List[str]:
    return [event for event in EVENTS if string.lower() in event.lower()]

@bot.slash_command()
async def announce_event(
        inter: disnake.CommandInteraction,
        event: str = commands.Param(autocomplete=autocomplete_event),
        message_body: str = "Find us in game."
):
    """
    Post an event announcement to #ps2-announcements

    Parameters
    ----------
    message_body: The message to attach to the announcement.'

    """

    await inter.response.defer(ephemeral=True)
    try:
        await ops.event_message(inter, message_body, event)
    except Exception as e:
        await inter.edit_original_message("Hmm, looks like something went wrong.")
        logging.exception(e)


@bot.message_command(name="Add Reactions")
@commands.default_member_permissions(manage_messages=True)
async def vote(inter: disnake.interactions.application_command.ApplicationCommandInteraction,
               message: disnake.Message):
    emoji_list: list

    await inter.response.defer(ephemeral=True)
    # Permission checks
    # this is as a catch just in case the default_members_permissions fail
    if not message.channel.permissions_for(inter.author).manage_messages:
        await inter.edit_original_message("Request denied.\n" +
                                          "You don't have the permissions to remove unneeded reactions or spam in " +
                                          message.channel.mention + "\nhttps://www.govloop.com/wp-content/uploads"
                                                                    "/2015/02/data-star-trek-request-denied.gif"
                                          )
        return

    discord_emojis = list(set(re.compile(r"<:.*:[0-9]*>").findall(message.content)))  # some magic to delete duplicates
    emoji_list = emoji.distinct_emoji_list(message.content) + discord_emojis

    for item in emoji_list:
        await message.add_reaction(item)
    await inter.edit_original_message("reacted with:" + str(emoji_list))


async def new_members(inter, days: int = 7):
    """
    Gets new Discord Members

    Parameters
    ----------
    Days: How many days in the past to search for new members
    """
    all_ps2_members = []
    all_a3_members = []
    for member in bot.get_all_members():
        roles: [disnake.Role] = member.roles
        for r in roles:
            if r.name == "Planetside 2":
                all_ps2_members.append(member)
            if r.name == "Arma 3":
                all_a3_members.append(member)

    date_delta = datetime.datetime.now() - datetime.timedelta(days=days)
    new_ps2_members = []
    new_a3_members = []
    new_ps2_message = "\n---------------\n"
    new_a3_message = "\n---------\n"
    for i in all_ps2_members:
        if i.joined_at.timestamp() > date_delta.timestamp():
            new_ps2_members.append(i.name)
            new_ps2_message = new_ps2_message + "<@" + str(i.id) + ">" + "\n"
    for i in all_a3_members:
        if i.joined_at.timestamp() > date_delta.timestamp():
            new_a3_members.append(i.name)
            new_a3_message = new_a3_message + "<@" + str(i.id) + ">" + "\n"
    
    Message = disnake.Embed(
        title="New Discord Member Report",
        color=0x9E0B0F,
        description="Members who joined within the last "+ str(days) +" days",
        )
    Message.add_field(
        name="PlanetSide 2",
        value= "Count: " + str(len(new_ps2_members)) + new_ps2_message,
        inline = True
        )
    Message.add_field(
        name="Arma 3",
        value= "Count: " + str(len(new_a3_members)) + new_a3_message,
        inline = True
        )
    #channel = disnake.utils.get(bot.get_all_channels(), guild__name='Freelancers Union [FU]', name='Officers')
    channel = disnake.utils.get(bot.get_all_channels(), guild__name='FU Demo/Testing Server', name='officers')
    await channel.send(embed=Message)
    await inter.response.edit_original_message("Report generated")


@bot.slash_command()
async def new_member_report(
        inter: disnake.CommandInteraction,
        days: int = 7,
):
    """
    Display new Discord members

    Parameters
    ----------
    Days: How many days in the past to search for new members
    """
    await inter.response.defer(ephemeral=True)
    await new_members(inter, days)

bot.run(discordClientToken)
