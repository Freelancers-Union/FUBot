import os
import re
import logging
import flatdict
import auraxium
import disnake
from disnake.ext import commands
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
            service_id=os.getenv("CENSUS_TOKEN"), no_ssl_certs=True
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
            service_id=os.getenv("CENSUS_TOKEN"), no_ssl_certs=True
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
                    "$or": [
                        {"ps2_char1.name": str(ps2_char.name)},
                        {"ps2_char2.name": str(ps2_char.name)},
                        {"ps2_char3.name": str(ps2_char.name)},
                        {"ps2_char4.name": str(ps2_char.name)},
                        {"ps2_char5.name": str(ps2_char.name)},
                        {"ps2_char6.name": str(ps2_char.name)},
                        {"ps2_char7.name": str(ps2_char.name)},
                    ]
                },
            )
        except Exception as e:
            raise e
        else:
            if ps2_record is None:
                return False
            else:
                db_dict = flatdict.FlatDict(ps2_record, delimiter=".")
                if str(ps2_char.name) in db_dict.values():
                    return True

    @commands.slash_command()
    async def link_planetside_account(
            self, inter: disnake.ApplicationCommandInteraction,
            account_name: str
    ):
        """
        Links your Planetside account to FU

        Parameters
        ----------
        account_name: PS2 Character name to link.

        """
        await inter.response.defer(ephemeral=True)

        if not re.match(pattern="^[a-zA-Z0-9]*$", string=account_name):
            await inter.edit_original_message("Did you know that PlanetSide 2 character names are alphanumeric?")
            return

        # Check if this PS2 character exists, get the character object if it does.
        ps2_char = await self.ps2_get_char(account_name)
        if ps2_char is None:
            await inter.edit_original_message("Impossible. Perhaps the Archives are incomplete." +
                                              f"\n character {account_name} doesn't exist")
            return

        try:
            # Check if this PS2 character already claimed.
            ps2_db_check = await self.check_ps2_db(ps2_char)
            # If the account is already claimed, inform the user.
            if ps2_db_check is True:
                await inter.edit_original_message(
                    str(ps2_char.name) + " is already connected to another FU member!" +
                    "\nIf this is an issue, contact an Officer"
                )
                raise NameError
        except NameError:
            del self
            return
        except Exception as e:
            await inter.edit_original_message(
                "Timed out talking to Database. Try again later"
            )
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
                "Link timed out!\nYou must log in within 2 minutes."
            )
            del self.login_checks[account_name]
        else:
            if account_linked is True:
                # Feedback to user that a login was detected
                await inter.edit_original_message(
                    "**"
                    + str(self.login_checks[account_name].characters[0].name)
                    + "** Log in detected!"
                )
                try:
                    # Link the discord user and PS2 char in the db
                    await add_to_db(ps2_char, inter.author)
                except Exception as e:
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

    # Add PS2 attrs to an object
    ps2_obj = {}
    ps2_attrs = ["id", "name"]
    for count, ele in enumerate(ps2_attrs):
        ps2_obj[ele] = str(getattr(ps2_char, ele))

    # If the ps2_char is in an outfit, add those details
    if await ps2_char.outfit_member() is not None:
        ps2_outfit = await ps2_char.outfit_member()
        ps2_outfit_obj = {}
        outfit = await ps2_outfit.outfit()
        ps2_outfit_obj["outfit_name"] = outfit.name
        ps2_outfit_obj["outfit_alias"] = outfit.alias
        ps2_outfit_obj["outfit_rank"] = ps2_outfit.rank
        ps2_outfit_obj["joined_outfit"] = ps2_outfit.member_since_date
        ps2_obj["outfit"] = ps2_outfit_obj

    try:
        # find member record to append to
        query = {"discord_user.id": str(author.id)}
        existing_record = Database.find_one("members", query)
        alt_count = 0
        for i in existing_record.keys():
            if i.startswith("ps2_char"):
                alt_count += 1
        if alt_count == 0:
            char = "ps2_char1"
        else:
            char = "ps2_char" + str(alt_count + 1)
        new_values = {"$set": {str(char): ps2_obj}}

        Database.update_one("members", query, new_values)
    except Exception as e:
        print("summits fucked ay")
        raise e
    else:
        return


def setup(bot: commands.Bot):
    bot.add_cog(InitiateDiscordPs2Link(bot))
