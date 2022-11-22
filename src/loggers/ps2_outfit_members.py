import logging
import os
import datetime
from database_connector import Database
import census
import pymongo.collection
from auraxium import event, ps2
import auraxium


class PS2OutfitMembers:
    def __init__(self, _db: Database):
        try:
            self.db = _db.DATABASE
            # check if the database contains such collection
            self._monitored_outfits = ["FU", "nFUc", "vFUs"]

            for outfit in self._monitored_outfits:
                collection_name = "ps2_outfit_members_"+str(outfit)
                current_collection_options = self.db[collection_name].options()

                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(name=collection_name)
                elif "timeseries" in current_collection_options.keys():
                    raise Exception(f"collection {collection_name} exists, but is a timeseries")

            # self.collection = db[collection_name]
            self.client = auraxium.event.EventClient(service_id=os.getenv('CENSUS_TOKEN'))
        except Exception as exception:
            logging.error("Failed to initialize PS2 Outfit Member Collection", exc_info=exception)

    async def _get_api_outfit_members(self, outfit):
        outfit, online_members = await census.get_outfit(
            outfit_name = 0,
            outfit_tag = str(outfit),
            client = self.client)
        live_members = await outfit.members()
        return live_members

    async def _get_db_outfit_members(self, collection):
        db_ids = []
        old_members = []
        for x in collection.find({}, {"_id":1, "left_outfit_date":1}):
            db_ids.append(x.get("_id"))
            if x.get("left_outfit_date") is not None:
                old_members.append(x.get("_id"))
        return db_ids, old_members

    async def add_new_members(self, new_members, collection):
        if collection is not None and len(new_members) != 0:
            data = []
            for member in new_members:
                ps2_player_object = {}
                attributes = ["outfit_id", "member_since_date", "rank"]
                character_obj = await member.character()
                ps2_player_object["_id"] = member.id
                ps2_player_object["name"] = str(character_obj.name)
                for count, ele in enumerate(attributes):
                    ps2_player_object[ele] = str(getattr(member, ele))
                data.append(ps2_player_object)
                # Write to the DB
            if not data:
                return
            else:
                collection.insert_many(data)

    async def member_left_outfit(self, old_members, collection):
        if collection is not None and len(old_members) != 0:
            for member in old_members:
                collection.update_one({'_id': member}, {'$push': {'left_outfit_date': datetime.now()}})

    async def member_rejoined_outfit(self, returning_members, collection):
        if collection is not None and len(returning_members) != 0:
            for member in returning_members:
                collection.update_one({'_id': member.id}, {'$push': {'rejoined_outfit_date': datetime.now()}})

    async def update_outfit_members(self):
        """
            Updates the collection with the latest Outfit member information
        """
        try:
            # For each outfit: Get a list of all outfit members from the API
            for outfit in self._monitored_outfits:
                collection = self.db["ps2_outfit_members_"+str(outfit)]
                live_members = await self._get_api_outfit_members(outfit)

                # Get a list of all member IDs in the database
                # And a list of all members that have previously left the outfit
                db_members, old_members = await self._get_db_outfit_members(collection)

                # Establish which members are new and which have rejoined
                new_members = []
                returning_members = []
                for member in live_members:
                    if member.id not in db_members:
                        new_members.append(member)
                    elif member.id in old_members:
                        returning_members.append(member)

                # Establish which members have left the outfit
                old_members = []
                for member in db_members:
                    if member not in live_members:
                        old_members.append(member)

                # Perform database actions
                await self.add_new_members(new_members, collection)
                await self.member_rejoined_outfit(returning_members, collection)
                await self.member_left_outfit(old_members, collection)

        except Exception as exception:
            logging.error("Failed to update PS2 Outfit Member Collection", exc_info=exception)
