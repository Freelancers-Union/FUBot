import os
import aiohttp
import logging
import requests
import auraxium
from auraxium import ps2, Client

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
    async def get_online_outfit_members(outfit: ps2.Outfit):
        """
        Get a list of online members of an outfit

        Parameters
        ----------
        outfit: outfit to get online members of

        Returns
        -------
        list of online members
        """
        url = f"https://census.daybreakgames.com/{os.getenv('CENSUS_TOKEN')}/get/ps2/outfit?alias_lower={outfit.alias_lower}&c:show=name,outfit_id&c:join=outfit_member^inject_at:members^show:character_id%27rank^outer:0^list:1(character^show:name.first^inject_at:character^outer:0^on:character_id(characters_online_status^inject_at:online_status^show:online_status^outer:0(world^on:online_status^to:world_id^outer:0^show:world_id^inject_at:ignore_this))"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
            
            online_members = []
            for member in data['outfit_list'][0]['members']:
                if member['character']['online_status'] != 0:
                    online_members.append(member['character_id'])
        except Exception as e:
            raise e
            return None
        return online_members

    @staticmethod
    async def get_outfit(outfit_name: str = None, outfit_tag: str = None):
        outfit = None
        try:
            if outfit_tag is not None:
                logging.info(f"looking up PS2 Outfit details for: {outfit_tag}")
                outfit = await Census.CLIENT.get(ps2.Outfit, alias_lower = outfit_tag.lower())
            elif outfit_name is not None:
                logging.info(f"looking up PS2 Outfit details for: {outfit_name}")
                outfit = await Census.CLIENT.get(ps2.Outfit, name_lower = outfit_name.lower())
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
        character = None
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
            return None
        except Exception as e:
            raise e
            return None
