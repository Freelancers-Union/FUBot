import os
import logging
from cron_jobs import init_cron_jobs
from fubot import FUBot
import disnake
from disnake.ext import commands
import helpers.discord_checks as dc
import commands.ops as ops
import emoji

# from database import init_database, get_mongo_uri

logging.basicConfig(
    level=os.getenv("LOGLEVEL"),
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
)

# Discord Intents
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Initialize the bot

discordClientToken = os.getenv("DISCORDTOKEN")
bot_description = "The serious bot for the casual Discord."

bot = FUBot(
    command_prefix=commands.when_mentioned_or("?"),
    description=bot_description,
    intents=intents,
    command_sync_flags=commands.CommandSyncFlags.default(),
)


@bot.event
async def on_connect():
    # Easierr to ask for forgiveness than permission
    # https://stackoverflow.com/a/610923
    try:
        if bot.first_time_connected:
            logging.info("Reconnected to Discord.")
            return
    except AttributeError:
        bot.first_time_connected = (
            True  # Used to prevent the bot from running the on_ready code on reconnects
        )
    # everything below here will only run on the first connect

    # try:
    #     logging.info("Connected to Discord. Initializing Database.")
    #     await init_database(get_mongo_uri(), "FUBot")
    # except Exception as e:
    #     logging.exception(e)
    #     logging.error("Failed to initialize database. Exiting...")
    #     exit(1)

    init_cron_jobs(bot)

    logging.info("Loading extensions...")
    # Load cog extensions into the bot
    # bot.load_extension("commands.role_added")
    bot.load_extension("commands.new_discord_members")
    # bot.load_extension("commands.link_ps2_discord")
    bot.load_extension("commands.squad_markup")
    bot.load_extension("commands.ps2_lookup")
    bot.load_extension("commands.arma_cog")
    # bot.load_extension("loggers.discord_logger")
    # bot.load_extension("loggers.ps2_outfit_members")
    # bot.load_extension("loggers.ps2_outfit_online_logger")
    # bot.load_extension("loggers.arma_server_logger")
    bot.load_extension("send_intro")
    bot.load_extension("helpers.sync_commands")
    bot.load_extension("services.a3_onboarding")
    bot.load_extension("services.ps2_leader_messages")


@bot.event
async def on_ready():
    logging.info("Logged in as " + str(bot.user) + " (ID: " + str(bot.user.id) + ")")
    logging.info("FUBot is ready!")


# async def autocomplete_event(inter, string: str) -> list[str]:
#     events = [
#         "Drill",
#         "nFUc",
#         "vFUs",
#         "Casual",
#         "FUAD",
#         "FUAF",
#         "FUBG",
#         "FUEL",
#         "FUGG",
#         "Huntsmen",
#         "ArmaOps",
#         "CombinedArms",
#     ]
#     return [event for event in events if string.lower() in event.lower()]
#
#
# @bot.slash_command(dm_permission=False)
# async def announce_event(
#     inter: disnake.CommandInteraction,
#     event: str = commands.Param(autocomplete=autocomplete_event),
#     message_body: str = "Find us in game.",
# ):
#     """
#     Post an event announcement to #ps2-announcements
#
#     Parameters
#     ----------
#     inter:
#         The interaction object.
#     event:
#         The name of the event to announce.
#     message_body: The message to attach to the announcement.'
#
#     """
#
#     await inter.response.defer(ephemeral=True)
#     try:
#         await ops.event_message(inter, message_body, event)
#     except Exception as e:
#         await inter.edit_original_message("Hmm, looks like something went wrong.")
#         logging.exception(e)


@bot.message_command(name="Add Reactions")
@commands.default_member_permissions(manage_messages=True)
async def add_reactions(
    inter: disnake.ApplicationCommandInteraction, message: disnake.Message
):
    await inter.response.defer(ephemeral=True)
    # Permission checks
    # this is as a catch just in case the default_members_permissions fail
    if not await dc.user_or_role_has_permission(
        inter=inter, manage_reactions=True, send_error=True
    ):
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
    await inter.edit_original_message(
        "reacted with:" + str(sorted_list) + "\nTo message:" + message.jump_url
    )


bot.run(discordClientToken)
