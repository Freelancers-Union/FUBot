import urllib.parse
from typing import List
import random
import glob
import disnake

async def event_message(
    inter,
    message_body,
    event
):

    ops_dict = {
    "Drill": ["Outfit Drill", "Planetside 2", "Planetside 2"],
    "Casual": ["Casual Play", "Planetside 2", "Planetside 2"],
    "FUAD": ["FUAD (Armoured Division)", "FUAD", "Planetside 2"],
    "FUBG": ["FUBG (Builders Group)", "FUBG", "Planetside 2"],
    "FUEL": ["FUEL (Emerging Leaders)", "Planetside 2", "Planetside 2"],
    "FUGG": ["FUGG (Galaxy Group)", "FUGG", "Planetside 2"],
    "Huntsmen": ["Huntsmen (not this outfit)", "Huntsmen", "Planetside 2"],
    "ArmaOps": ["", "Arma 3", "Arma 3"]
    }
    game = ops_dict[event][2]
    teamspeak_channel = ops_dict[event][0]
    if game == "Planetside 2":
        required_role = "PS2 Division Officer"
        channel_name = "ps2-announcements"
    elif game == "Arma 3":
        required_role = "Arma Division Officer"
        channel_name = "a3-announcements"
    role_name = ops_dict[event][1]

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
            teamspeak_channel.encode('utf-8')
            teamspeak_channel = urllib.parse.quote(str(game + "/" + teamspeak_channel), safe="")
            team_speak = disnake.ui.Button(style=disnake.ButtonStyle.url,
                                           url="https://invite.teamspeak.com/ts.fugaming.org/?password=futs&channel="+str(teamspeak_channel),
                                           label="Open TeamSpeak")
            Message = await message_embed(message_body, game, event) #eval(str(event.lower()) + "(message_body)")
            Message.set_image(
                file=disnake.File(fp=random.choice(glob.glob("./assets/splash_art/"+str(event.lower())+"/*.png")))
            )
            await channel.send(role_to_ping.mention, embed=Message, components=team_speak,
                               delete_after=18000)
            await inter.edit_original_message("Posted a " + str(event) + " announcement to " + str(channel.id))
        except Exception as e:
            raise e


async def message_embed(message_body, game, event):
    Message = disnake.Embed(
            title=str(game) + " - " + str(event) + " - Starting NOW!",
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
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            )
    return Message
