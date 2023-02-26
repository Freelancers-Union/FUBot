import logging
import os
import datetime
import asyncio
import pymongo.collection
import auraxium
from auraxium import event
from disnake.ext import commands
from database_connector import Database
from census import Census


class Ps2OutfitPlayerLogger(commands.Cog):
    def __init__(
            self,
            db: Database,
            bot: commands.Bot
    ):
        """
        initializes ps2 logger.
        Parameters
        ----------
        db: Database class instance to use
        """
        FU_id = 37509488620602936
        nFUc_id = 37558455247570544
        vFUs_id = 37558804429669935
        SNGE_id = 37516191867639145
        self._monitored_outfits: {int} = {FU_id, nFUc_id, vFUs_id, SNGE_id}
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

    async def _save_player_count(self, outfit):
        """
        Saves the player count of an outfit to the database

        Parameters
        ----------
        outfit: Class of outfit to save
        """
        timestamp = datetime.datetime.utcnow()
        online_count = await Census.get_online_outfit_members(outfit)
        self.collection.insert_one(
            {
                "metadata": {"outfit": outfit.id, "outfit_name": outfit.name},
                "player_count":len(online_count),
                "timestamp": timestamp
            }
        )

    async def ps2_outfit_events(self) -> None:
        """
        Creates event listeners for log in/out events. 
        Events for monitored outfits are saved to the database
        """
        client = auraxium.event.EventClient(service_id=os.getenv('CENSUS_TOKEN'))

        @client.trigger(event=event.PlayerLogout, worlds=[10])
        async def logged_out(_event: event.PlayerLogout):
            character = await Census.get_character(character_id=_event.character_id)
            outfit = await character.outfit()
            if not outfit:
                return
            if outfit.id in self._monitored_outfits:
                logging.info(f"Player [{outfit.alias}] {character.name} logged out")
                await self._save_player_count(outfit)

        @client.trigger(event=event.PlayerLogin, worlds=[10])
        async def logged_in(_event: event.PlayerLogin):
            character = await Census.get_character(character_id=_event.character_id)
            outfit = await character.outfit()
            if not outfit:
                return
            if outfit.id in self._monitored_outfits:
                logging.info(f"Player [{outfit.alias}] {character.name} logged in")
                await self._save_player_count(outfit)


def setup(bot: commands.Bot):
    bot.add_cog(Ps2OutfitPlayerLogger(bot=bot, db=Database))
