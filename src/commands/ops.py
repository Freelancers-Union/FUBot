import os
import helpers.discord_checks as dc
import urllib.parse
import random
import glob
import time
import disnake


async def event_message(
    inter: disnake.interactions.application_command.ApplicationCommandInteraction,
    message_body,
    event,
):
    ops_dict = {
        "Drill": {"short_title":"Drill" ,"ts_channel": "Outfit Drill", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "CombinedArms": {"short_title":"combinedarms" ,"ts_channel": "Combined Arms", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "nFUc": {"short_title":"nFUc" ,"ts_channel": "nFUc", "game": "Planetside 2", "ping_role": "nFUc", "color": 0x004b80},
        "vFUs": {"short_title":"vFUs", "ts_channel": "vFUs", "game": "Planetside 2", "ping_role": "vFUs", "color": 0x440E62},
        "Casual": {"short_title":"Casual", "ts_channel": "Casual Play", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "FUAD": {"short_title":"FUAD" ,"ts_channel": "FUAD (Armoured Division)", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "FUAF": {"short_title":"FUAF", "ts_channel": "FUAF (Air Force)", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "FUBG": {"short_title":"FUBG", "ts_channel": "FUBG (Builders Group)", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "FUEL": {"short_title":"FUEL", "ts_channel": "FUEL (Emerging Leaders)", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "FUGG": {"short_title":"FUGG", "ts_channel": "FUGG (Galaxy Group)", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "Huntsmen": {"short_title":"Huntsmen", "ts_channel": "Huntsmen", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
        "ArmaOps": {"short_title":"ArmaOps", "ts_channel": "", "game": "Arma 3", "ping_role": "Arma 3", "color": 0xb641d}
    }

    game = ops_dict[event]["game"]
    teamspeak_channel = ops_dict[event]["ts_channel"]

    if ops_dict[event]["game"] != "Planetside 2":
        channel_name = "a3-announcements"
    else:
        channel_name = "ps2-announcements"

    # find the channel, where to send the message
    channel = await dc.get_channel(
        inter=inter, channel_name=channel_name, send_error=True
    )
    role_to_ping = await dc.get_role(
        inter=inter, role_name=ops_dict[event]["ping_role"], send_error=True
    )

    if (
        not channel
        or not role_to_ping
        or not await dc.bot_has_permission(
            inter=inter, channel=channel, write=True, send_error=True
        )
        or not await dc.user_or_role_has_permission(
            inter=inter, channel=channel, write=True, send_error=True
        )
    ):
        return
    else:
        try:
            teamspeak_channel.encode("utf-8")
            teamspeak_channel = urllib.parse.quote(
                str(game + "/" + teamspeak_channel), safe=""
            )
            team_speak = disnake.ui.Button(
                style=disnake.ButtonStyle.url,
                url="https://invite.teamspeak.com/ts.fugaming.org/?password=futs&channel="
                + str(teamspeak_channel),
                label="Click to open TeamSpeak",
            )
            Message = await message_embed(message_body, ops_dict[event])
            Message.set_image(
                file=disnake.File(
                    fp=random.choice(
                        glob.glob(
                            "./assets/splash_art/"
                            + str(ops_dict[event]["short_title"].lower())
                            + "/*.png"
                        )
                    )
                )
            )
            await channel.send(
                role_to_ping.mention,
                embed=Message,
                components=team_speak,
                delete_after=18000,
            )
            await inter.edit_original_message(
                "Posted a "
                + str(ops_dict[event]["short_title"])
                + " announcement to "
                + channel.mention
            )
        except Exception as e:
            raise e


async def message_embed(message_body, event):

    if "arma" in str.lower(event["game"]):
        title = "Main Operation - Starting in 1 h"
    else:
        title = str(event["ts_channel"]) + " - Starting NOW!"

    Message = disnake.Embed(
        title=title,
        color=event["color"],
        description=str(message_body),
    )
    await globals()[event["short_title"].lower()](Message)
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
        name="Join us on TeamSpeak",
        value="Get your TFAR's ready!",
    )
    return Message


async def nfuc(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message


async def vfus(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message
  
  
async def combinedarms(Message):
    Message.add_field(
        name="Join the conversation on TeamSpeak",
        value="For chat, tactics and discussion.",
    )
    return Message
