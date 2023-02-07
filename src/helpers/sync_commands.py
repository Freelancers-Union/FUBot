import logging
import disnake
from disnake.ext import commands
from database_connector import Database
from loggers.discord_logger import DiscordMemberLogger
from helpers.discord_db_actions import DiscordDB


class DiscordSync(commands.Cog):
    """
    Class cog for Discord sync commands
    """
    def __init__(self,
            client: commands.Bot,
            db: Database
            ):
        self.db = db.DATABASE
        self.client = client

    @staticmethod
    async def sync_roles(guild: disnake.Guild):
        """
        Syncs roles between discord and database

        Parameters
        ----------
        guild : class : disnake.Guild
        """
        DiscordDBActions = DiscordDB()
        members = guild.members
        discordLogger = DiscordMemberLogger(commands.Bot, Database)
        while members:
            try:
                member = members.pop()
                db_record = Database.find_one("members", {'discord_user.id': str(member.id)})
                # Add missing roles
                if db_record:
                    for role in member.roles:
                        if role.name not in [r["role"] for r in db_record['discord_user']['roles']]:
                            await DiscordDBActions.add_role(role, member)

                    # Remove surplus roles
                    for role in db_record['discord_user']['roles']:
                        if role['role'] not in [r.name for r in member.roles]:
                            role_class = disnake.utils.get(guild.roles, name=role['role'])
                            if role_class:
                                await DiscordDBActions.remove_role(role_class, member)
                else:
                    await discordLogger.add_member_profile(member = member)
            except Exception as e:
                logging.error(e)

    @commands.slash_command(dm_permission=True)
    async def sync(self, inter):
        pass

    @sync.sub_command_group()
    async def discord(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        pass
    @discord.sub_command()
    async def roles(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        """
        Manually Sync Roles
        Only available to Guild Administrators

        Parameters
        ----------
        inter : class : disnake.ApplicationCommandInteraction
        """
        await inter.response.defer(ephemeral=True)
        await inter.edit_original_message("Syncing discord roles...")
        await self.sync_roles(inter.guild)
        await inter.edit_original_message("Sync complete! :tada:")

def setup(bot: commands.Bot):
    bot.add_cog(DiscordSync(bot, Database))
    DiscordRoleSync = DiscordSync(bot, Database)
    logging.info("Syncing Discord roles...")
    for guild in bot.guilds:
        if guild is not None:
            DiscordRoleSync.sync_roles(guild=guild)