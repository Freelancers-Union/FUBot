import logging
from census import Census

from datetime import datetime
from disnake.ext import commands, tasks
from models.ps2.outfit_with_member_characters import Ps2OutfitMember

from database.models.planetside2 import Ps2Character, RankHistory
from beanie.operators import In, Set, Push


class PS2OutfitMembers(commands.Cog):
    def __init__(
            self
    ):
        try:
            # todo: this should be read from the database
            FU_id = 37509488620602936
            nFUc_id = 37558455247570544
            vFUs_id = 37558804429669935
            SNGE_id = 37516191867639145
            Dig_id = 37509488620604883
            BHO_id = 37534120470912916
            CTIA_id = 37569919291763416
            self._monitored_outfits: dict[int] = {FU_id, nFUc_id, vFUs_id, SNGE_id, Dig_id, BHO_id, CTIA_id}
            logging.info("Synchronising outfit members with database...")
            self.update_outfit_members.start()

        except Exception as exception:
            logging.error("Failed to initialize PS2 Outfit Member Collection", exc_info=exception)

    def cog_unload(self):
        logging.info("Unloading PS2 Outfit Member logging cog")
        self.update_outfit_members.cancel()

    @tasks.loop(minutes=30.0)
    async def update_outfit_members(self):
        """
            Updates each outfit collection with the latest Outfit member information
        """
        try:
            # For each outfit: Get a list of all outfit members from the API
            for outfit_id in self._monitored_outfits:
                current_members = await Census.get_outfit_with_member_characters(outfit_id)

                # Get a list of dictionaries of members in the DB
                db_members = await Ps2Character.find_many(Ps2Character.outfit_id == outfit_id).project(
                    Ps2Character
                ).to_list()

                if not db_members:
                    logging.info("Outfit {} has no members in the database. adding {} members".format(
                        outfit_id,
                        len(current_members))
                    )
                    await _add_new_members(current_members, outfit_id)
                    continue

                # Establish which members are new and which have rejoined
                new_members: list[Ps2OutfitMember] = []
                outdated_ranks: list[Ps2Character] = []
                for member in current_members:
                    # Check if the member is already in the database
                    db_character = next((db_member for db_member in db_members if db_member.id == member.character_id),
                                        None)
                    if db_character:
                        # Check for any changes in rank
                        if db_character.rank != member.rank:
                            db_character.rank = member.rank
                            outdated_ranks.append(db_character)
                        db_members.remove(db_character)
                    else:
                        new_members.append(member)

                logging.info("Outfit {} has {} new, {} left and {} ranks are outdated".format(
                    outfit_id, len(new_members), len(db_members), len(outdated_ranks)
                ))

                # everyone left in the db_members list has left the outfit
                await _member_left_outfit(db_members, outfit_id)

                # Perform database actions
                await _add_new_members(new_members, outfit_id)
                await _update_member_ranks(outdated_ranks)

        except Exception as exception:
            logging.error("Failed to update PS2 Outfit Member Collection", exc_info=exception)


async def _update_member_ranks(outdated_rank_members: list[Ps2Character]):
    """
    Saves to database the new rank of each member in the list.
    This assumes that the character object already has the new rank already set
    Parameters
    ----------
    outdated_rank_members:
        List of Ps2Character objects with outdated ranks.
    """
    for member in outdated_rank_members:
        await Ps2Character.find_one(Ps2Character.id == member.character_id).update_one(
            Set({Ps2Character.rank: member.rank}),
            Push({
                Ps2Character.rank_history: RankHistory(
                    name=member.rank,
                    outfit_id=member.outfit_id,
                    added=datetime.now()
                )
            })
        )


async def _member_left_outfit(db_characters: list[Ps2Character], outfit_id: int):
    """
    Updates the database to reflect that the member has left the outfit
    Parameters
    ----------
    db_characters:
        List of PS2 characters that have left the outfit
    outfit_id:
        The outfit id of the outfit that the members have left
    """
    await Ps2Character.find(In(Ps2Character.id, [character.id for character in db_characters])).update(
        Set({
            Ps2Character.outfit_id: None,
            Ps2Character.rank: None,
            Ps2Character.joined: None,
        }),
        Push({
            Ps2Character.rank_history: RankHistory(
                name="LEFT",
                outfit_id=outfit_id,
                added=datetime.now(),
            )
        })
    )


async def _add_new_members(new_members: list[Ps2OutfitMember], outfit_id: int):
    for member in new_members:
        db_char = await Ps2Character.find_one(Ps2Character.id == member.character_id)
        if db_char:
            await db_char.update(
                Set({
                    Ps2Character.rank: member.rank,
                    Ps2Character.outfit_id: outfit_id,
                    Ps2Character.joined: member.member_since_date,
                }),
                Push({
                    Ps2Character.rank_history: RankHistory(
                        name=member.rank,
                        outfit_id=outfit_id,
                        added=member.member_since_date
                    )
                })
            )
        else:
            await Ps2Character(
                id=member.character_id,
                outfit_id=outfit_id,
                name=member.character.name.first,
                rank=member.rank,
                joined=member.member_since_date,
                left=None,
                rank_history=[
                    RankHistory(
                        name=member.rank,
                        outfit_id=outfit_id,
                        added=member.member_since_date
                    )
                ]
            ).insert()


def setup(bot: commands.Bot):
    bot.add_cog(PS2OutfitMembers())


# # todo: delete this
# import os
#
# logging.basicConfig(
#     level=os.getenv('LOGLEVEL'),
#     format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
# )

# import asyncio
# from database import init_database, get_mongo_uri
# async def main():
#     await init_database(get_mongo_uri(), "FUBot")
#     await PS2OutfitMembers().update_outfit_members()
#
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
