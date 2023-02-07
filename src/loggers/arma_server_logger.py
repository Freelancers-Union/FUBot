import logging
import os
import datetime
from steam import SteamQuery
from database_connector import Database


class ArmaLogger:
    def __init__(self, _db: Database):
        try:
            db = _db.DATABASE
            # check if the database contains such collection
            collection_options = {'timeField': 'timestamp', 'metaField': 'mission', 'granularity': 'hours'}
            collection_name = "arma_player_count"
            current_collection_options = db[collection_name].options()

            if collection_name not in db.list_collection_names():
                db.create_collection(name=collection_name, timeseries=collection_options,
                                     expireAfterSeconds=94608000)
            elif "timeseries" not in current_collection_options.keys():
                raise Exception(f"collection {collection_name} exists, but isn't timeseries")

            self.collection = db[collection_name]
            self.server_query = SteamQuery(os.getenv("ARMA_HOST"), int(os.getenv("ARMA_QUERY_PORT")))
        except Exception as exception:
            logging.error("Failed to initialize ArmA logger", exc_info=exception)

    def log_server_status(self):
        """
            Logs the max amount of players in server currently.
            If it can't connect to arma, it saves -1 as player count
        """
        try:
            response = self.server_query.query_game_server()
            player_count = response.get("players")
            mission = response.get("description")
            if self.collection is not None:
                timestamp = datetime.datetime.utcnow()
                last = self.collection.find_one(sort=[("timestamp", pymongo.DESCENDING)])

                player_count = player_count if player_count is not None else -1
                mission = mission if player_count is not None else None

                if not player_count:
                    logging.info("ArmA player count unchanged")
                if last["player_count"] != player_count:
                    self.collection.insert_one({
                        "metadata": {"mission": mission},
                        "player_count": player_count,
                        "timestamp": timestamp
                    })
        except Exception as exception:
            logging.error("Something went wrong logging ArmA3 server", exc_info=exception)
