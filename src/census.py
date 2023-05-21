import asyncio
import os
import logging
from ctypes import Union

import aiohttp
import requests
import auraxium
from auraxium import ps2, Client

# from models.ps2.outfit_with_member_characters import OutfitMemberList
from models.ps2.outfit_with_member_characters import Ps2OutfitMember


class Census(object):
    """
    Class to handle all census requests
    
    Attributes
    ----------
    CLIENT: auraxium Client
        Client to make requests with
    
    Methods
    -------
    get_online_outfit_members(outfit: ps2.Outfit) -> list[ps2.Character]
        Get a list of online members of an outfit
    
    get_outfit(outfit_tag: str, outfit_name: str) -> ps2.Outfit
        Get an outfit by tag or name
    
    get_character(character_name: str, character_id: int) -> ps2.Character
        Get a character by name or ID

    """

    CLIENT = Client(service_id=str(os.getenv("CENSUS_TOKEN")))

    @staticmethod
    def get_client():
        return Census.CLIENT

    @staticmethod
    async def get_online_outfit_members(outfit: ps2.Outfit) -> list[ps2.Character]:
        """
        Get a list of online members of an outfit

        Parameters
        ----------
        outfit: outfit to get online members of

        Returns
        -------
        list of online members
        """
        try:
            member_ids = []
            for member in await outfit.members():
                member_ids.append(member.character_id)
            online_members = await auraxium.ps2.Character.get_online(*member_ids, client=Census.CLIENT)
        except IndexError as e:
            raise e
        except Exception as e:
            raise e

        return online_members

    @staticmethod
    async def get_outfit(outfit_name: str = None, outfit_tag: str = None, synchro: bool = False):
        outfit = None
        try:
            if outfit_tag is not None:
                if synchro is False:
                    logging.info(f"looking up PS2 Outfit details for: {outfit_tag}")
                outfit = await Census.CLIENT.get(ps2.Outfit, alias_lower=outfit_tag.lower())
            elif outfit_name is not None:
                if synchro is False:
                    logging.info(f"looking up PS2 Outfit details for: {outfit_name}")
                outfit = await Census.CLIENT.get(ps2.Outfit, name_lower=outfit_name.lower())
            else:
                return None
            if outfit is not None:
                return outfit
        except auraxium.errors.CensusError as e:
            raise e
            return None
        except Exception as e:
            raise e
            return None

    @staticmethod
    async def get_character(character_name: str = None, character_id: int = None):
        """
        Get a character by name or ID

        Parameters
        ----------
        character_name: name of character to get
        character_id: ID of character to get

        Returns
        -------
        character object
        """
        try:
            if character_name is not None:
                character = await Census.CLIENT.get_by_name(auraxium.ps2.Character, character_name)
                return character
            elif character_id is not None:
                character = await Census.CLIENT.get_by_id(ps2.Character, character_id)
                return character
            else:
                return None
        except auraxium.errors.CensusError as e:
            raise e
        except Exception as e:
            raise e

    @staticmethod
    async def get_outfit_with_member_characters(outfit_id: int) -> list[Ps2OutfitMember]:
        member_list_query = auraxium.census.Query(collection="outfit_member", service_id=Census.CLIENT.service_id)

        member_list_query = member_list_query.add_term(
            field="outfit_id",
            value=outfit_id
        ).resolve("outfit_rank").resolve("character").limit(6000)

        async with aiohttp.ClientSession() as session:
            async with session.get(member_list_query.url(), allow_redirects=False) as resp:
                response = await resp.json()
                return [Ps2OutfitMember(member) for member in response["outfit_member_list"]]

# todo: delete this
# async def main():
#     FU_id = 37509488620602936
#     nFUc_id = 37558455247570544
#     vFUs_id = 37558804429669935
#     SNGE_id = 37516191867639142
#
#     a = await Census.get_outfit_with_member_characters(SNGE_id)
#     print(a)
#
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
