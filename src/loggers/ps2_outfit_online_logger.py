import logging
import os
import datetime
from typing import Union
from auraxium import event, ps2
from disnake.ext import commands
from census import Census
from database.models.planetside2 import Ps2Character, OnlineOutfitMemberTS


class Ps2OutfitPlayerLogger(commands.Cog):
    def __init__(
            self,
            bot
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
        self._monitored_outfits: dict[int] = {FU_id, nFUc_id, vFUs_id, SNGE_id, Dig_id, BHO_id, CTIA_id}

        try:
            bot.loop.create_task(self.ps2_outfit_events())
        except Exception as exception:
            logging.error("Failed to initialize PlanetSide outfit player logger", exc_info=exception)

    async def ps2_outfit_events(self) -> None:
        """
        Creates event listeners for log in/out events. 
        Events for monitored outfits are saved to the database
        """
        client = event.EventClient(service_id=os.getenv('CENSUS_TOKEN'))

        cached_ps2_outfits: dict[int, ps2.Outfit] = {}

        async def _save_player_count(_event: Union[event.PlayerLogin, event.PlayerLogout]):
            """
            Saves the player count of an outfit to the database

            Parameters
            ----------         
            outfit: Class of outfit to save
            """
            db_character = await Ps2Character.find_one(Ps2Character.id == _event.character_id)
            if not db_character:
                return
            
            if db_character.outfit_id not in cached_ps2_outfits.keys():
                cached_ps2_outfits[db_character.outfit_id] = await Census.CLIENT.get_by_id(ps2.Outfit, db_character.outfit_id)

            online_count = await Census.get_online_outfit_members(cached_ps2_outfits[db_character.outfit_id])
            await OnlineOutfitMemberTS(
                online_count=len(online_count),
                outfit_id=db_character.outfit_id,
                timestamp=datetime.datetime.utcnow()
            ).insert()
            logging.info(f"Saved outfit {cached_ps2_outfits[db_character.outfit_id].name} player count of {len(online_count)}")


        @client.trigger(event=event.PlayerLogout, worlds=[10])
        async def logged_out(_event: event.PlayerLogout):
            await _save_player_count(_event)

        @client.trigger(event=event.PlayerLogin, worlds=[10])
        async def logged_in(_event: event.PlayerLogin):
            await _save_player_count(_event)


def setup(bot: commands.Bot):
    bot.add_cog(Ps2OutfitPlayerLogger(bot))
