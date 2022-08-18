import disnake
import datetime
from disnake.ext import commands
from database_connector import Database


class DiscordMemberDB(commands.Cog):
    """
    Triggers when a member joins the guild

    """

    async def update_member_count(self, member):
        total_members = {
            "metadata": {"guild": member.guild.id},
            "timestamp": datetime.datetime.now(),
            "members": member.guild.member_count,
        }
        Database.insert_one("discord members", total_members)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        query = {"discord_user.id": str(member.id)}
        db_entry = Database.find_one("members", query)
        if db_entry is None:
            disc_obj = {}
            data = {}
            discord_attrs = ["id", "name", "nick", "joined_at"]
            for count, ele in enumerate(discord_attrs):
                disc_obj[ele] = str(getattr(member, ele))
            disc_obj["name"] = (
                str(disc_obj["name"]) + "#" + str(disc_obj["discriminator"])
            )
            data["discord_user"] = disc_obj
            Database.insert_one("members", data)
        else:
            query = {"discord_user.id": str(member.id)}
            data = {"$set": {"discord_user.rejoined_at": str(member.joined_at)}}
            Database.update_one("members", query, data)
        await self.update_member_count(member)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        query = {"discord_user.id": str(member.id)}
        data = {
            "$set": {
                "discord_user.left_at": str(
                    datetime.datetime.now(datetime.timezone.utc)
                )
            }
        }
        Database.update_one("members", query, data)
        await self.update_member_count(member)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def add_all_members(
        self, inter: disnake.ApplicationCommandInteraction
    ):
        """
        Updates every member in the guild to the DB WARNING: may take a long time.

        """
        await inter.response.defer(ephemeral=True)
        all_mems = []
        async for member in inter.guild.fetch_members():
            query = {"discord_user.id": str(member.id)}
            db_entry = Database.find_one("members", query)
            if db_entry is None:
                disc_obj = {}
                data = {}
                discord_attrs = ["id", "name", "nick", "joined_at"]
                for count, ele in enumerate(discord_attrs):
                    disc_obj[ele] = str(getattr(member, ele))
                disc_obj["name"] = (
                    str(disc_obj["name"]) + "#" + str(member.discriminator)
                )
                data["discord_user"] = disc_obj
                all_mems.append(data)
        if all_mems is not None:
            Database.insert_many("members", all_mems)
            await inter.edit_original_message("Complete. Added: " + str(len(all_mems)))
        else:
            await inter.edit_original_message("No new members to add.")



def setup(bot: commands.Bot):
    bot.add_cog(DiscordMemberDB(bot))
