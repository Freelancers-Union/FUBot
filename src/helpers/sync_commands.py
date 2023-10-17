from datetime import datetime
import logging
import disnake
from disnake.ext import commands
from beanie.operators import Push, Pull

from database.models.discord import DiscordUserRole
from database.models.members import Member
from loggers.discord_logger import DiscordMemberLogger, add_member_profile


class DiscordSync(commands.Cog):
    """
    Class cog for Discord sync commands
    """

    def __init__(self, bot: commands.Bot):
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
                                Push(
                                    {
                                        Member.discord.roles: DiscordUserRole(
                                            added=datetime.utcnow(),
                                            id=role.id,
                                            name=role.name,
                                        ),
                                    }
                                )
                            )

                    # Remove surplus roles
                    for role in db_member.discord.roles:
                        if role.id not in [r.id for r in member.roles]:
                            role_class = disnake.utils.get(
                                guild.roles, name=role["role"]
                            )
                            if role_class:
                                await Member.find_one(
                                    {Member.discord.id: role.id}
                                ).update(
                                    Pull(
                                        {
                                            Member.discord.roles: DiscordUserRole(
                                                id=role.id
                                            ),
                                        }
                                    )
                                )
                else:
                    await add_member_profile(member=member)
            except Exception as e:
                logging.error(e)

    @staticmethod
    async def sync_members(guild: disnake.Guild):
        """
        Syncs members between discord and database

        Parameters
        ----------
        guild : class : disnake.Guild
        """
        members = guild.members
        while members:
            try:
                member = members.pop()
                db_member = await Member.find_one({Member.discord.id: member.id})
                if not db_member:
                    await add_member_profile(member=member)
            except Exception as e:
                logging.error(e)

    @commands.slash_command(
        dm_permission=False,
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def sync(self, inter):
        pass

    @sync.sub_command_group()
    async def discord(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @discord.sub_command()
    async def roles(self, inter: disnake.ApplicationCommandInteraction):
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

    @discord.sub_command()
    async def members(self, inter: disnake.ApplicationCommandInteraction):
        """
        Manually Sync Members
        Only available to Guild Administrators

        Parameters
        ----------
        inter : class : disnake.ApplicationCommandInteraction
        """
        await inter.response.defer(ephemeral=True)
        await inter.edit_original_message("Syncing discord members...")
        await self.sync_members(inter.guild)
        await inter.edit_original_message("Sync complete! :tada:")


def setup(bot: commands.Bot):
    bot.add_cog(DiscordSync(bot))
