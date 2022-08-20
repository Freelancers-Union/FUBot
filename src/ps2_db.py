import os
import datetime
import asyncio
import disnake
from disnake.ext import commands
import auraxium
from auraxium import event, ps2
from database_connector import Database
import census


async def update_db(char, evt, indicator, client):
    outfit, online_count = await census.get_outfit(
        None, str(await char.outfit()), client
    )
    if outfit is not None:
        if indicator == 1:
            state = "player_logged_in"
        elif indicator == 2:
            state = "player_logged_out"

        total_members = {
            "metadata": {state: char.id},
            "timestamp": evt.timestamp,
            "online": online_count,
        }
        Database.insert_one("FU Outfit Members", total_members)


async def PlayerLogin():

    client = auraxium.event.EventClient(
        service_id=os.getenv("CENSUS_TOKEN"), no_ssl_certs=True
    )

    @client.trigger(event.PlayerLogin, worlds=[10])
    async def print_login(evt: event.PlayerLogin):
        char = await client.get_by_id(ps2.Character, evt.character_id)
        # Brand new characters may not be available in the API yet
        if char is None:
            return
        if str(await char.outfit()) == "Freelancers Union":
            asyncio.create_task(update_db(char, evt, 1, client))

    _ = print_login


async def PlayerLogout():

    client = auraxium.event.EventClient(
        service_id=os.getenv("CENSUS_TOKEN"), no_ssl_certs=True
    )

    @client.trigger(event.PlayerLogout, worlds=[10])
    async def print_logout(evt: event.PlayerLogout):
        char = await client.get_by_id(ps2.Character, evt.character_id)
        # Brand new characters may not be available in the API yet
        if char is None:
            return
        if str(await char.outfit()) == "Freelancers Union":
            asyncio.create_task(update_db(char, evt, 2, client))

    _ = print_logout


if __name__ == "__PlayerLogin__":
    loop = asyncio.get_event_loop()
    loop.create_task(PlayerLogin())
    loop.run_forever()

if __name__ == "__PlayerLogout__":
    loop = asyncio.get_event_loop()
    loop.create_task(PlayerLogout())
    loop.run_forever()
