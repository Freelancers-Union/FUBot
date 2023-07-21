import logging
import datetime
from auraxium import ps2
from beanie import BulkWriter
from disnake.ext import commands, tasks
from census import Census
from database.models.planetside2 import PS2RibbonTS, Ps2RibbonMetaData
from models.ps2.general import Ps2RibbonIDs


class Ps2OutfitRibbonLogger(commands.Cog):
    def __init__(
            self,
            bot: commands.Bot,
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

        self.monitored_outfits: set[int] = {FU_id, nFUc_id, vFUs_id, SNGE_id}
        self.logged_ribbons = [Ps2RibbonIDs.PlatoonLeadership, Ps2RibbonIDs.SquadLeadership]
        

        try:
            self.ps2_outft_ribbon_saver.start()
        except Exception as exception:
            logging.error("Failed to initialize PlanetSide outfit ribbon logger", exc_info=exception)
    
    def cog_unload(self):
        self.ps2_outft_ribbon_saver.cancel()

    @tasks.loop(minutes=60)
    async def ps2_outft_ribbon_saver(self) -> None:
        for outfit_id in self.monitored_outfits:
            outfit = await Census.CLIENT.get_by_id(ps2.Outfit, outfit_id)
            ribbons = await Census.get_outfit_member_ribbons(outfit, self.logged_ribbons)
        
            for ribbon in ribbons:
                async with BulkWriter() as bulk_writer:
                    for achievement in ribbons[ribbon]:
                        new_ribbon_ts_entry = PS2RibbonTS(
                            ribbon_count=achievement.earned_count,
                            timestamp=datetime.datetime.now(), 
                            meta=Ps2RibbonMetaData(ribbon_id=achievement.achievement_id, character_id=achievement.character_id)
                        )
                        last_record = await PS2RibbonTS.find(
                            {"meta": Ps2RibbonMetaData(ribbon_id=achievement.achievement_id, character_id=achievement.character_id)},
                        ).sort(-PS2RibbonTS.timestamp).first_or_none()

                        if last_record is None or last_record.ribbon_count != new_ribbon_ts_entry.ribbon_count:
                                await PS2RibbonTS.insert_one(document = new_ribbon_ts_entry)
                    print(f"inserted {len(ribbons[ribbon])} ribbons for ribbon {ribbon}")


def setup(bot: commands.Bot):
    bot.add_cog(Ps2OutfitRibbonLogger(bot))