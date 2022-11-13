import src.helpers.discord_checks as dc
import urllib.parse
import random
import glob
import disnake


async def event_message(
        inter: disnake.interactions.application_command.ApplicationCommandInteraction,
        message_body,
        event
):
    ops_dict = {
        "Drill": ["Outfit Drill", "Planetside 2"],
        "Casual": ["Casual Play", "Planetside 2"],
        "FUAD": ["FUAD (Armoured Division)", "Planetside 2"],
        "FUAF": ["FUAF (Air Force)", "Planetside 2"],
        "FUBG": ["FUBG (Builders Group)", "Planetside 2"],
        "FUEL": ["FUEL (Emerging Leaders)", "Planetside 2"],
        "FUGG": ["FUGG (Galaxy Group)", "Planetside 2"],
        "Huntsmen": ["Huntsmen", "Planetside 2"],
        "ArmaOps": ["", "Arma 3"]
    }
    game = ops_dict[event][1]
    teamspeak_channel = ops_dict[event][0]
    channel_name: str = ""
    if game == "Planetside 2":
        channel_name = "ps2-annosuncements"
    elif game == "Arma 3":
        channel_name = "a3-announcements"

    # find the channel, where to send the message
    channel = await dc.get_channel(inter=inter, channel_name=channel_name, send_error=True)
    role_to_ping = await dc.get_role(inter=inter, role_name=ops_dict[event][1], send_error=True)

    if not channel or \
            not role_to_ping or \
            not await dc.bot_has_permission(inter=inter, channel=channel, write=True, send_error=True) or \
            not await dc.user_or_role_has_permission(inter=inter, channel=channel, write=True, send_error=True):
        return
    else:
        try:
            teamspeak_channel.encode('utf-8')
            teamspeak_channel = urllib.parse.quote(str(game + "/" + teamspeak_channel), safe="")
            team_speak = disnake.ui.Button(style=disnake.ButtonStyle.url,
                                           url="https://invite.teamspeak.com/ts.fugaming.org/?password=futs&channel=" + str(
                                               teamspeak_channel),
                                           label="Open TeamSpeak")
            Message = await message_embed(message_body, game, event)  # eval(str(event.lower()) + "(message_body)")
            Message.set_image(
                file=disnake.File(fp=random.choice(glob.glob("./assets/splash_art/" + str(event.lower()) + "/*.png")))
            )
            await channel.send(role_to_ping.mention, embed=Message, components=team_speak,
                               delete_after=18000)
            await inter.edit_original_message("Posted a " + str(event) + " announcement to " + channel.mention)
        except Exception as e:
            raise e


async def message_embed(message_body, game, event):
    title = str(game) + " - " + str(event)
    if "arma" in str.lower(game):
        title = "Main Operation - Starting in 1 h"
    else:
        title += " - Starting NOW!"
    # Arma 3
    Message = disnake.Embed(
        title=title,
        color=0x9E0B0F,
        description=str(message_body),
    )
    await globals()[event.lower()](Message)
    return Message


async def drill(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message


async def casual(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message


async def fugg(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message


async def fubg(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For relaxation, calm thoughts and stress free building.",
    )
    return Message


async def fuad(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message


async def fuaf(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message


async def huntsmen(Message):
    Message.add_field(
        name="TeamSpeak is Mandatory!",
        value="Hit the button below to go straight there.",
    )
    return Message


async def fuel(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message


async def armaops(Message):
    Message.add_field(
        name="Join us on TeamSpeak?",
        value="Get your TFAR's ready!",
    )
    return Message
