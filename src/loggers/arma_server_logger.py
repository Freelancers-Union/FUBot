import logging
import os
import datetime
from steam import SteamQuery
from src.database_connector import Database


class ArmaLogger:
    def __init__(self, db: Database, arma_host: str):
        try:
            # check if the database contains such collection
            collection_options = {'timeField': 'timestamp', 'metaField': 'mission', 'granularity': 'hours'}
            collection_name = "arma_player_count"
            current_collection_options = db.DATABASE[collection_name].options()
            if "timeseries" not in current_collection_options.keys():
                raise Exception(f"collection {collection_name} exists, but isn't timeseries")
            if not current_collection_options:
                db.DATABASE.create_collection('testColl', timeseries=collection_options, expireAfterSeconds=94608000)

            self.collection = db.DATABASE[collection_name]
            self.server_query = SteamQuery(os.getenv("ARMA_HOST"), int(os.getenv("ARMA_QUERY_PORT")))
        except Exception as exception:
            logging.error("Failed to initialize ArmA logger", exc_info=exception)

    def log_server_status(self, ):
        """
            Logs the max amount of players in current hour.
            if there are more people than last time scanned in this hour, the measurement gets updated
            If it can't connect to arma
        """
        try:
            response = self.server_query.query_game_server()
            player_count = response["players"]
            mission = response["description"]
        except Exception as exception:
            player_count = -1
            mission = "None"
            logging.error("Failed to log ArmA server status", exc_info=exception)

        if self.collection:
            timestamp = datetime.datetime.utcnow().replace(microsecond=0, second=0, minute=0)
            previous_value = list(self.collection.find({"timestamp": timestamp}))

            if not previous_value or previous_value[0]["player_count"] < player_count:
                self.collection.insert_one({
                    "metadata": {"mission": mission},
                    "player_count": player_count,
                    "timestamp": timestamp
                })
