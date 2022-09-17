import os
import datetime
import asyncio
import disnake
from disnake.ext import commands
import auraxium
from auraxium import event, ps2
from bson.dbref import DBRef
from database_connector import Database


async def update_event_db(char, evt, indicator, client):
    print(char)
    char_outfit = await char.outfit()
    outfit = await client.get_by_id(ps2.Outfit, char_outfit.id)
    if outfit is not None:

        outfit_members = await outfit.members()
        outfit_member_ids =[]
        for i in outfit_members:
            outfit_member_ids.append(i.id)
        print(outfit_member_ids)
        outfit_online = await auraxium.ps2.Character.get_online(5428010618031001329, 5428010618034874593, 5428010618035201345, client=client)

        if indicator == 1:
            state = "player_logged_in"
        elif indicator == 2:
            state = "player_logged_out"
        ref=DBRef(collection='Planetside Characters',id=int(char.id))
        data = {
            "metadata": {
                "event": state,
                "character_id": int(char.id),
            },
            "timestamp": evt.timestamp,
            "outfit_online": len(outfit_online),
        }
        Database.insert_one("Planetside Event Stream", data)


async def insert_character_db(char):

    data = {
        "_id": int(char.id),
        "name": char.name,
        "created": char.created_at,
        "last_joined_fu": char.outfit.joined_at,
    }
    Database.insert_one("Planetside Characters", data)

async def add_all_outfit():
    client = auraxium.event.EventClient(
        service_id=os.getenv("CENSUS_TOKEN"), no_ssl_certs=True
    )
    outfit = await client.get(ps2.Outfit, alias_lower="fu")
    outfit_members = await outfit.members()
    data = []
    for i in outfit_members:
        char = await i.character()
        created = datetime.datetime.fromtimestamp(char.times.creation).isoformat()
        joined = datetime.datetime.fromtimestamp(i.member_since).isoformat()
        obj = {}
        obj["_id"]=char.id
        obj["name"]=char.name.first_lower
        obj["created"]=created
        obj["last_joined_fu"]=joined
        data.append(obj)
    print(len(data))
    print(data[1])
    Database.insert_many("Planetside Characters", data)



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
            print("FUUUU!")
            asyncio.create_task(update_event_db(char, evt, 1, client))

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
            asyncio.create_task(update_event_db(char, evt, 2, client))

    _ = print_logout


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(PlayerLogin())
    loop.create_task(PlayerLogout())
    loop.run_forever()
