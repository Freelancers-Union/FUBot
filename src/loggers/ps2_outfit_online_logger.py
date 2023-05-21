import logging
import os
import datetime
import asyncio
from typing import Union
import auraxium
from auraxium import event
from disnake.ext import commands
from census import Census
from database.models.discord import DiscordGuildTSMetadata
from database.models.planetside2 import Ps2Character, OnlineOutfitMemberTS


class Ps2OutfitPlayerLogger(commands.Cog):
    def __init__(
            self
    ):
        """
        initializes ps2 logger.

        Parameters
        ----------
        """
        FU_id = 37509488620602936
        nFUc_id = 37558455247570544
        vFUs_id = 37558804429669935
        SNGE_id = 37516191867639145
        Dig_id = 37509488620604883
        BHO_id = 37534120470912916
        CTIA_id = 37569919291763416
        self._monitored_outfits: {int} = {FU_id, nFUc_id, vFUs_id, SNGE_id, Dig_id, BHO_id, CTIA_id}

    async def _save_player_count(self, _event: Union[event.PlayerLogin, event.PlayerLogout]):
        """
        Saves the player count of an outfit to the database

        Parameters
        ----------
        outfit: Class of outfit to save
        """
        db_character = await Ps2Character.find_one(Ps2Character.character_id == _event.character_id)
        if not db_character:
            return
        logging.info(f"Player [{db_character.name}] from {db_character.outfit_id} logged in or out of PS2")

        # online_count = await Census.get_online_outfit_members(outfit)
        await OnlineOutfitMemberTS(
            online_count=50,
            outfit=db_character.outfit_id,
            timestamp=datetime.datetime.utcnow()
        ).insert()

    async def ps2_outfit_events(self) -> None:
        """
        Creates event listeners for log in/out events. 
        Events for monitored outfits are saved to the database
        """
        client = auraxium.event.EventClient(service_id=os.getenv('CENSUS_TOKEN'))

        @client.trigger(event=event.PlayerLogout, worlds=[10])
        async def logged_out(_event: event.PlayerLogout):
            await self._save_player_count(_event)

        @client.trigger(event=event.PlayerLogin, worlds=[10])
        async def logged_in(_event: event.PlayerLogin):
            await self._save_player_count(_event)


def setup(bot: commands.Bot):
    bot.add_cog(Ps2OutfitPlayerLogger())
