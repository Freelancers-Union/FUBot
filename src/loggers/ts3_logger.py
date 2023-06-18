#!/usr/bin/python3

import time
import ts3
import datetime
import asyncio
import logging

import disnake
from disnake.ext import commands
from database.models.ts3 import OnlineTeamspeakTS


class TeamSpeak(commands.Cog):
    def __init__(self, bot: commands.Bot):

        ts3conn = ts3.query.TS3ServerConnection(
            "telnet://serveradmin:WxC6HrFVmfG9VtPmSyb7g9BQhjvYreQPz@fugaming.org:10011"
        )
        ts3conn.exec_("use", sid=1)
        self.ts3conn = ts3conn
        self.bot = bot
        self.bot.loop.create_task(self.init_ts3_connection())
        self.channel_dict = {}

    async def get_channel_list(self):
        """
        Retrieves the list of channels from the TeamSpeak server and returns a dictionary
        mapping channel IDs to channel names.

        Parameters
        ----------
        ts3conn : ts3.query.TS3Connection
            The TeamSpeak server query connection object.

        Returns
        -------
        dict
            A dictionary mapping channel IDs to channel names.
        """
        channel_list = self.ts3conn.exec_("channellist")
        channel_dict = {}
        for channel in channel_list:
            channel_dict[channel["cid"]] = channel["channel_name"]
        return channel_dict

    async def init_ts3_connection(self):
        """
        Initializes the TeamSpeak connection and registers the event listener
        """
        # Register for events
        self.ts3conn.exec_("servernotifyregister", event="server")

        while True:
            self.ts3conn.send_keepalive()
            try:
                event = await self.bot.loop.run_in_executor(
                    None, self.ts3conn.wait_for_event, 60
                )
            except ts3.query.TS3TimeoutError:
                pass
            else:
                # Greet new clients.
                if event[0]["reasonid"] == "0" and event[0]["client_type"] == "0":
                    logging.info(
                        f"{event[0]['client_nickname']} connected to TeamSpeak"
                    )
                    await self.log_ts3()
                if event[0]["reasonid"] == "8":
                    await self.log_ts3()
                    logging.info(f"client disconnected from TeamSpeak")

    async def log_ts3(
        self,
    ):
        """
        Logs the current number of connected clients to the database

        """
        online_count = len(self.ts3conn.exec_("clientlist"))
        print(self.ts3conn.exec_("channellist").__dict__)

        await OnlineTeamspeakTS(
            online_count=online_count, timestamp=datetime.datetime.utcnow()
        ).insert()

    def cog_unload(self):
        self.bot.loop.create_task(self.ts3conn.disconnect())


def setup(bot: commands.Bot):
    bot.add_cog(TeamSpeak(bot))
