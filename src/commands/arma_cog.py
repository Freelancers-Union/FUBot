import asyncio
import disnake
from disnake.ext import commands
import logging

from commands.arma.get_db import get_players, get_mapping, add_mapping
from commands.arma.upload_map import upload_mission


class ArmACog(commands.Cog):
    """
    Class cog for Arma commands.
    """

    def __init__(self, bot: commands.Bot):
        self.timeout_min = 10
        self.bot = bot
        self.interactions: [disnake.Message] = []

    @commands.slash_command()
    async def arma(self, inter):
        pass

    @arma.sub_command()
    async def upload_mission(self, inter: disnake.ApplicationCommandInteraction):
        """
        Upload a map to the server.
        """
        await inter.response.defer(ephemeral=False)
        # check if user has arma/uploader role
        if not any(role.name == "Arma Uploader" for role in inter.author.roles):
            await inter.edit_original_message(
                content="You do not have permission to upload missions.\n"
                + "https://www.govloop.com/wp-content/uploads/2015/02/data-star-trek-request-denied.gif"
            )
            return
        await inter.edit_original_message(
            content=f"Within {self.timeout_min} min reply to this message with the attached `.pbo` "
            "file to upload the mission to the server."
        )

        interaction_message = await inter.original_message()
        self.interactions.append(interaction_message)

        await asyncio.sleep(self.timeout_min * 60)
        await interaction_message.edit(
            content="To upload again, run the command again."
            + "\n"
            + interaction_message.content
        )
        try:
            self.interactions.remove(interaction_message)
        except ValueError:
            pass

    @commands.Cog.listener("on_message")
    async def a3_map_upload_request(self, message: disnake.Message):
        if not message.attachments or not self.interactions:
            return
        for interaction in self.interactions:
            if message.reference and interaction.id == message.reference.message_id:
                self.interactions.remove(interaction)
                await interaction.edit(
                    content="Map upload request received."
                    + "\n ~~"
                    + interaction.content
                    + "~~"
                )
                try:
                    uploading_message = await message.reply(
                        "Uploading map to server..."
                    )
                    await upload_mission(message.attachments[0].url)
                    if uploading_message:
                        await uploading_message.edit(
                            "Mission `"
                            + message.attachments[0].filename
                            + "` uploaded successfully."
                        )
                except Exception as ex:
                    logging.exception(f"Mission upload failed: {ex}")
                    await message.reply(f"Mission upload failed.\nWith error:\n{ex}")
                return

    @arma.sub_command()
    async def get_players(self, inter: disnake.ApplicationCommandInteraction):
        """
        Display a list of players that have played on the Arma server.
        """
        await inter.response.defer(ephemeral=False)

        message = await get_players()

        await inter.edit_original_message(content=message)

    @arma.sub_command()
    async def get_mapping(self, inter: disnake.ApplicationCommandInteraction):
        """
        Display the Discord <--> Steam user mapping.
        """
        await inter.response.defer(ephemeral=False)

        message = await get_mapping()

        await inter.edit_original_message(content=message)

    @arma.sub_command()
    async def add_mapping(
        self, inter: disnake.ApplicationCommandInteraction, steam_id: str
    ):
        """
        Add a Discord <--> Steam user mapping.
        Parameters
        ----------
        steam_id: str
            The Steam ID to add to the mapping.
        """
        await inter.response.defer(ephemeral=False)

        username = inter.author.name
        discord_id = str(inter.author.id)

        message = await add_mapping(username, discord_id, steam_id)

        await inter.edit_original_message(content=message)


def setup(bot: commands.Bot):
    bot.add_cog(ArmACog(bot))
