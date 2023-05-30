import os
from typing import Type
from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient


def get_mongo_uri():
    port: str = ":" + str(os.getenv("MONGO_PORT")) if os.getenv("MONGO_PORT") else ""
    uri = (
            "mongodb://"
            + str(os.getenv('MONGO_USERNAME'))
            + ":"
            + str(os.getenv('MONGO_PASSWORD'))
            + "@" + str(os.getenv('MONGO_ADDRESS'))
            + port + "/"
    )
    return uri


def get_all_documents() -> list[Type[Document]]:
    """Returns a list of all MongoDB document models defined."""
    from .models.arma import OnlineFUArmaPlayers
    from .models.members import Member
    from .models.planetside2 import Ps2Character, OnlineOutfitMemberTS
    from database.models.discord import DiscordGuildTS

    documents = [OnlineFUArmaPlayers, Member, Ps2Character, OnlineOutfitMemberTS, DiscordGuildTS]
    return documents


async def init_database(mongo_uri: str, db_name: str):
    """
    Initializes the database connection and registers all document models.
    If needed creates basic data in the database.

    Parameters
    ----------
    mongo_uri :
        The URI to connect to the MongoDB database.
    db_name:
        The name of the database to connect to.
    """
    db_list = get_all_documents()
    client = AsyncIOMotorClient(str(mongo_uri))
    await init_beanie(
        database=getattr(client, db_name),
        document_models=db_list,
        allow_index_dropping=True
    )
    return
    # This is the place we can add some default data to the database if needed
