#!/usr/bin/python3
import os
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
            f"telnet://serveradmin:{os.getenv('TEAMSPEAK_PASSWORD')}@fugaming.org:10011"
        )
        ts3conn.exec_("use", sid=1)
        self.ts3conn = ts3conn
        self.bot = bot
        self.bot.loop.create_task(self.ts3_event_listener())
        self.channel_dict = {}
        # channel_dict = asyncio.create_task(self.get_channel_list())
        # self.channel_dict = channel_dict

    # async def get_channel_list(self):
    #     """
    #     Retrieves the list of channels from the TeamSpeak server and returns a dictionary
    #     mapping channel IDs to channel names.

    #     Returns
    #     -------
    #     dict
    #         A dictionary mapping channel IDs to channel names.
    #     """
    #     channel_list = self.ts3conn.exec_("channellist")
    #     print(f"Channels: {len(channel_list)}")
    #     print(type(channel_list))
    #     channel_dict = {}
    #     for channel in channel_list:
    #         channel_dict[channel["cid"]] = channel["channel_name"]
    #     print(type(channel_dict))
    #     # logging.info(
    #     #     f"TeamSpeak event listener started\n{len(channel_dict)} channels found"
    #     # )
    #     return channel_dict

    async def get_channel_list(self):
        channel_list = self.ts3conn.exec_("channellist").parsed

        # Get list of channels for each game
        arma_channels = [
            channel
            for channel in channel_list
            if channel["pid"] == "0" and "Arma" in channel["channel_name"]
        ]
        planetside_channels = [
            channel
            for channel in channel_list
            if channel["pid"] == "0" and "Planetside" in channel["channel_name"]
        ]
        other_games_channels = [
            channel
            for channel in channel_list
            if channel["pid"] == "0" and "Other Games" in channel["channel_name"]
        ]

        # Calculate total number of clients in each game's subchannels
        arma_clients = sum(
            int(channel["total_clients"])
            for channel in channel_list
            if channel["pid"] in [c["cid"] for c in arma_channels]
        )
        planetside_clients = sum(
            int(channel["total_clients"])
            for channel in channel_list
            if channel["pid"] in [c["cid"] for c in planetside_channels]
        )
        other_games_clients = sum(
            int(channel["total_clients"])
            for channel in channel_list
            if channel["pid"] in [c["cid"] for c in other_games_channels]
        )

        return {
            "arma": arma_clients,
            "planetside": planetside_clients,
            "other_games": other_games_clients,
        }

    async def ts3_event_listener(self):
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
                print(event[0])
                if event[0]["reasonid"] == "0" and event[0]["client_type"] == "0":
                    logging.info(
                        f"{event[0]['client_nickname']} connected to TeamSpeak"
                    )
                    await self.log_ts3()
                    await self.update_discord_channel()
                if event[0]["reasonid"] == "8":
                    await self.log_ts3()
                    await self.update_discord_channel()
                    logging.info(f"client disconnected from TeamSpeak")

    async def log_ts3(
        self,
    ):
        """
        Logs the current number of connected clients to the database

        """
        online_count = len(self.ts3conn.exec_("clientlist"))

        await OnlineTeamspeakTS(
            online_count=online_count, timestamp=datetime.datetime.utcnow()
        ).insert()

    def cog_unload(self):
        self.bot.loop.create_task(self.ts3conn.disconnect())

    async def update_discord_channel(self):
        """
        Updates the Discord voice channels with the current number of connected clients for each game
        """
        channel_dict = await self.get_channel_list()
        arma = self.bot.get_channel(1120456354251944059)
        planetside = self.bot.get_channel(1120456220558504060)
        other_games = self.bot.get_channel(1120456423134986260)

        await arma.edit(name=f"Arma 3 - {channel_dict['arma']}")
        await planetside.edit(name=f"Planetside 2 - {channel_dict['planetside']}")
        await other_games.edit(name=f"Other Games - {channel_dict['other_games']}")


def setup(bot: commands.Bot):
    bot.add_cog(TeamSpeak(bot))
