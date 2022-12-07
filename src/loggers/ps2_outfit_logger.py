from database_connector import Database
from auraxium import event, ps2
import census
import logging
import os
import datetime
import asyncio
import time
import typing
import pymongo.collection
import auraxium
from disnake.ext import commands


class Ps2OutfitPlayerLogger(commands.Cog):
    def __init__(
            self,
            db: Database,
            bot: commands.Bot,
            saving_period: float = 5 * 60
    ):
        """
        initializes ps2 logger.
        Parameters
        ----------
        db: Database class instance to use
        saving_period: time in seconds for fow frequently the data should be saved
        """
        self.saving_period: float = saving_period
        FU_id = 37509488620602936
        nFUc_id = 37558455247570544
        vFUs_id = 37558804429669935
        self._monitored_outfits: {int} = {FU_id, nFUc_id, vFUs_id}
        self._max_player_count: typing.Dict[int: int] = dict.fromkeys(self._monitored_outfits, None)
        self._last_player_count_save_time: float = .0
        self.collection: pymongo.collection.Collection

        db_collection_name = "ps2_outfit_player_log"
        collection_options = {'timeField': 'timestamp', 'metaField': 'outfit', 'granularity': 'minutes'}

        try:
            self.collection = db.init_timeseries_db(db_collection_name, collection_options)
            # This will create a task. currently, the loop will be run forever by the bot in disnake bots code
            loop = asyncio.get_event_loop()
            loop.create_task(self.ps2_outfit_events())
        except Exception as exception:
            logging.error("Failed to initialize PlanetSide outfit player logger", exc_info=exception)

    def add_outfit(self, outfit_id: int):
        """
        Adds an outfit to the list of monitored outfits

        Parameters
        ----------
        outfit_id: ID of outfit to monitor. Using ID as that's the only thing that doesn't really change
        """
        self._max_player_count[outfit_id] = None
        self._monitored_outfits.add(outfit_id)

    async def _save_player_count(self, outfit_id: int, current_count: int):
        if not self._max_player_count[outfit_id] or current_count > self._max_player_count[outfit_id]:
            self._max_player_count[outfit_id] = current_count

        if time.time() > self._last_player_count_save_time + self.saving_period:
            self._last_player_count_save_time = time.time()

            tmp_store = self._max_player_count.copy()  # not 100% sure how async works in python, so going safe way
            self._max_player_count = dict.fromkeys(self._monitored_outfits, None)
            timestamp = datetime.datetime.utcnow()
            for outfit in tmp_store:
                if tmp_store[outfit]:
                    self.collection.insert_one(
                        {
                            "metadata": {"outfit": outfit},
                            "player_count": tmp_store[outfit],
                            "timestamp": timestamp
                        }
                    )

    async def ps2_outfit_events(self) -> None:
        client = auraxium.event.EventClient(service_id=os.getenv('CENSUS_TOKEN'))

        @client.trigger(event=event.PlayerLogout, worlds=[10])
        async def logged_out(_event: event.PlayerLogout):
            character = await client.get_by_id(ps2.Character, _event.character_id)
            outfit = await character.outfit()
            if not outfit:
                return
            if outfit.id in self._monitored_outfits:
                await self._save_player_count(outfit.id, await census.get_online_outfit(outfit.id))

        @client.trigger(event=event.PlayerLogin, worlds=[10])
        async def logged_in(_event: event.PlayerLogin):
            character = await client.get_by_id(ps2.Character, _event.character_id)
            outfit = await character.outfit()
            if not outfit:
                return
            if outfit.id in self._monitored_outfits:
                await self._save_player_count(outfit.id, await census.get_online_outfit(outfit.id))


def setup(bot: commands.Bot):
    bot.add_cog(Ps2OutfitPlayerLogger(bot=bot, db=Database))
