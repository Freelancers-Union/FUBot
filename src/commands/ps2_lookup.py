import os
import logging
import aiohttp
import disnake
from disnake.ext import commands
import auraxium
from auraxium import ps2
from census import Census


class Ps2Lookup(commands.Cog):
    """
    Class cog for ps2 character lookup
    """
    faction_logo = [
        'https://census.daybreakgames.com/files/ps2/images/static/94.png',
        'https://census.daybreakgames.com/files/ps2/images/static/12.png',
        'https://census.daybreakgames.com/files/ps2/images/static/18.png',
        'https://wiki.planetside-universe.com/ps/images/3/3d/Logo_ns.png'
    ]
    faction_color = [0x440E62, 0x004B80, 0x9E0B0F, 0x5B5B5B]
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.census_client = auraxium.Client(service_id=str(os.getenv("CENSUS_TOKEN")))

    @commands.slash_command(dm_permission=True)
    async def planetside(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        pass

    @planetside.sub_command_group()
    async def lookup(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        pass

    @lookup.sub_command()
    async def player(
            self,
            inter: disnake.ApplicationCommandInteraction,
            character_name: str,
            private: bool = False
    ):
        """
        Get information about a player

        Parameters
        ----------
        character_name: character name to search for
        private: whether to show the message as a private message (default: False)
        """
        await inter.response.defer(ephemeral=private)
        await inter.edit_original_message(f"Looking up {character_name}... :mag:")
        try:
            ps2_char = await Census.get_character(character_name = character_name)
            if ps2_char is not None:
                if ps2_char.outfit() is not None:
                    outfit = await ps2_char.outfit()
                    Message = await self.render_character_message(character=ps2_char, outfit=outfit)
                else:
                    Message = await self.render_character_message(character = ps2_char)
                await inter.edit_original_message(content = None, embed=Message)
            else:
                await inter.edit_original_message(content = None, embed = disnake.Embed(
                    title = "Character Not Found 😕",
                    description = f"Could not find {character_name}, please check spelling and try again."
                ))
        except auraxium.errors.CensusError as e:
            logging.error(e)
            await inter.edit_original_message("Census API Error. 😕")
        except auraxium.errors.MaintenanceError as e:
            logging.error(e)
            await inter.edit_original_message("Census API Maintenance. 😕")
        except auraxium.errors.AuraxiumException as e:
            logging.error(e)
            await inter.edit_original_message("Generic Error. 😕")
        except Exception as e:
            logging.error(e)
            await inter.edit_original_message("Generic Error. 😕")


    async def render_character_message(self,
    character,
    outfit = None
    ):
        Message = disnake.Embed(
            title="__" + str(character.name) + ":__",
            color=self.faction_color[character.faction_id - 1],
            description="[Click here for Fisu Stats](https://ps2.fisu.pw/player/?name=" + str(character.name) + ")",
        ).set_thumbnail(
            url=self.faction_logo[character.faction_id - 1]
        ).add_field(
            name="Last Seen",
            value=str(character.times.last_save_date)[:16],
            inline=True
        ).add_field(
            name="Battle Rank",
            value=str(character.battle_rank.value),
            inline=False
        ).add_field(
            name="ASP",
            value=str(character.data.prestige_level),
            inline=False
        ).add_field(
            name="Created",
            value=str(character.times.creation_date)[:16],
            inline=True
        ).add_field(
            name="Playtime",
            value=str(round(character.times.minutes_played / 60)) + " Hours",
            inline=True
        )
        if outfit is not None:
            outfit_details = await Census.get_outfit(outfit_name = str(outfit.name.lower()))
            outfit_member = await character.outfit_member()
            Message.add_field(
                name="Outfit",
                value="[[" + str(outfit_details.data.alias) + "]](https://ps2.fisu.pw/outfit/?name=" +
                      str(outfit_details.data.alias_lower) + ") " + str(outfit_details.name),
                inline=False
            )
            Message.add_field(
                name="Rank",
                value=str(outfit_member.rank),
                inline=True
            )
            Message.add_field(
                name="Joined",
                value=str(outfit_member.member_since_date)[:16],
                inline=True
            )
        return Message

    @lookup.sub_command()
    async def outfit(
            self,
            inter: disnake.ApplicationCommandInteraction,
            outfit_tag: str = None,
            outfit_name: str = None,
            private: bool = False
    ):
        """
        Get information about an outfit

        Parameters
        ----------
        outfit_name: outfit name to search for
        outfit_tag: outfit tag to search for
        private: whether to show the message as a private message (default: False)
        """
        await inter.response.defer(ephemeral=private)
        await inter.edit_original_message(f"Looking up Outfit... :mag:")
        try:
            outfit = await Census.get_outfit(outfit_name = outfit_name, outfit_tag = outfit_tag)
            if outfit is not None:
                Message = await self.render_outfit_message(outfit=outfit)
                await inter.edit_original_message(content = None, embed=Message)
            else:
                await inter.edit_original_message(content = None, embed = disnake.Embed(
                    title = "Outfit Not Found 😕",
                    description = f"Could not find that outfit, please check spelling and try again."
                ))  
        except auraxium.errors.CensusError as e:
            logging.error(e)
            await inter.edit_original_message("Census API Error. 😕")
        except auraxium.errors.MaintenanceError as e:
            logging.error(e)
            await inter.edit_original_message("Census API Maintenance. 😕")
        except auraxium.errors.AuraxiumException as e:
            logging.error(e)
            await inter.edit_original_message("Generic Error. 😕")
        except Exception as e:
            logging.error(e)
            await inter.edit_original_message("Generic Error. 😕")


    async def render_outfit_message(self,
    outfit: auraxium.ps2.Outfit,
    ):
        online_members = await Census.get_online_outfit_members(outfit = outfit)
        outfit_leader = await Census.get_character(character_id = outfit.leader_character_id)
        Message = disnake.Embed(
            title="__[" + outfit.alias + "] " + str(outfit.name) + ":__",
            color=self.faction_color[outfit_leader.faction_id - 1],
            description="[Click here for Fisu Stats](https://ps2.fisu.pw/outfit/?name=" + str(outfit.alias_lower) + ")"
        ).add_field(
            name="Faction",
            value=str(await self.census_client.get_by_id(ps2.Faction, outfit_leader.faction_id)),
            inline=True
        ).add_field(
            name="Leader",
            value=str(outfit_leader.name),
            inline=False
        ).add_field(
            name="Members",
            value=str(outfit.member_count),
            inline=True
        ).add_field(
            name="Online",
            value=str(str(len(online_members))),
            inline=True
        ).add_field(
            name="Founded",
            value=str(outfit.time_created_date)[:10],
            inline=False
        )

        return Message

def setup(bot: commands.Bot):
    bot.add_cog(Ps2Lookup(bot))