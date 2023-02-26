from datetime import datetime
import logging
import disnake
from disnake.ext import commands
from database_connector import Database
from loggers.discord_logger import DiscordMemberLogger
from helpers.discord_db_actions import DiscordDB


class MemberRoleUpdate(commands.Cog):
    """
    Triggers when a member role changes
    """
    def __init__(self,
    client: commands.Bot):
        self.DiscordDBActions = DiscordDB()
        self.client = client
        self.onboard_roles = ["Planetside 2"]
        self.onboard_embeds = {}
        self.onboard_embeds["Planetside 2"] = self.ps2_onboard_payload


    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        """
        listens for changes to members such as role change
        If role is onboardable, DM onboarding message.
        If a role is removed, remove from database
        If a role is added, add to database

        Parameters
        ----------
        before : class : disnake.Member before change
        after : class : disnake.Member after change

        """

        try:
            # Check if the member has gained a role
            if len(before.roles) < len(after.roles):
                for gained in (set(before.roles) ^ set(after.roles)):
                    await self.DiscordDBActions.add_role(gained, after)

            # Check if the member has lost a role
            elif len(before.roles) > len(after.roles):
                for lost in (set(before.roles) ^ set(after.roles)):
                    await self.DiscordDBActions.remove_role(lost, after)
                    return
        except disnake.HTTPException:
            raise
        except disnake.Forbidden:
            raise
        except disnake.TypeError:
            raise
        except disnake.ValueError:
            raise

def setup(client):
    client.add_cog(MemberRoleUpdate(client))
