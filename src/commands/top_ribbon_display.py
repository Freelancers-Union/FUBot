import disnake
from disnake.ext import commands


class Ps2SquadMarkup(commands.Cog):
    """
    Class cog for ps2 squad markup help message.
    """

    @commands.slash_command(dm_permission=True)
    async def top_leaders(
            self,
            inter: disnake.ApplicationCommandInteraction,
            last_hours: int = 0,
            last_days: int = 0,
            private: bool = False,
            # outfit_tag: str = commands.Param(name="outfit tag", description="Outfit tag to search for", default="FU", choices=["FU"])
    ):
        """
        Print the markup for colourful squad names.
        """
        await inter.response.defer(ephemeral=True)
        

        await inter.edit_original_message(embed=message)


def setup(bot: commands.Bot):
    bot.add_cog(Ps2SquadMarkup(bot))
