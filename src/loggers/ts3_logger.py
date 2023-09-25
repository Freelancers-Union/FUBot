import os
import logging
import datetime

import ts3
import disnake
from disnake.ext import commands, tasks

from database.models.ts3 import OnlineTeamspeakTS


class TeamSpeak(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ts3conn = None
        self.channel_dict = {}
        self.routine_ts3_log.start()

    def cog_unload(self):
        self.routine_ts3_log.cancel()
        if self.ts3conn:
            self.ts3conn.disconnect()

    async def wait_for_discord(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def routine_ts3_log(self):
        """
        Logs the current number of connected clients to the database every 10 minutes
        """
        await self.log_ts3()
        await self.update_discord_channel()

    async def log_ts3(self):
        """
        Logs the current number of connected clients to the database
        """
        if not self.ts3conn:
            self.ts3conn = ts3.query.TS3ServerConnection(
                f"telnet://serveradmin:{os.getenv('TEAMSPEAK_PASSWORD')}@fugaming.org:10011"
            )
            self.ts3conn.exec_("use", sid=1)

        online_count = len(self.ts3conn.exec_("clientlist"))
        await OnlineTeamspeakTS(
            online_count=online_count, timestamp=datetime.datetime.utcnow()
        ).insert()

    async def get_channel_list(self):
        if not self.ts3conn:
            self.ts3conn = ts3.query.TS3ServerConnection(
                f"telnet://serveradmin:{os.getenv('TEAMSPEAK_PASSWORD')}@fugaming.org:10011"
            )
            self.ts3conn.exec_("use", sid=1)

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
        other_clients = (
            sum(
                int(channel["total_clients"])
                for channel in channel_list
                if channel["channel_name"] != "AFK"
            )
            - int(arma_clients)
            - int(planetside_clients)
        )

        return {
            "arma": arma_clients,
            "planetside": planetside_clients,
            "other_games": other_clients,
        }

    async def update_discord_channel(self):
        """
        Updates the Discord voice channels with the current number of connected clients for each game
        """
        channel_dict = await self.get_channel_list()
        arma = self.bot.get_channel(1120456354251944059)
        planetside = self.bot.get_channel(1120456220558504060)
        other_games = self.bot.get_channel(1120456423134986260)
        logging.info(f"Updating Discord voice channels with {channel_dict}")

        # Check if the client count for each game has changed
        if arma.name != f"Arma 3 - {channel_dict['arma']}":
            try:
                await arma.edit(name=f"Arma 3 - {channel_dict['arma']}")
            except Exception as e:
                logging.error(f"Error updating Arma 3 channel name: {e}")

        if planetside.name != f"Planetside 2 - {channel_dict['planetside']}":
            try:
                await planetside.edit(
                    name=f"Planetside 2 - {channel_dict['planetside']}"
                )
            except Exception as e:
                logging.error(f"Error updating Planetside 2 channel name: {e}")

        if other_games.name != f"Other - {channel_dict['other_games']}":
            try:
                await other_games.edit(name=f"Other - {channel_dict['other_games']}")
            except Exception as e:
                logging.error(f"Error updating Other Games channel name: {e}")

    @routine_ts3_log.before_loop
    async def before_routine_ts3_log(self):
        await self.wait_for_discord()

    @tasks.loop(seconds=60)
    async def ts3_event_listener(self):
        """
        Initializes the TeamSpeak connection and registers the event listener
        """
        if not self.ts3conn:
            self.ts3conn = ts3.query.TS3ServerConnection(
                f"telnet://serveradmin:{os.getenv('TEAMSPEAK_PASSWORD')}@fugaming.org:10011"
            )
            self.ts3conn.exec_("use", sid=1)
            self.ts3conn.exec_("servernotifyregister", event="server")

        try:
            self.ts3conn.send_keepalive()
            event = await self.bot.loop.run_in_executor(
                None, self.ts3conn.wait_for_event, 60
            )
        except ts3.query.TS3TimeoutError:
            pass
        except ts3.query.TS3TransportError:
            logging.warning("TeamSpeak connection lost. Attempting to reconnect...")
            self.ts3conn.disconnect()
            self.ts3conn = None
        else:
            if event[0]["cfid"] == "0" and event[0]["client_type"] == "0":
                logging.info(f"{event[0]['client_nickname']} connected to TeamSpeak")
                await self.log_ts3()
                await self.update_discord_channel()
            if event[0]["cfid"] == "1":
                await self.log_ts3()
                await self.update_discord_channel()
                logging.info(f"A client disconnected from TeamSpeak")


def setup(bot: commands.Bot):
    bot.add_cog(TeamSpeak(bot))
