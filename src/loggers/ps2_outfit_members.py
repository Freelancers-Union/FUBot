import logging
import os
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

    async def update_outfit_members(self):
        """
            Updates the collection with the latest Outfit member information
        """
        try:
            # Get a list of all outfit members from the API
            for outfit in self._monitored_outfits:
                collection = self.db["ps2_outfit_members_"+str(outfit)]
                outfit, online_members = await census.get_outfit(
                    outfit_name = 0,
                    outfit_tag = str(outfit),
                    client = self.client)
                live_members = await outfit.members()

                # build the mongodb document for outfit members in API payload
                data = []
                for member in live_members:
                    ps2_player_object = {}
                    attributes = ["outfit_id", "member_since_date", "rank"]
                    character_obj = await member.character()
                    ps2_player_object["_id"] = member.id
                    ps2_player_object["name"] = str(character_obj.name)
                    for count, ele in enumerate(attributes):
                        ps2_player_object[ele] = str(getattr(member, ele))
                    data.append(ps2_player_object)
                    # Write to the DB
                if collection is not None:
                    collection.insert_many(data)
        except Exception as exception:
            logging.error("Failed to update PS2 Outfit Member Collection", exc_info=exception)
