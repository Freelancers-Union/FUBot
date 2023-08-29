from datetime import datetime, timedelta
import disnake
from disnake.ext import commands
from database.models.planetside2 import PS2RibbonDiff, PS2RibbonTS
from models.ps2.general import Ps2RibbonIDs


class Ps2RibbonsCog(commands.Cog):
    """
    Class cog for ps2 character lookup
    """
    @commands.slash_command(dm_permission=True)
    async def planetside(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        pass

    @planetside.sub_command_group()
    async def stats(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        pass

    async def autocomplete_R(inter, string: str) -> list[str]:
        events = [""]
        return [event for event in events if string.lower() in event.lower()]


    # @stats.sub_command()
    @commands.slash_command(dm_permission=True)
    async def top_leaders(
            self,
            inter: disnake.ApplicationCommandInteraction,
            ribbon_type: str = commands.param(choices=list(Ps2RibbonIDs.__members__.keys()), default=Ps2RibbonIDs.SquadLeadership.name),
            count: int = 10,
            hours: int = 0,
            days: int = 0,
            months: int = 0,
            private: bool = False
    ):
        # todo: docstring
        """
        """
        await inter.response.defer(ephemeral=True)
        await inter.edit_original_message(f"Digging up the records 📜")
        # try:
        end_time = datetime.utcnow()
        time_diff = timedelta(hours=hours, days=(days+months*30))
        start_time = end_time - time_diff
        ribbon_diffs = await PS2RibbonDiff.get_top_ribbons_in_timpespan(
            ribbon_id = Ps2RibbonIDs[ribbon_type],
            start=start_time,
            end=end_time,
            count=count
            )
        embed = self.render_top_ribbon_message(ribbon_diffs, ribbon_type, time_diff, count)
        await inter.edit_original_message(embed=embed)
        # except Exception as e:
        #     logg


    def render_top_ribbon_message(
            self,
            ribbon_diffs: list[PS2RibbonDiff],
            ribbon_name: str,
            time_diff: timedelta
    ) -> disnake.Embed:
        time_string = ""
        if time_diff.days > 0:
            time_string += f"{time_diff.days} days, "
        if time_diff.seconds > 3600:
            time_string += f"{time_diff.seconds // 3600}h, "
        if time_diff.seconds % 3600 > 60:
            time_string += f"{time_diff.seconds % 3600 // 60}min"
        
        embed_title: str = f"Top {len(ribbon_diffs)} {ribbon_name} in the last {time_string}"
        embed_description: str = "Place | Gained | Total in end |   Name"

        # build embed 
        for index, ribbon_diff in enumerate(ribbon_diffs):
            ribbon_diff = ribbon_diffs[index]
            embed_description += f"\n{index + 1:>4} | {ribbon_diff.diff:>6} | {ribbon_diff.latest.ribbon_count} | {ribbon_diff.character.name}"

        embed = disnake.Embed(
            title=embed_title,
            description=embed_description,
            color=disnake.Color.red()
        )
        return embed

def setup(bot: commands.Bot):
    bot.add_cog(Ps2RibbonsCog(bot))