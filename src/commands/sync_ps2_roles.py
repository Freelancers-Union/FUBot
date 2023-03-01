import disnake
from database_connector import Database
from commands.ps2_lookup import Ps2Lookup
from disnake.ext import commands


class Ps2RoleSync(commands.Cog):
    """
    Class cog for ps2 role sync check message.
    """
    
    DB = Database.DATABASE
    COLLECTION = DB["members"]

    @Ps2Lookup.planetside.slash_command_group(dm_permission=True)
    async def role(self, inter):
        pass

    @role.sub_command()
    async def check(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        """
        Checks if the user has the correct in-game rank for their discord role.
        """
        await inter.response.defer(ephemeral=True)
        # Get DB documents that match the relevant roles

def setup(bot: commands.Bot):
    bot.add_cog(Ps2RoleSync(bot))
