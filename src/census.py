import os
import logging
import requests
from auraxium import ps2, Client
from typing import Tuple


async def get_character(
    char_name: str, client: Client
) -> Tuple[ps2.Character, int, ps2.OutfitMember]:
    """
    Gets character, world it is in and its outfit
    Parameters
    ----------
    char_name:
        character name
    client:
        auraxium client

    Returns
    -------
    Tuple
         Character, Current status, outfit of player
    """
    character = await client.get_by_name(ps2.Character, char_name)
    current_world: int = 0
    outfit = None
    if character is not None:
        current_world = await character.online_status()
        outfit = await client.get_by_id(ps2.OutfitMember, character.character_id)
    return character, current_world, outfit


async def get_outfit(outfit_tag, outfit_name, client):
    """
    Parameters
    ----------
    outfit_tag: str
    outfit_name: str
    client

    Returns
    -------
    Tuple: Tuple[ps2.Outfit, int]
        Outfit, count of online players
    """
    # outfit = []
    outfit = None
    online_members = None
    try:
        if outfit_tag:
            outfit = await client.get(ps2.Outfit, alias_lower=outfit_tag.lower())
        elif outfit_name is not None:
            outfit = await client.get(ps2.Outfit, name_lower=outfit_name.lower())
        if outfit is not None:
            online_members = await get_online_outfit(outfit.id)
    except AttributeError as e:
        logging.exception(e)
    finally:
        return outfit, online_members


async def get_online_outfit(outfit) -> int:
    """
    Return the online players of the given outfit.

    Parameters
    ----------
    outfit: Outfit
        outfit which members to count

    Returns
    -------
    count: int
        count of online members
    """
    count = 0
    try:
        url = (
            "https://census.daybreakgames.com/"
            + str(os.getenv("CENSUS_TOKEN"))
            + "/get/ps2:v2/outfit?outfit_id="
            + str(outfit)
            + "&c:resolve=member_character&c:join=characters_online_status%5Eon:members.character_id%5Eto:character_id%5Einject_at:character_online_status"
        )
        response = requests.get(url)
        member_count = len(response.json()["outfit_list"][0]["members"])
        for i in range(member_count):
            if (
                response.json()["outfit_list"][0]["members"][i][
                    "character_online_status"
                ]["online_status"]
                != "0"
            ):
                count += 1
    except Exception as e:
        logging.exception(e)
    finally:
        return count
