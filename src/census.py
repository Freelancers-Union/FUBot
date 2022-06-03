import auraxium
import asyncio
from auraxium import ps2

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError as err:
    """
    This is an expected error when not running locally using dotenv
    """
    logging.exception(err)

async def getChar(charname):
    async with auraxium.Client(service_id=os.getenv('CENSUS_TOKEN')) as client:
        
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
    async with auraxium.Client(service_id=os.getenv('CENSUS_TOKEN')) as client:
        
        outfit = await client.get(ps2.Outfit, name_lower=outfitTag)
        print(await outfit.members())
        return outfit

