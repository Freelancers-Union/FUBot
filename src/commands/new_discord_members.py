import datetime
import disnake
from disnake.ext import commands
import logging
import time

logging.basicConfig(level=logging.os.getenv('LOGLEVEL'), format='%(asctime)s %(funcName)s: %(message)s ',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


class NewDiscordMembers(commands.Cog):
    """
    Class cog for new Discord member report.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def post_member_report(self, guild: disnake.Guild, days: int = 7):
        date_delta = datetime.datetime.now() - datetime.timedelta(days=days)
        all_new_members = []
        new_ps2_members = []
        new_a3_members = []
        new_other_members = []
        members = guild.members
        # start = time.time()
        # for member in members:
        while members:
            member = members.pop()
            if member.joined_at.timestamp() > date_delta.timestamp():
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
        # end = time.time()

        new_ps2_message = "\n---------------\n"
        new_a3_message = "\n---------------\n"
        new_other_message = "\n---------------\n"
        for player in new_ps2_members:
            new_ps2_message = new_ps2_message + player.mention + "\n"
        for player in new_a3_members:
            new_a3_message = new_a3_message + player.mention + "\n"
        for player in new_other_members:
            new_other_message = new_other_message + player.mention + "\n"

        Message = disnake.Embed(
            title="New Discord Member Report",
            color=0x9E0B0F,
            description=str(len(all_new_members)) + " new members joined Discord in the last " + str(days) + " days",
        )
        Message.add_field(
            name="PlanetSide 2",
            value=str(len(new_ps2_members)) + new_ps2_message,
            inline=True
        )
        Message.add_field(
            name="Arma 3",
            value=str(len(new_a3_members)) + new_a3_message,
            inline=True
        )
        Message.add_field(
            name="No Game Role",
            value=str(len(new_other_members)) + new_other_message,
            inline=True
        )
        # Message.add_field(
        #     name="time taken(playing with optimisation that is absolutely not needed)",
        #     value=f"replacing if in game role list: {(end-start)*10**3}ms"
        # )
        try:
            channel = disnake.utils.find(lambda chanel: chanel.name == 'officers', guild.channels)
        except AttributeError as e:
            raise e
        await channel.send(embed=Message)

    @commands.slash_command()
    async def new_member_report(
            self,
            inter: disnake.ApplicationCommandInteraction,
            days: int = 7,
    ):
        """
        Report of new Discord members.

        Parameters
        ----------
        Days: How many days in the past to search for new members
        """
        await inter.response.defer(ephemeral=True)
        # find the channel, where to send the message
        channels: [disnake.abc.GuildChannel] = await inter.guild.fetch_channels()
        channel = None
        for ch in channels:
            if ch.name == "officers":
                channel = ch
        if not channel.permissions_for(inter.author).send_messages:
            await inter.edit_original_message(
                "Imitating the Captain, huh? Surely that violates some kind of Starfleet protocol." +
                "\n You don't have the permission to announce, so I won't"
            )
        elif channel is None:
            await inter.edit_original_message("Impossible. Perhaps the Archives are incomplete." +
                                              "\n I can't find #officers.")
        elif not channel.permissions_for(channel.guild.me).send_messages:
            await inter.edit_original_message("My lord, is that legal? \n I don't have the permissions to send there")
        else:
            try:
                await self.post_member_report(inter.guild, days)
            except Exception as e:
                await inter.edit_original_message("Uh oh - an error occurred!")
                logging.exception(e)
            else:
                await inter.edit_original_message("Report posted to #officers channel")


def setup(bot: commands.Bot):
    bot.add_cog(NewDiscordMembers(bot))