import auraxium
import asyncio
from auraxium import ps2

async def getChar(charname):
    async with auraxium.Client(service_id="s:fuofficers") as client:
        
        char = await client.get_by_name(ps2.Character, charname)  
        if char is not None:
            outfit = await client.get_by_id(ps2.OutfitMember, char.character_id)
            if outfit is not None:
                #Returns for characters that exist and are in an outfit
                return char, outfit 
            else:
                #Returns for characters that exists but are not in an outfit
                return char, None 
        else:
            # Returns for characters that don't exist
            return None, None 
        

async def getOutfit(outfitTag):
    async with auraxium.Client(service_id="fuofficers") as client:
        
        outfit = await client.get(ps2.Outfit, name_lower=outfitTag)
        print(await outfit.members())
        return outfit

