import os
import asyncio
import disnake
from disnake.ext import commands
import auraxium
from auraxium import event, ps2


async def PlayerLogin():

    client = auraxium.event.EventClient(
        service_id=os.getenv("CENSUS_TOKEN"), no_ssl_certs=True)

    @client.trigger(event.PlayerLogin)
    async def print_login(evt: event.PlayerLogin):
        char = await client.get_by_id(ps2.Character, evt.character_id)

        # Brand new characters may not be available in the API yet
        if char is None:
            print('Skipping anonymous player')
            return
        
        print(f'{await char.outfit()} has logged in!')

    _ = print_login

if __name__ == '__PlayerLogin__':
    loop = asyncio.get_event_loop()
    loop.create_task(PlayerLogin())
    loop.run_forever()