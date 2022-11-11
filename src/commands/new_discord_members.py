import datetime
import disnake
from disnake.ext import commands
import logging
import src.helpers.discord_checks as dc


class NewDiscordMembers(commands.Cog):
    """
    Class cog for new Discord member report.
    """

    async def build_member_report(self, guild: disnake.Guild, days: int = 7):
        date_delta = datetime.datetime.now() - datetime.timedelta(days=days)
        all_new_members = 0
        new_ps2_members = []
        new_a3_members = []
        new_other_members = []
        members = guild.members

        while members:
            member = members.pop()
            if member.joined_at.timestamp() > date_delta.timestamp():
                all_new_members += 1
                roles: [disnake.Role] = member.roles
                no_game: bool = True
                for r in roles:
                    if r.name == "Planetside 2":
                        new_ps2_members.append(member)
                        no_game = False
                    if r.name == "Arma 3":
                        new_a3_members.append(member)
                        no_game = False
                if no_game:
                    new_other_members.append(member)

        new_ps2_message = "\n---------------\n"
        new_a3_message = "\n---------------\n"
        new_other_message = "\n---------------\n"
        for player in new_ps2_members:
            new_ps2_message = (
                    new_ps2_message + str(player) + "\n"
            )
        for player in new_a3_members:
            new_a3_message = (
                    new_a3_message + str(player) + "\n"
            )
        for player in new_other_members:
            new_other_message = (
                    new_other_message + str(player) + "\n"
            )

        Message = disnake.Embed(
            title="New Discord Member Report",
            color=0x9E0B0F,
            description=str(all_new_members)
                        + " new members joined Discord in the last "
                        + str(days)
                        + " days.\n",

        )
        Message.add_field(
            name="PlanetSide 2",
            value=str(len(new_ps2_members)) + new_ps2_message,
            inline=True,
        )
        Message.add_field(
            name="Arma 3", value=str(len(new_a3_members)) + new_a3_message, inline=True
        )
        Message.add_field(
            name="Other roles",
            value=str(len(new_other_members)) + new_other_message,
            inline=True,
        )
        return Message

    @commands.slash_command(dm_permission=False)
    async def new_member_report(
            self,
            inter: disnake.ApplicationCommandInteraction,
            days: int = 7
    ):
        """
        Report of new Discord members.

        Parameters
        ----------
        Days: How many days in the past to search for new members
        """
        await inter.response.defer(ephemeral=True)
        # find the channel, where to send the message
        channel = await dc.get_channel(inter=inter, channel_name="officers", send_error=True)
        if not channel:
            return
        elif not await dc.user_or_role_has_permission(inter=inter, channel=channel, can_write=True, send_error=True):
            return
        elif not await dc.check_if_bot_has_permission(inter=inter, channel=channel, send_error=True):
            return
        else:
            try:
                discord_analytics_button = disnake.ui.Button(
                    style=disnake.ButtonStyle.url,
                    url="https://discord.com/developers/servers/"
                        + str(inter.guild.id)
                        + "/analytics",
                    label="Server Insights",
                )
                await channel.send(
                    embed=await self.build_member_report(inter.guild, days),
                    components=discord_analytics_button,
                )
            except Exception as e:
                await inter.edit_original_message("Uh oh - an error occurred!")
                logging.exception(e)
            else:
                await inter.edit_original_message("Report posted to #officers channel")


def setup(bot: commands.Bot):
    bot.add_cog(NewDiscordMembers(bot))
