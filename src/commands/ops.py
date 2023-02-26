import os
import urllib.parse
import random
import glob
import time
from typing import List
import disnake
from disnake.ext import commands
from disnake import Webhook
import aiohttp
import helpers.discord_checks as dc

class AnnounceEvent(commands.Cog):
    """
    Class cog for ps2 squad markup help message.
    """

    @commands.slash_command(dm_permission=False)
    async def announce(self, inter):
        pass

    @announce.sub_command()
    async def event(
            self,
            inter: disnake.CommandInteraction,
            event: str,
            message_body: str = "Find us in game."
    ):
        """
        Post an event announcement to #ps2-announcements

        Parameters
        ----------
        inter: disnake.CommandInteraction
            The interaction object
        event: str
            The event to announce.
        message_body: str
            The message to attach to the announcement.

        """
        await inter.response.defer(ephemeral=True)
        ops_dict = {
            "Drill": {"short_title":"Drill" ,"ts_channel": "Outfit Drill", "game": "Planetside 2", "ping_role": "Planetside 2", "color": 0x9E0B0F},
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
        channel = await dc.get_channel(inter=inter, channel_name=channel_name, send_error=True)
        role_to_ping = await dc.get_role(inter=inter, role_name=ops_dict[event]["ping_role"], send_error=True)

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
                                            url="https://invite.teamspeak.com/ts.fugaming.org/?password=futs&channel=" +
                                                str(teamspeak_channel),
                                            label="Click to open TeamSpeak")
                Message = await self.message_embed(message_body, ops_dict[event])
                Message.set_image(
                    file=disnake.File(fp=random.choice(glob.glob("./assets/splash_art/" + str(ops_dict[event]["short_title"].lower()) + "/*.png")))
                )
                await channel.send(role_to_ping.mention, embed=Message, components=team_speak,
                                delete_after=18000)
                await inter.edit_original_message("Posted a " + str(ops_dict[event]["short_title"]) + " announcement to " + channel.mention)
                if ops_dict[event]["game"] == "Planetside 2":
                    await self.webhook_send(ops_dict[event])
            except Exception as e:
                raise e

    @event.autocomplete("event")
    async def autocomplete_event(self, inter: disnake.CommandInteraction, string: str) -> List[str]:
        events = ["Drill", "nFUc", "vFUs", "Casual", "FUAD", "FUAF", "FUBG", "FUEL", "FUGG", "Huntsmen", "ArmaOps"]
        return [event for event in events if string.lower() in event.lower()]

    async def message_embed(self, message_body, event):
        
        if "arma" in str.lower(event["game"]):
            title = "Main Operation - Starting in 1 h"
        else:
            title = str(event["ts_channel"]) + " - Starting NOW!"

        Message = disnake.Embed(
            title=title,
            color=event["color"],
            description=str(message_body),
        )
        await getattr(self, event["short_title"].lower())(Message)
        return Message


    async def drill(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message


    async def casual(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message


    async def fugg(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message


    async def fubg(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For relaxation, calm thoughts and stress free building.",
        )
        return Message


    async def fuad(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message


    async def fuaf(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message


    async def huntsmen(self, Message):
        Message.add_field(
            name="TeamSpeak is Mandatory!",
            value="Hit the button below to go straight there.",
        )
        return Message


    async def fuel(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message


    async def armaops(self, Message):
        Message.add_field(
            name="Join us on TeamSpeak",
            value="Get your TFAR's ready!",
        )
        return Message

    async def nfuc(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message

    async def vfus(self, Message):
        Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
        )
        return Message


    async def webhook_send(self, event):
        """

        Parameters
        ----------
        Send a webhook to the interlink discord
        """
        if os.getenv('INTERLINK_WEBHOOK'):
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(os.getenv('INTERLINK_WEBHOOK'), session=session)
                message = "FU has started an event!\n**" + str(event["short_title"]) + "**\n<t:" + str(int(time.time())) + ":R>"
                await webhook.send(message, username='FUBot', avatar_url='https://www.fugaming.org/uploads/1/3/0/9/130953309/editor/pslogo1417p.png?1617516785')

def setup(bot):
    bot.add_cog(AnnounceEvent(bot))