import asyncio
import disnake
from disnake.ext import commands
import aiohttp
import aiofiles
import asyncssh
import logging
import os
import urllib.parse


async def upload_mission(url):
    """
    Uploads a mission file to the Arma server.
    Base of this function was written be @necronicalpug

    :param url: The url to the mission file.
    """
    host = os.getenv("ARMA_SFTP_HOST")
    port = int(os.getenv("ARMA_SFTP_PORT"))
    username = os.getenv("ARMA_SFTP_USERNAME")
    password = os.getenv("ARMA_SFTP_PASSWORD")
    map_path = os.getenv("ARMA_SFTP_MAP_PATH")
    if not (host and port and username and password):
        raise EnvironmentError("Missing configuration for Arma server.")

    # Parse the url to get the file name and check if it is a .pbo file i.e. exported mission file for A3.
    parsed_url = urllib.parse.urlparse(url)
    file_name = parsed_url.path.split("/")[-1]
    if not (file_name[-4:] == ".pbo"):
        raise Exception("File is not a .pbo file.")

    # Open asynchronous HTTP session and download the file from the provided url.
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async with aiofiles.open(f"{file_name}", mode="wb") as f:
                await f.write(await response.read())

    # Open SSH connection to the server and upload the file to the correct directory.
    try:
        ssh_options = asyncssh.SSHClientConnectionOptions(
            username=username, password=password, known_hosts=None, connect_timeout=15
        )
        async with asyncssh.connect(host=host, port=port, options=ssh_options) as connection:
            async with connection.start_sftp_client() as sftp:
                await sftp.put(f"{file_name}", f"{map_path}/{file_name}")
    except asyncssh.SFTPError as ex:
        logging.error(f"Mission upload failed: {ex}")
        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass
    else:
        logging.info(f"Mission upload completed successfully.")
        os.remove(file_name)


class ArmAMapUpload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.timeout_min = 10
        self.bot = bot
        self.interactions: [disnake.Message] = []

    @commands.slash_command()
    async def arma(self, inter):
        pass

    @arma.sub_command()
    async def upload_mission(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        """
        Upload a map to the server.
        """
        await inter.response.defer(ephemeral=False)
        # check if user has arma/uploader role
        if not any(role.name == "Arma Uploader" for role in inter.author.roles):
            await inter.edit_original_message(
                content="You do not have permission to upload missions.\n" +
                        "https://www.govloop.com/wp-content/uploads/2015/02/data-star-trek-request-denied.gif"
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
            content="To upload again, run the command again." + "\n" + interaction_message.content
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
            if interaction.id == message.reference.message_id:
                self.interactions.remove(interaction)
                await interaction.edit(content="Map upload request received." + "\n" + interaction.content)
                try:
                    await message.reply("Uploading map to server...")
                    await upload_mission(message.attachments[0].url)
                    await message.reply("Map uploaded successfully.")
                except Exception as ex:
                    logging.exception(f"Mission upload failed: {ex}")
                    await message.reply(f"Mission upload failed.\nWith error:\n{ex}")
                return

    def cog_unload(self):
        self.bot.remove_listener(func=self.a3_map_upload_request, name="on_message")


def setup(bot: commands.Bot):
    bot.add_cog(ArmAMapUpload(bot))
