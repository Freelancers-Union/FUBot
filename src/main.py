import os
import logging
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


@bot.slash_command()
async def drill(
        inter: disnake.CommandInteraction,
        message_body: str = "Find us in game."
):
    """
    Post a drill announcement to #ps2-announcements

    Parameters
    ----------
    message_body: The message to attach to the announcement.'

    """
    required_role = "PS2 Division Officer"
    channel_name = "ps2-announcements"
    role_name = "Planetside 2"
    await inter.response.defer(ephemeral=True)

    # Check the user has the required role
    user_roles = []
    for role in inter.author.roles:
        user = role.name
        user_roles.append(user)
    if required_role not in user_roles:
        await inter.edit_original_message("I understand your command. Request denied.")
        return

    # find the channel, where to send the message
    channels: [disnake.abc.GuildChannel] = await inter.guild.fetch_channels()
    channel = None
    for ch in channels:
        if ch.name == channel_name:
            channel = ch

    # find PS2 role, that should be Tagged:
    roles: [disnake.Role] = inter.guild.roles
    role_to_ping = None
    for r in roles:
        if r.name == role_name:
            role_to_ping = r

    if channel is None or role_to_ping is None:
        await inter.edit_original_message("Impossible. Perhaps the Archives are incomplete." +
                                          f"\n channel `{channel_name}` or role `{role_name}` doesn't exist")
    elif not channel.permissions_for(inter.author).send_messages:
        await inter.edit_original_message(
            "Imitating the Captain, huh? Surely that violates some kind of Starfleet protocol." +
            "\n You don't have the permission to announce, so I won't"
        )
    elif not channel.permissions_for(channel.guild.me).send_messages:
        await inter.edit_original_message("My lord, is that legal? \n I don't have the permissions to send there")
    else:
        try:
            team_speak = disnake.ui.Button(style=disnake.ButtonStyle.url,
                                           url="https://invite.teamspeak.com/ts.fugaming.org/?password=futs&channel=Planetside%202%2FOutfit%20drill",
                                           label="Open TeamSpeak")
            await channel.send(role_to_ping.mention, embed=await ops.drill(message_body), components=team_speak,
                               delete_after=18000)
            await inter.edit_original_message("Posted a drill announcement to <#986317590811017268>")
        except Exception as e:
            await inter.edit_original_message("Looks like something went wrong." + str(e))
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

bot.run(discordClientToken)
