import logging
import os
from datetime import datetime
from database_connector import Database
import census
import pymongo.collection
from auraxium import event, ps2
import auraxium
from disnake.ext import commands, tasks


class PS2OutfitMembers(commands.Cog):
    def __init__(
            self,
            _db: Database,
            bot: commands.Bot
    ):
        try:
            self.bot = bot
            self.db = _db.DATABASE
            # check if the database contains such collection
            self._monitored_outfits = ["FU", "nFUc", "vFUs", "SNGE"]

            for outfit in self._monitored_outfits:
                collection_name = "ps2_outfit_members_" + str(outfit)
                current_collection_options = self.db[collection_name].options()

                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(name=collection_name)
                elif "timeseries" in current_collection_options.keys():
                    raise Exception(f"collection {collection_name} exists, but is a timeseries")

            self.client = auraxium.event.EventClient(service_id=os.getenv('CENSUS_TOKEN'))
            self.update_outfit_members.start()
        except Exception as exception:
            logging.error("Failed to initialize PS2 Outfit Member Collection", exc_info=exception)

    def cog_unload(self):
        self.update_outfit_members.cancel()

    async def _get_api_outfit_members(self, outfit):
        outfit, online_members = await census.get_outfit(
            outfit_name=0,
            outfit_tag=str(outfit),
            client=self.client)
        live_members = await outfit.members()
        return live_members

    async def add_new_members(self, new_members, collection):
        if collection is not None and len(new_members) != 0:
            data = []
            for member in new_members:
                ps2_player_object = {}
                character_obj = await member.character()
                rank = {
                    "rank": member.rank,
                    "time": datetime.now()
                }
                ps2_player_object["_id"] = member.id
                ps2_player_object["name"] = str(character_obj.name)
                ps2_player_object["active_member"] = True
                ps2_player_object["outfit_id"] = member.outfit_id
                ps2_player_object["member_since"] = datetime.fromtimestamp(member.member_since)
                ps2_player_object["rank_history"] = [rank]
                data.append(ps2_player_object)
                # Write to the DB
            if not data:
                return
            else:
                collection.insert_many(data)

    async def member_left_outfit(self, old_members, collection):
        if collection is not None and len(old_members) != 0:
            for member in old_members:
                if member.get("active_member") is True:
                    collection.update_one({'_id': member.get("_id")}, {
                        '$push': {'left_outfit_date': datetime.now()},
                        '$set': {'active_member': False}
                    })

    async def member_rejoined_outfit(self, returning_members, collection):
        if collection is not None and len(returning_members) != 0:
            for member in returning_members:
                collection.update_one({'_id': member.id}, {
                    '$push': {'rejoined_outfit_date': datetime.now()},
                    '$set': {'active_member': True}
                })

    @tasks.loop(minutes=1.0)
    async def update_outfit_members(self):
        """
            Updates each outfit collection with the latest Outfit member information
        """
        try:
            # For each outfit: Get a list of all outfit members from the API
            for outfit in self._monitored_outfits:
                collection = self.db["ps2_outfit_members_" + str(outfit)]
                live_members = await self._get_api_outfit_members(outfit)

                # Get a list of dictionaries of members in the DB
                db_result = collection.find({}, {
                    "_id": 1,
                    "left_outfit_date": 1,
                    "active_member": 1,
                    "rank_history": 1
                })
                db_members = []
                for result in db_result:
                    db_members.append(result)

                # Establish which members are new and which have rejoined
                new_members = []
                returning_members = []
                live_member_ids = []
                updated_ranks = []
                for member in live_members:
                    live_member_ids.append(member.id)
                    # List comprehension:
                    # If a dictionary in the list of dictionaries (db_members) does not have a key "_id" with a value equal to the member.id then:
                    if not any(d.get('_id') == member.id for d in db_members):
                        new_members.append(member)

                    elif any(d.get('_id') == member.id and d.get('active_member') is False for d in db_members):
                        returning_members.append(member)

                # Establish which members have left the outfit
                left_members = []
                for member in db_members:
                    if member.get('_id') not in live_member_ids:
                        left_members.append(member)

                # Perform database actions
                await self.add_new_members(new_members, collection)
                await self.member_rejoined_outfit(returning_members, collection)
                await self.member_left_outfit(left_members, collection)

        except Exception as exception:
            logging.error("Failed to update PS2 Outfit Member Collection", exc_info=exception)


def setup(bot: commands.Bot):
    bot.add_cog(PS2OutfitMembers(bot=bot, _db=Database))
