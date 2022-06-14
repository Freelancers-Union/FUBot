import os
import disnake
import auraxium
from auraxium import ps2
import census


async def get_outfit(tag, name):
    async with auraxium.Client(service_id=str(os.getenv('CENSUS_TOKEN'))) as client:
        outfit = await census.get_outfit(tag, name, client)
        if outfit is None:
            return None

        faction_color = [0x440E62, 0x004B80, 0x9E0B0F, 0x5B5B5B]

        outfit_leader = await client.get_by_id(auraxium.ps2.Character, outfit[0].leader_character_id)
        faction_id = outfit_leader.faction_id
        Message = disnake.Embed(
            title="__[" + outfit[0].alias + "] " + str(outfit[0].name) + ":__",
            color=faction_color[faction_id - 1],
            description="[Click here for Fisu Stats](https://ps2.fisu.pw/outfit/?name=" + str(outfit[0].alias_lower) + ")"
        )
        Message.add_field(
            name="Faction",
            value=str(await client.get_by_id(ps2.Faction, outfit_leader.faction_id)),
            inline=True
        )
        Message.add_field(
            name="Leader",
            value=str(outfit_leader.name),
            inline=False
        )
        Message.add_field(
            name="Members",
            value=str(outfit[0].member_count),
            inline=True
        )
        Message.add_field(
            name="Online",
            value=str(outfit[1]),
            inline=True
        )
        Message.add_field(
            name="Founded",
            value=str(outfit[0].time_created_date)[:10],
            inline=False
        )
    return Message
