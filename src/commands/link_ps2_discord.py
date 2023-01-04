import os
import re
import logging
import datetime
import flatdict
import auraxium
import disnake
from disnake.ext import commands
from bson.objectid import ObjectId
from bson.dbref import DBRef
import census
from database_connector import Database


class LinkPs2(commands.Cog):
    """

    Class cog for linking PS2 and Discord accounts.

    """

    def __init__(self, bot: commands.Bot, ps2_char):
        """
        Parameters
        ----------
        bot : commands.Bot
            Discord Bot class
        client : auraxium.event.EventClient
            The Auraxium Event client
        census_client : auraxium.Client
            The Auraxium census Client
        account_name : str
            The name of the PS2 account to associate
        """

        self.bot = bot
        self.client = auraxium.event.EventClient(
            service_id=os.getenv("CENSUS_TOKEN")
        )
        self.characters = [None]
        self.characters[0] = ps2_char
        self.login_trigger = None

    def create_trigger(self):
        self.login_trigger = auraxium.Trigger(
            auraxium.event.PlayerLogin,
            characters=self.characters,
            single_shot=True,
            name=str(self.characters[0].name),
        )
        self.client.add_trigger(self.login_trigger)
        return self.login_trigger

    async def login_check(self):
        try:
            get_login_trigger = self.client.get_trigger(
                name=str(self.characters[0].name)
            )
            linked_account = await self.client.wait_for(
                trigger=get_login_trigger, timeout=120
            )
        except TimeoutError:
            self.client.remove_trigger(str(self.characters[0].name))
            raise
        else:
            if linked_account.character_id == self.characters[0].id:
                return True
            else:
                return None


class InitiateDiscordPs2Link(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.login_checks = {}
        self.client = auraxium.event.EventClient(
            service_id=os.getenv("CENSUS_TOKEN")
        )
        self.census_client = auraxium.Client(service_id=str(os.getenv("CENSUS_TOKEN")))

    async def ps2_get_char(self, account_name):
        """Queries the PS2 Census API and checks if a character exists.

        Parameters
        ----------
        account_name : str
            The name of the PS2 character to check.

        Returns
        ------
        characters : list(ps2.Character)
            list of matching characters.
        """
        character, *unused_tuple = await census.get_character(
            account_name, self.census_client
        )
        return character

    async def check_ps2_db(self, ps2_char):
        """Queries the mongoDB for existing ps2_char.

        Parameters
        ----------
        ps2_char : class auraxium.ps2.Character
            The PS2 character to check.

        Returns
        ------
        characters : bool
            True if the character exists in the db.
        """
        try:
            ps2_record = Database.find_one(
                "members",
                {
                    "ps2_characters.$id": { '$in': [ ps2_char.id ] },
                }
            )
        except Exception as e:
            raise e

        if ps2_record is None:
            return False, None

        member_id = ps2_record["discord_user"]["id"]
        return True, member_id

    @commands.slash_command(dm_permission=True)
    async def ps2(
        self,
        inter: disnake.ApplicationCommandInteraction
    ):
        pass

    @ps2.sub_command_group()
    async def link(
        self,
        inter: disnake.ApplicationCommandInteraction
    ):
        pass

    @link.sub_command()
    async def account(
            self,
            inter: disnake.ApplicationCommandInteraction,
            account_name: str
    ):
        """
        Link your Planetside account to FU for cool stats and stuff!

        Parameters
        ----------
        account_name: PS2 Character name to link.

        """
        await inter.response.defer(ephemeral=True)

        if not re.match(pattern="^[a-zA-Z0-9]*$", string=account_name):
            await inter.edit_original_message("PlanetSide 2 character names are alphanumeric, are you sure you spelt that right?")
            return

        # Check if this PS2 character exists, get the character object if it does.
        ps2_char = await self.ps2_get_char(account_name)
        if ps2_char is None:
            await inter.edit_original_message("Impossible. Perhaps the Archives are incomplete." +
                                              f"\n character {account_name} doesn't exist")
            return

        try:
            # Check if this PS2 character already claimed.
            ps2_db_check, member_id = await self.check_ps2_db(ps2_char)
            # If the account is already claimed, inform the user.
            if ps2_db_check is True:
                if str(member_id) == str(inter.author.id):
                    await inter.edit_original_message(
                        str(ps2_char.name) + " is already connected to your account!"
                    )
                    raise NameError
                else:
                    await inter.edit_original_message(
                        str(ps2_char.name) + " is already connected to another FU member!" +
                        "\nIf this is an issue, contact the Bot Devs `@BotDevs`"
                    )
                    raise NameError
        except NameError:
            del self
            return
        except Exception as e:
            await inter.edit_original_message(
                "Timed out talking to Database. Try again later"
            )
            logging.error("Failed to connect to database", exc_info=e)
            del self
            return

        # Instantiate a new LinkPs2 class and store it in a list.
        self.login_checks.update({account_name: LinkPs2(self.bot, ps2_char)})

        # use that class instance to watch for login events
        self.login_checks[account_name].create_trigger()
        try:
            await inter.edit_original_message(
                "Please log in to `"
                + str(self.login_checks[account_name].characters[0].name)
                + "` within the next 2 minutes."
                + "\nIf you are already logged in, please log out and back in again.\n"
            )
            account_linked = await self.login_checks[account_name].login_check()
        except TimeoutError:
            await inter.edit_original_message(
                "Link timed out!\nYou must log in within 2 minutes.\nPlease try again."
            )
            del self.login_checks[account_name]
        else:
            if account_linked is True:
                # Feedback to user that a login was detected
                await inter.edit_original_message(
                    "**"
                    + str(self.login_checks[account_name].characters[0].name)
                    + "** Log in detected!\nNow linking accounts..."
                )
                try:
                    # Link the discord user and PS2 char in the db
                    await add_to_db(ps2_char, inter.author)
                except Exception as e:
                    logging.error("Failed to add to the database", exc_info=e)
                    await inter.edit_original_message(
                        "Looks like something went wrong talking to the Database"
                    )
                    return
                else:
                    await inter.edit_original_message(
                        "You've successfully connected accounts! :tada:\nPS2: **"
                        + str(self.login_checks[account_name].characters[0].name)
                        + "**\nDiscord: **"
                        + str(inter.author.name)
                        + "**"
                    )

                    del self.login_checks[account_name]
            elif account_linked is None:
                await inter.edit_original_message("Something went wrong!:cry:")
                del self.login_checks[account_name]
                return


async def add_to_db(ps2_char, author):
    """
    Inserts new Documents or updates existing ones in the MongoDB

    Parameters
    ----------
    ps2_char : class auraxium.ps2.Character
        The character being attached.

    author : class interaction.author
        The discord Member class of the user

    """

    # Check if the character is in a tracked outfit
    FU_id = 37509488620602936
    nFUc_id = 37558455247570544
    vFUs_id = 37558804429669935
    tracked_outfits = [FU_id, nFUc_id, vFUs_id]
    if await ps2_char.outfit() is not None:
        outfit = await ps2_char.outfit()
        if outfit.id not in tracked_outfits:
            pass
        else:
            # Reference the character in the outfit collection to the member object
            char_reference = DBRef(f"ps2_outfit_members_{str(outfit.alias)}",
                                ps2_char.id
            )
            try:
                Database.update_one("members", {"discord_user.id": str(author.id)}, {
                    '$push': {'ps2_characters': char_reference}
                })
                return
            except Exception as e:
                logging.error("Failed to update database", exc_info=e)

    # Create a new document for the member
    ps2_player_object = {}
    ps2_player_object["_id"] = ps2_char.id
    ps2_player_object["name"] = str(ps2_char.name)
    ps2_player_object["active_member"] = True
    outfit_object = await ps2_char.outfit_member()
    if outfit_object is not None:
        rank = {
            "rank": outfit_object.rank,
            "time": datetime.datetime.utcnow()
        }
        ps2_player_object["outfit_id"] = outfit_object.id
        ps2_player_object["member_since"] = datetime.datetime.fromtimestamp(outfit_object.member_since)
        ps2_player_object["rank_history"] = [rank]
    try:
        Database.insert_one("ps2_other_characters", ps2_player_object)
        char_reference = DBRef("ps2_other_characters",
                                ps2_char.id
            )
        Database.update_one("members", {"discord_user.id": str(author.id)}, {
            '$push': {'ps2_characters': char_reference}
        })
    except Exception as e:
        raise e

def setup(bot: commands.Bot):
    bot.add_cog(InitiateDiscordPs2Link(bot))
