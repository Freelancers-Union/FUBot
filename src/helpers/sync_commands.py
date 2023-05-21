import logging
import disnake
from disnake.ext import commands
from beanie.operators import Push, Pull

from database.models.discord import DiscordUserRole
from database.models.members import Member
from loggers.discord_logger import DiscordMemberLogger, _add_member_profile


class DiscordSync(commands.Cog):
    """
    Class cog for Discord sync commands
    """

    def __init__(self,
                 bot: commands.Bot
                 ):
        self.bot = bot

    @staticmethod
    async def sync_roles(guild: disnake.Guild):
        """
        Syncs roles between discord and database

        Parameters
        ----------
        guild : class : disnake.Guild
        """
        members = guild.members
        while members:
            try:
                member = members.pop()
                db_member = await Member.find_one({Member.discord.id: member.id})
                # Add missing roles
                if db_member:
                    for role in member.roles:
                        if role.id not in [r.id for r in db_member.discord.roles]:
                            await Member.find_one({Member.discord.id: role.id}).update(
                                Push({
                                    Member.discord.roles: DiscordUserRole(id=role.id, name=role.name),
                                }
                                ))

                    # Remove surplus roles
                    for role in db_member.discord.roles:
                        if role.id not in [r.id for r in member.roles]:
                            role_class = disnake.utils.get(guild.roles, name=role['role'])
                            if role_class:
                                await Member.find_one({Member.discord.id: role.id}).update(
                                    Pull({
                                        Member.discord.roles: DiscordUserRole(id=role.id),
                                    })
                                )
                else:
                    await _add_member_profile(member=member)
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
    bot.add_cog(DiscordSync(bot))
    DiscordRoleSync = DiscordSync(bot)
    logging.info("Syncing Discord roles...")
    for guild in bot.guilds:
        if guild is not None:
            DiscordRoleSync.sync_roles(guild=guild)
