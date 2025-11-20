# import os
# import re
# import logging
# from typing import Union

# import auraxium
# from auraxium import ps2
# import disnake
# from disnake.ext import commands
# from census import Census
# from database.models.members import Member
# from database.models.planetside2 import Ps2Character
# from beanie.operators import Push


# class LinkPs2(commands.Cog):
#     """

#     Class cog for linking PS2 and Discord accounts.

#     """

#     def __init__(self, bot: commands.Bot, ps2_char):
#         """
#         Parameters
#         ----------
#         bot : commands.Bot
#             Discord Bot class
#         client : auraxium.event.EventClient
#             The Auraxium Event client
#         account_name : str
#             The name of the PS2 account to associate
#         """

#         self.bot = bot
#         self.client = auraxium.event.EventClient(
#             service_id=os.getenv("CENSUS_TOKEN")
#         )
#         self.characters = [None]
#         self.characters[0] = ps2_char
#         self.login_trigger = None

#     def create_trigger(self):
#         """Creates a trigger for PS2 character logon events.

#         Returns
#         -------
#         login_trigger : auraxium.Trigger
#             The trigger for the PS2 character.
#         """
#         self.login_trigger = auraxium.Trigger(
#             auraxium.event.PlayerLogin,
#             characters=self.characters,
#             single_shot=True,
#             name=str(self.characters[0].name),
#         )
#         self.client.add_trigger(self.login_trigger)
#         return self.login_trigger

#     async def login_check(self):
#         """Checks if the PS2 character has logged in.

#         Returns
#         -------
#         bool
#             True if the character has logged in.
#         """
#         try:
#             get_login_trigger = self.client.get_trigger(
#                 name=str(self.characters[0].name)
#             )
#             linked_account = await self.client.wait_for(
#                 trigger=get_login_trigger, timeout=120
#             )
#         except TimeoutError:
#             self.client.remove_trigger(str(self.characters[0].name))
#             raise
#         else:
#             if linked_account.character_id == self.characters[0].id:
#                 return True
#             else:
#                 return None


# class InitiateDiscordPs2Link(commands.Cog):
#     """

#     Class cog for initiating the PS2 and Discord account linking process.

#     """

#     def __init__(self, bot: commands.Bot):
#         """
#         Parameters
#         ----------
#         bot : commands.Bot
#             Discord Bot class
#         """
#         self.bot = bot
#         self.login_checks = {}

#     @commands.slash_command(dm_permission=True)
#     async def ps2(
#             self,
#             inter: disnake.ApplicationCommandInteraction
#     ):
#         pass

#     @ps2.sub_command_group()
#     async def link(
#             self,
#             inter: disnake.ApplicationCommandInteraction
#     ):
#         pass

#     @link.sub_command()
#     async def account(
#             self,
#             inter: disnake.ApplicationCommandInteraction,
#             account_name: str
#     ):
#         """
#         Link your Planetside account to FU for cool stats and stuff!

#         Parameters
#         ----------
#         account_name: PS2 Character name to link.

#         """
#         await inter.response.defer(ephemeral=True)

#         if not re.match(pattern="^[a-zA-Z0-9]*$", string=account_name):
#             await inter.edit_original_message("PlanetSide 2 character names are alphanumeric, are you sure you spelt " +
#                                               "that right?")
#             return

#         # Check if this PS2 character exists, get the character object if it does.
#         ps2_char: ps2.Character = await Census.get_character(account_name)
#         if ps2_char is None:
#             await inter.edit_original_message("Impossible. Perhaps the Archives are incomplete." +
#                                               f"\n character {account_name} doesn't exist")
#             return

#         try:
#             # Check if this PS2 character already claimed.
#             member = await Member.find_one(Member.ps2_character_ids == ps2_char.id)
#             # If the account is already claimed, inform the user.
#             if member:
#                 if str(member.discord.id) == str(inter.author.id):
#                     await inter.edit_original_message(
#                         str(ps2_char.name.first) + " is already connected to your account!"
#                     )
#                     raise NameError
#                 else:
#                     await inter.edit_original_message(
#                         str(ps2_char.name.first) + " is already connected to another FU member!" +
#                         "\nIf this is an issue, contact the Bot Devs `@BotDevs`"
#                     )
#                     raise NameError
#         except NameError:
#             del self
#             return
#         except Exception as e:
#             await inter.edit_original_message(
#                 "Timed out talking to Database. Try again later"
#             )
#             logging.error("Failed to connect to database", exc_info=e)
#             del self
#             return

#         # Instantiate a new LinkPs2 class and store it in a list.
#         self.login_checks.update({account_name: LinkPs2(self.bot, ps2_char)})

#         # use that class instance to watch for login events
#         self.login_checks[account_name].create_trigger()
#         try:
#             await inter.edit_original_message(
#                 "Please log in to `"
#                 + str(self.login_checks[account_name].characters[0].name)
#                 + "` within the next 2 minutes."
#                 + "\nIf you are already logged in, please log out and back in again.\n"
#             )
#             account_linked = await self.login_checks[account_name].login_check()
#         except TimeoutError:
#             await inter.edit_original_message(
#                 "Link timed out!\nYou must log in within 2 minutes.\nPlease try again."
#             )
#             del self.login_checks[account_name]
#         else:
#             if account_linked is True:
#                 # Feedback to user that a login was detected
#                 await inter.edit_original_message(
#                     "**"
#                     + str(self.login_checks[account_name].characters[0].name)
#                     + "** Log in detected!\nNow linking accounts..."
#                 )
#                 try:
#                     # Link the discord user and PS2 char in the db
#                     await add_to_db(ps2_char, inter.author)
#                 except Exception as e:
#                     logging.error("Failed to add to the database", exc_info=e)
#                     await inter.edit_original_message(
#                         "Looks like something went wrong talking to the Database"
#                     )
#                     return
#                 else:
#                     logging.info(f"Linked {ps2_char.name.first} to {inter.author.name}")
#                     await inter.edit_original_message(
#                         "You've successfully connected accounts! :tada:\nPS2: "
#                         + str(ps2_char.name.first)
#                         + "\nDiscord: "
#                         + str(inter.author.name)
#                     )

#                     del self.login_checks[account_name]
#             elif account_linked is None:
#                 await inter.edit_original_message("Something went wrong!:cry:")
#                 del self.login_checks[account_name]
#                 return


# async def add_to_db(ps2_char: ps2.Character, author: Union[disnake.Member, disnake.User]):
#     """
#     Inserts new Documents or updates existing ones in the MongoDB

#     Parameters
#     ----------
#     ps2_char : class auraxium.ps2.Character
#         The character being attached.

#     author : class interaction.author
#         The discord Member class of the user

#     """
#     # Create a new document for the member
#     await Ps2Character(
#         id=ps2_char.id,
#         name=ps2_char.name.first,
#     ).save()
#     await Member.find_one(Member.discord.id == author.id).update(Push({Member.ps2_character_ids: ps2_char.id}))


# def setup(bot: commands.Bot):
#     bot.add_cog(InitiateDiscordPs2Link(bot))
