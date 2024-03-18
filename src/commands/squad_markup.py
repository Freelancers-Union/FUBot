import disnake
from disnake.ext import commands


class Ps2SquadMarkup(commands.Cog):
    """
    Class cog for ps2 squad markup help message.
    """

    @commands.slash_command(dm_permission=False, help="Print the markup for colourful squad names.")
    async def squad(self, inter):
        pass

    @squad.sub_command()
    async def markup(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        """
        Print the markup for colourful squad names.
        """
        await inter.response.defer(ephemeral=True)

        markup = {
            "Alpha": "`<font color=\"#ff0000\">✵ FU Alpha Platoon/Voice Lead ✴</font>`",
            "Bravo": "`<font color=\"#ff0000\">✵ FU Bravo Platoon/Voice Lead ✴</font>`",
            "Charlie": "`<font color=\"#ff0000\">✵ FU Charlie Platoon/Voice Lead ✴</font>`",
            "Delta": "`<font color=\"#ff0000\">✵ FU Delta Platoon/Voice Lead ✴</font>`"
        }

        message = disnake.Embed(
            title="Squad Markup",
            color=0x9E0B0F,
            description="Copy and paste the following into your squad description."
        )
        for key, value in markup.items():
            message.add_field(
                name=f"{key} Squad",
                value=value,
                inline=False
            )
        await inter.edit_original_message(embed=message)


def setup(bot: commands.Bot):
    bot.add_cog(Ps2SquadMarkup(bot))
