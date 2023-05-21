import logging
import datetime
import disnake
from disnake.ext import commands
from beanie.operators import Set, Push

from database.models.discord import DiscordGuildTS, DiscordGuildTSMetadata, DiscordUser, DiscordUserPresence, \
    DiscordUserRole
from database.models.members import Member


async def _add_member_profile(member: disnake.Member):
    """
    Adds a new member to the database

    Parameters
    ----------
    member: disnake.Member
    """
    db_member = Member.find_one(Member.discord.id == member.id)
    # If new to the DB, add a new entry.
    await db_member.upsert(
        Set({
            Member.discord.is_present: True,
            Member.discord.joined: member.joined_at,
        }),
        on_insert=Member(
            discord=DiscordUser(
                id=member.id,
                name=member.name,
                nick=member.nick,
                joined=member.joined_at,
                is_present=True,
                roles=[DiscordUserRole(id=role.id, name=role.name) for role in member.roles],
                presence_history=[]
            )
        )
    )
# TODO: We will at some point need to extend this to handle a single user in multiple tracked guilds.
#  But let's cross that bridge when we get to it.


async def _member_left(member: disnake.Member):
    """
    Updates the database when a member leaves the server.

    Parameters
    ----------
    member
        Discord member that left the server
    """
    db_member = Member.find_one(Member.discord.id == member.id)
    if db_member is None:
        logging.warning(f"Member {member.name} left but was not found in the database")
    presence_history_record = DiscordUserPresence(
        joined=member.joined_at,
        left=datetime.datetime.utcnow()
    )
    await db_member.upsert(
        Set({
            Member.discord.is_present: False,
            Member.discord.joined: None,
            Member.discord.roles: [],
        }),
        Push({
            Member.discord.presence_history: presence_history_record
        }),
        on_insert=Member(
            discord=DiscordUser(
                id=member.id,
                name=member.name,
                nick=member.nick,
                joined=None,
                roles=[],
                is_present=False,
                presence_history=[presence_history_record]
            )))


async def _save_member_count(guild_id: int, current_count: int, role_id=None):
    """
    Logs the total members of the guild and writes to the db
    Triggered by join/leave events in Discord

    Parameters
    ----------
    role_id
    guild_id: ID of Discord guild to monitor.
    current_count: the count to log
    """

    await DiscordGuildTS(
        member_count=current_count,
        metadata=DiscordGuildTSMetadata(guild_id=guild_id, role=role_id)
    ).insert()


class DiscordMemberLogger(commands.Cog):
    """
    Logs total guild member count for given guild IDs.
    Members joining or leaving will trigger the updated member count to be logged.

    Parameters
    ----------
    bot:
        Database class instance
    """

    def __init__(self):
        """
        Initializes Discord logger timeseries db
        """

        FU_guild_id = 282514718445273089
        FU_demo_guild_id = 914185528268689428
        self._monitored_guilds: {int} = {FU_guild_id, FU_demo_guild_id}

    def add_guild(self, guild_id: int):
        """
        Adds a guild to the list of monitored guilds

        Parameters
        ----------
        guild_id: ID of Discord guild to monitor.
        """
        self._monitored_guilds.add(guild_id)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: disnake.Member):
        guild_id = member.guild.id
        if guild_id in self._monitored_guilds:
            logging.info(f"Member {member.id} joined {member.guild.id}")
            await _save_member_count(guild_id, member.guild.member_count)
            await _add_member_profile(member)

    @commands.Cog.listener("on_member_remove")
    async def on_raw_member_remove(self, member: disnake.Member):
        guild_id = member.guild.id
        if guild_id in self._monitored_guilds:
            logging.info(f"Member {member.id} left {member.guild.id}")
            await _save_member_count(guild_id, member.guild.member_count)
            await _member_left(member)


def setup(bot: commands.Bot):
    bot.add_cog(DiscordMemberLogger())
