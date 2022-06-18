import os
import logging
import requests
from auraxium import ps2

logging.basicConfig(level=logging.os.getenv('LOGLEVEL'),format='%(asctime)s %(funcName)s: %(message)s ' , datefmt='%m/%d/%Y %I:%M:%S %p')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError as err:
    """
    This is an expected error when not running locally using dotenv
    """
    logging.warning(err)


async def getChar(charname, client):
    """
    Char object is array with elements:
    [0] ps2.Character(class)
    [1] online_status(int)
    """
    char=[]
    char.insert(0, await client.get_by_name(ps2.Character, charname))
    if char[0] is not None:
        char.insert(1, await char[0].online_status())
        outfit = await client.get_by_id(ps2.OutfitMember, char[0].character_id)
        return char, outfit 
    else:
        return None, None


async def getOutfit(outfitTag, outfitName, client):
    """
    outfit object is array with elements:
    [0] ps2.Outfit(class)
    [1] online_members(int)
    """
    outfit = []
    try:
        if outfitTag is not 0:
            outfit.insert(0, await client.get(ps2.Outfit, alias_lower=outfitTag.lower()))
        elif outfitName is not 0:
            outfit.insert(0, await client.get(ps2.Outfit, name_lower=outfitName.lower()))
        if outfit[0] is not None:
            online_members = await get_online_outfit(outfit[0].id)
            outfit.insert(1, online_members)
            return outfit
        else:
            return None
    except AttributeError as err:
        logging.exception(err)
        return None


async def get_online_outfit(outfit):
    """Return the online friends of the given character."""
    try:
        url="https://census.daybreakgames.com/"+str(os.getenv('CENSUS_TOKEN'))+"/get/ps2:v2/outfit?outfit_id="+str(outfit)+"&c:resolve=member_character&c:join=characters_online_status%5Eon:members.character_id%5Eto:character_id%5Einject_at:character_online_status"
        response=requests.get(url)
        member_count=len(response.json()['outfit_list'][0]['members'])
        count = 0
        for i in range(member_count):
            if response.json()['outfit_list'][0]['members'][i]['character_online_status']['online_status'] is not "0":
                count +=1
        return count
    except httperror as err:
        logging.exception(err)
        return 0
