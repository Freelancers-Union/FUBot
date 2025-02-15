import asyncio
import logging
import os
from steam import SteamQuery


async def get_server_info():
    try:
        server_query = SteamQuery(os.getenv("ARMA_HOST"), int(os.getenv("ARMA_QUERY_PORT")))
        response = server_query.query_server_info()
        player_count: int = response.get("players")
        description: str = response.get("description")
        if not response.get("error") is None:
            logging.error(f"An error occurred while fetching Arma server info: {response.get('error')}")
            return f"An error occurred while fetching Arma server info, is the server online?"
        return f"**Player Count**: {player_count}\n**Mission/Status**: {description}"
    except Exception as ex:
        logging.exception(f"Failed to get Arma server info: {ex}")
        return f"An error occurred while fetching Arma server info, please let the admins know."
