import disnake
import logging
logging.basicConfig(level=logging.INFO)
import requests
import auraxium
from auraxium import ps2
from disnake.ext import commands
import os
import census
#from census import getChar


#discordClientToken = os.getenv('discordClientToken')
discordClientToken = ""


intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
Botdescription = "The serious bot for the casual Discord."

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("?"), 
    description=Botdescription, 
    intents=intents, 
    test_guilds=[914185528268689428],
    sync_commands_debug=False
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("The bot is ready!")
    print("------")

@bot.slash_command()
async def ping(inter):
    await inter.response.send_message("Pong!")

@bot.command()
async def repeat(ctx, times: int, content="repeating..."):
    """Repeats a message multiple times. [repeat # message]"""
    for i in range(times):
        await ctx.send(content)

@bot.command()
async def whoami(ctx):
    """Helps you with those existential crises you keep having"""
    await ctx.send(ctx.author)

@bot.slash_command()
async def playercard(inter, charactername):
    """Get character information for a given character"""

    await inter.response.send_message("Getting player stats for "+charactername+" ...")

    char, outfit = await census.getChar(charactername)
    if char is None:
        await inter.edit_original_message("Player "+charactername+" cannot be found.")
        raise ValueError("Player could not be found.", charactername)

    async with auraxium.Client(service_id="s:fuofficers") as client:

        faction = await client.get_by_id(auraxium.ps2.Faction, char.faction_id)
        Message = disnake.Embed(
            title="__Player Card for "+str(char.name)+":__",
            color=3166138,
            description="[Fisu Stats](https://ps2.fisu.pw/player/?name="+str(char.name)+")\n\n \
            **Faction:** "+str(faction)+"\n \
            **Battle rank:** "+str(char.battle_rank.value)+"\n \
            **ASP level:** "+str(char.data.prestige_level)+"\n \
            **Played since:** "+str(char.times.creation_date)[:16]+"\n \
            **Last online:** "+str(char.times.last_save_date)[:16]+"\n \
            **Playtime:** "+str(round(char.times.minutes_played/60))+" Hours\n \
",
        )
        if outfit is not None:
            outfitName = await client.get_by_id(auraxium.ps2.Outfit, outfit.outfit_id)
            Message.add_field(
                name="Outfit",
                value="**"+str(outfitName)+"**\n \
                    **Rank:** "+str(outfit.rank)+"\n \
                    **Joined:** "+str(outfit.member_since_date)[:16]+" ",
                inline=True
            )

    try:
        await inter.edit_original_message(" ",embed=Message)
        #result = requests.post(discord_webhook_url, json=Message)
    except requests.exceptions.HTTPError as err:
        logging.exception(err)
        await inter.edit_original_message('Oops! Something went wrong.')

    logging.info("Playercard for "+charactername+" delivered successfully.")


bot.run(discordClientToken)