import os
import logging
import datetime
from typing import List
import aiocron
import disnake
from disnake.ext import commands
import auraxium
from auraxium import ps2
import census
import helpers.discord_checks as dc
import commands.new_discord_members as new_discord_members
import commands.get_player as get_player
import commands.get_outfit as get_outfit
import commands.ops as ops
from database_connector import Database
from loggers.arma_server_logger import ArmaLogger
import emoji
import re

logging.basicConfig(level=logging.os.getenv('LOGLEVEL'), format='%(asctime)s %(funcName)s: %(message)s ',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

# Discord Intents
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Initialize the bot

discordClientToken = os.getenv('DISCORDTOKEN')
Botdescription = "The serious bot for the casual Discord."

Database.initialize()
arma_logger = ArmaLogger(Database)

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


async def autocomplete_event(inter, string: str) -> List[str]:
    events = ["Drill", "nFUc", "vFUs", "Casual", "FUAD", "FUAF", "FUBG", "FUEL", "FUGG", "Huntsmen", "ArmaOps"]
    return [event for event in events if string.lower() in event.lower()]


@bot.slash_command(dm_permission=False)
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
async def add_reactions(inter: disnake.ApplicationCommandInteraction,
                        message: disnake.Message):
    await inter.response.defer(ephemeral=True)
    # Permission checks
    # this is as a catch just in case the default_members_permissions fail
    if not await dc.user_or_role_has_permission(inter=inter, manage_reactions=True, send_error=True):
        return
    if not await dc.bot_has_permission(inter=inter, react=True, send_error=True):
        return

    discord_emojis = []
    for _ in message.guild.emojis:
        e = str(_)
        if str(e) in message.content:
            discord_emojis.append(e)
    emoji_list: list[str] = emoji.distinct_emoji_list(message.content) + discord_emojis
    sorted_list = sorted(emoji_list, key=lambda i: message.content.rfind(i))

    for item in sorted_list:
        await message.add_reaction(item)
    await inter.edit_original_message("reacted with:" + str(sorted_list) + "\nTo message:" + message.jump_url)


@aiocron.crontab("0 17 * * 5")
async def send_scheduled_message():
    """
    Scheduled task to post new Discord members report.
    Cron: Every Friday at 1700 UTC
    """
    weekly_new_member_report = new_discord_members.NewDiscordMembers(bot)
    try:
        for guild in bot.guilds:
            await weekly_new_member_report.build_member_report(guild=guild)
    except Exception as e:
        logging.exception(e)


@aiocron.crontab("*/10 * * * *")
async def log_arma_server_status():
    arma_logger.log_server_status()

# Load cog extensions into the bot
bot.load_extension("commands.role_added")
bot.load_extension("commands.new_discord_members")
bot.load_extension("commands.link_ps2_discord")
bot.load_extension("commands.squad_markup")
bot.load_extension("loggers.discord_logger")
bot.load_extension("loggers.ps2_outfit_members")
bot.load_extension("loggers.ps2_outfit_logger")


bot.run(discordClientToken)
