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


class DiscordMemberLogger(commands.Cog):
    """
    Logs total guild member count for given guild IDs.
    Members joining or leaving will trigger the updated member count to be logged.
    Parameters
    ----------
    db: Database class instance
    saving_period: time in seconds for fow frequently the data should be saved
    """
    def __init__(
            self,
            bot: commands.Bot,
            db: Database,
            saving_period: float = 5 * 60
    ):
        """
        initializes Discord logger timeseries db
        Parameters
        ----------
        db: Database class instance to use
        saving_period: time in seconds for fow frequently the data should be saved
        """
        self.saving_period: float = saving_period
        FU_guild_id = 282514718445273089
        FU_demo_guild_id = 914185528268689428
        self._monitored_guilds: {int} = {FU_guild_id, FU_demo_guild_id}
        self._max_member_count: typing.Dict[int: int] = dict.fromkeys(self._monitored_guilds, None)
        self._last_member_count_save_time: float = .0
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
        self._max_member_count[guild_id] = None
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
        if not self._max_member_count[guild_id] or current_count > self._max_member_count[guild_id]:
            self._max_member_count[guild_id] = current_count

        if time.time() > self._last_member_count_save_time + self.saving_period:
            self._last_member_count_save_time = time.time()

            tmp_store = self._max_member_count.copy()  # not 100% sure how async works in python, so going safe way
            self._max_member_count = dict.fromkeys(self._monitored_guilds, None)
            timestamp = datetime.datetime.utcnow()
            for guild in tmp_store:
                if tmp_store[guild]:
                    self.collection.insert_one(
                        {
                            "metadata": {"guild": guild},
                            "member_count": tmp_store[guild],
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
            discord_attrs = ["id", "name", "nick", "joined_at"]
            disc_obj["name"] = str(member)
            disc_obj["guild"] = str(member.guild.id)
            for count, ele in enumerate(discord_attrs):
                disc_obj[ele] = str(getattr(member, ele))
            data["discord_user"] = disc_obj
            Database.insert_one("members", data)
        else:
            rejoined = {}
            rejoined["discord_user"]["re-joined_at"] = member.joined_at
            Database.update_one("members", query, rejoined)
        # We will at some point need to extend this to handle a single user in multiple guilds.
        # But let's cross that bridge when we get to it.


    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        guild = member.guild.id
        if guild in self._monitored_guilds:
            await self._save_member_count(guild, member.guild.member_count)
            await self._add_member_profile(member)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        guild = member.guild.id
        if guild in self._monitored_guilds:
            await self._save_member_count(guild, member.guild.member_count)
            

def setup(bot: commands.Bot):
    bot.add_cog(DiscordMemberLogger(bot, Database))
