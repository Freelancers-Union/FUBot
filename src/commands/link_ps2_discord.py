import os
import logging
import json
from pprint import pprint
import auraxium
from auraxium import event, ps2
import asyncio
import disnake
from disnake.ext import commands
import census
import database_connector


logging.basicConfig(level=logging.os.getenv('LOGLEVEL'), format='%(asctime)s %(funcName)s: %(message)s ',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


class LinkPs2(commands.Cog):
    """
    Class cog for linking PS2 and Discord
    """

    def __init__(self, bot: commands.Bot, account_name):
        self.bot = bot
        self.client = auraxium.event.EventClient(service_id=os.getenv('CENSUS_TOKEN'), no_ssl_certs=True)
        self.census_client = auraxium.Client(service_id=str(os.getenv('CENSUS_TOKEN')))
        self.account_name = account_name
        self.characters = [None]

    async def get_characters(self):
        character, current_world, outfit = await census.get_character(self.account_name, self.census_client)
        self.characters[0] = character
        return self.characters

    def create_trigger(self):
        self.login_trigger = auraxium.Trigger(
        auraxium.event.PlayerLogin,
        characters=self.characters,
        single_shot=True,
        name=str(self.characters[0].name)
        )
        self.client.add_trigger(self.login_trigger)
        return self.login_trigger

        @self.login_trigger.callback
        async def get_login(evt: event.PlayerLogin):
            char = await self.client.get_by_id(ps2.Character, evt.character_id)
            if str(char.name).lower() == str(self.characters[0].name).lower():
                return char

    async def run_login_check(self):
        try:
            get_login_trigger = self.client.get_trigger(name=str(self.characters[0].name))
            linked_account = await self.client.wait_for(trigger=get_login_trigger, timeout=120)
        except TimeoutError:
            self.client.remove_trigger(str(self.characters[0].name))
            raise
        else:
            if linked_account.character_id == self.characters[0].id:
                return linked_account
            else:
                return None


class LinkPs2Discord(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.login_checks = {}
        self.client = auraxium.event.EventClient(service_id=os.getenv('CENSUS_TOKEN'), no_ssl_certs=True)

    @commands.slash_command()
    async def link_planetside_account(
            self,
            inter: disnake.ApplicationCommandInteraction,
            account_name
    ):
        """
        Links your Planetside account to FU

        Parameters
        ----------
        account_name: What account do you want to link?
        """
        await inter.response.defer(ephemeral=True)
        self.login_checks.update({account_name: LinkPs2(self.bot, account_name)})
        await self.login_checks[account_name].get_characters()
        self.login_checks[account_name].create_trigger()
        try:
            await inter.edit_original_message("Please log in to `" + str(self.login_checks[account_name].characters[0].name) +
            "` within the next 2 minutes.\nIf you are already logged in, please log out and back in again.\n"
)
            account_linked = await self.login_checks[account_name].run_login_check()
        except TimeoutError:
            await inter.edit_original_message("Link timed out!\nYou must log in within 2 minutes.")
            del self.login_checks[account_name]
        else:
            if account_linked is not None:
                await inter.edit_original_message("**" + str(self.login_checks[account_name].characters[0].name)
                + "** Log in detected!")
                char = await self.client.get_by_id(ps2.Character, account_linked.character_id)
                await add_to_db(char, inter.author)
                del self.login_checks[account_name]
            elif account_linked is None:
                await inter.edit_original_message("Something went wrong.")
                del self.login_checks[account_name]

async def add_to_db(ps2_char, author):
    # create a JSON object
    discord_obj = {}
    ps2_obj = {}
    
    discord_attrs = ["id", "name", "nick", "joined_at"]
    for count, ele in enumerate(discord_attrs):
        discord_obj[ele] = str(getattr(author, ele))

    ps2_attrs = ["id", "name"]
    for count, ele in enumerate(ps2_attrs):
        ps2_obj[ele] = str(getattr(ps2_char, ele))

    if await ps2_char.outfit_member() is not None:
        ps2_outfit = await ps2_char.outfit_member()
        ps2_outfit_obj = {}
        outfit = await ps2_outfit.outfit()
        ps2_outfit_obj["outfit_name"] = outfit.name
        ps2_outfit_obj["outfit_alias"] = outfit.alias
        ps2_outfit_obj["outfit_rank"] = ps2_outfit.rank
        ps2_outfit_obj["joined_outfit"] = ps2_outfit.member_since_date
        ps2_obj["outfit"]=ps2_outfit_obj

    member_obj = {}
    member_obj["ps2_char"] = ps2_obj
    member_obj["discord_user"] = discord_obj

    # Insert into member database
    mongodb = database_connector.get_database()
    mongodb.members.insert_one(member_obj)

def setup(bot: commands.Bot):
    bot.add_cog(LinkPs2Discord(bot))
