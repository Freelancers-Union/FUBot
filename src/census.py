import auraxium
import asyncio
from auraxium import ps2

async def getChar(charname):
    async with auraxium.Client(service_id="s:fuofficers") as client:
        
        char = await client.get_by_name(ps2.Character, charname)  
        if char is not None:
            outfit = await client.get_by_id(ps2.OutfitMember, char.character_id)
            if outfit is not None:
                return char, outfit
            else:
                return char, None
        else:
            return None, None
        

async def getOutfit(outfitname):
    async with auraxium.Client(service_id="fuofficers") as client:
        
        outfit = await client.get_by_name(ps2.OutfitMember, char.id)
        return outfit

