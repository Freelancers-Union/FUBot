import asyncio
import logging
import os
from steam import SteamQuery

async def get_server_info():
    try:
        server_query = SteamQuery(os.getenv("ARMA_HOST"), int(os.getenv("ARMA_QUERY_PORT")))
        response = server_query.query_server_info()
        player_count: int = response.get("players")
        description = response.get("description")
        return f"**Current player count**: {player_count}\n**Mission/Status**: {description}"
    except Exception as ex:
        logging.exception(f"Failed to get Arma server info: {ex}")
        return f"Failed to get server info, maybe it's offline?"

