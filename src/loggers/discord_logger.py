from database_connector import Database
import logging
import os
import datetime
import asyncio
import time
import typing
import pymongo.collection
import disnake
from disnake.ext import commands
from  send_intro import SendIntro


class DiscordMemberLogger(commands.Cog):
    """
    Logs total guild member count for given guild IDs.
    Members joining or leaving will trigger the updated member count to be logged.
    Parameters
    ----------
    db: Database class instance
    """

    def __init__(
            self,
            bot: commands.Bot,
            db: Database,
    ):
        """
        initializes Discord logger timeseries db
        Parameters
        ----------
        db: Database class instance to use
        """
        FU_guild_id = 282514718445273089
        FU_demo_guild_id = 914185528268689428
        self._monitored_guilds: {int} = {FU_guild_id, FU_demo_guild_id}
        self.collection: pymongo.collection.Collection

        db_collection_name = "discord_member_log"
        collection_options = {'timeField': 'timestamp', 'metaField': 'guild', 'granularity': 'minutes'}

        try:
            self.collection = db.init_timeseries_db(db_collection_name, collection_options)
            # This will create a task. currently, the loop will be run forever by the bot in disnake bots code
            loop = asyncio.get_event_loop()
            loop.create_task(self.discord_guild_events())
        except Exception as exception:
            logging.error("Failed to initialize Discord member logger", exc_info=exception)

    def add_guild(self, guild_id: int):
        """
        Adds a guild to the list of monitored guilds

        Parameters
        ----------
        guild_id: ID of Discord guild to monitor.
        """

        self._monitored_guilds.add(guild_id)

    async def _save_member_count(self, guild_id: int, current_count: int):
        """
        Logs the total members of the guild and writes to the db
        Triggered by join/leave events in Discord
        Parameters
        ----------
        guild_id: ID of Discord guild to monitor.
        current_count: the count to log
        """

        timestamp = datetime.datetime.utcnow()
        self.collection.insert_one(
            {
                "metadata": {"guild": guild_id},
                "member_count": current_count,
                "timestamp": timestamp
            }
        )

    async def _add_member_profile(self, member):
        # Query the DB to see if this user has appeared before.
        query = {"discord_user.id": str(member.id)}
        db_entry = Database.find_one("members", query)
        # If totally new to the DB, add a new entry.
        if db_entry is None:
            disc_obj = {}
            data = {}
            discord_attrs = ["id", "name", "nick"]
            disc_obj["joined_at"] = member.joined_at
            disc_obj["guild"] = str(member.guild.id)
            for count, ele in enumerate(discord_attrs):
                disc_obj[ele] = str(getattr(member, ele))
            data["discord_user"] = disc_obj
            Database.insert_one("members", data)
            # finally, send the intro message
        else:
            # Update their rejoined date
            update_data = {}
            update_data = {"$set": {'discord_user.re-joined': member.joined_at}}
            Database.update_one("members", query, update_data)

        # TODO: We will at some point need to extend this to handle a single user in multiple tracked guilds.
        # But let's cross that bridge when we get to it.

    async def _member_left(self, member):
        # Query the DB to find the user that has left.
        query = {"discord_user.id": str(member.id)}
        db_entry = Database.find_one("members", query)
        timestamp = datetime.datetime.utcnow()
        # Update their db entry to reflect when they left.
        if db_entry is not None:
            update_data = {}
            update_data = {"$set": {'discord_user.left': timestamp}}
            Database.update_one("members", query, update_data)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        guild = member.guild.id
        if guild in self._monitored_guilds:
            await self._save_member_count(guild, member.guild.member_count)
            await self._add_member_profile(member)

    @commands.Cog.listener("on_member_remove")
    async def on_raw_member_remove(self, payload):
        guild = payload.guild.id
        if guild in self._monitored_guilds:
            await self._save_member_count(guild, payload.guild.member_count)
            await self._member_left(payload)


def setup(bot: commands.Bot):
    bot.add_cog(DiscordMemberLogger(bot, Database))
