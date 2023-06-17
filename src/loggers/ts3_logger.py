#!/usr/bin/python3

import time
import ts3
import asyncio

import disnake
from disnake.ext import commands


class TeamSpeak(commands.Cog):
    def __init__(self, bot: commands.Bot):

        ts3conn = ts3.query.TS3ServerConnection(
            "telnet://serveradmin:WxC6HrFVmfG9VtPmSyb7g9BQhjvYreQPz@fugaming.org:10011"
        )
        ts3conn.exec_("use", sid=1)
        self.ts3conn = ts3conn
        self.bot = bot
        self.bot.loop.create_task(self.init_ts3_connection())

    async def init_ts3_connection(self):

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
                    print(f"{event[0]['client_nickname']} connected")
                    # self.ts3conn.exec_(
                    #     "clientpoke",
                    #     clid=event[0]["clid"],
                    #     msg="Hello from FUBot! *This is a test.",
                    # )
                if event[0]["reasonid"] == "8":
                    print(event[0])
                    print(f"client disconnected")

    def cog_unload(self):
        self.bot.loop.create_task(self.ts3conn.disconnect())


def setup(bot: commands.Bot):
    bot.add_cog(TeamSpeak(bot))
