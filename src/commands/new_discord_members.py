import datetime
import disnake
from disnake.ext import commands
import logging

logging.basicConfig(level=logging.os.getenv('LOGLEVEL'), format='%(asctime)s %(funcName)s: %(message)s ',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

class NewDiscordMembers(commands.Cog):
    """
    Class cog for new Discord member report.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def post_member_report(self,
        days: int = 7,):
        date_delta = datetime.datetime.now() - datetime.timedelta(days=days)
        all_new_members = []
        new_ps2_members = []
        new_a3_members = []
        new_other_members = []
        for members in self.bot.get_all_members():
            if members.joined_at.timestamp() > date_delta.timestamp():
                all_new_members.append(members)
        for member in all_new_members:
            roles: [disnake.Role] = member.roles
            for r in roles:
                if r.name == "Planetside 2":
                    new_ps2_members.append(member)
                if r.name == "Arma 3":
                    new_a3_members.append(member)
                
            if member not in new_a3_members and member not in new_ps2_members:
                new_other_members.append(member)


        new_ps2_message = "\n---------------\n"
        new_a3_message = "\n---------------\n"
        new_other_message = "\n---------------\n"
        for i in new_ps2_members:
            new_ps2_message = new_ps2_message + "<@" + str(i.id) + ">" + "\n"
        for i in new_a3_members:
            new_a3_message = new_a3_message + "<@" + str(i.id) + ">" + "\n"
        for i in new_other_members:
            new_other_message = new_other_message + "<@" + str(i.id) + ">" + "\n"

        Message = disnake.Embed(
            title="New Discord Member Report",
            color=0x9E0B0F,
            description= str(len(all_new_members)) + " new members joined Discord in the last "+ str(days) +" days",
            )
        Message.add_field(
            name="PlanetSide 2",
            value= str(len(new_ps2_members)) + new_ps2_message,
            inline = True
            )
        Message.add_field(
            name="Arma 3",
            value= str(len(new_a3_members)) + new_a3_message,
            inline = True
            )
        Message.add_field(
            name="No Game Role",
            value= str(len(new_other_members)) + new_other_message,
            inline = True
            )
        try:
            #channel = disnake.utils.get(self.bot.get_all_channels(), guild__name='Freelancers Union [FU]', name='officers')
            channel = disnake.utils.get(self.bot.get_all_channels(), guild__name='FU Demo/Testing Server', name='officers')
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
        try:
            await self.post_member_report(days)
        except Exception as e:
            await inter.edit_original_message("Uh oh - an error occurred!")
            logging.exception(e)
        else:
            await inter.edit_original_message("Report posted to #officers channel")
        

def setup(bot: commands.Bot):
    bot.add_cog(NewDiscordMembers(bot))
