import disnake
from disnake.ext import commands

import aiohttp
import aiofiles
import asyncssh
import logging
import os
import urllib.parse


async def upload_mission(url):
    # TODO: Need to check if the user has permission to upload missions.
    # TODO: Need to fetch the login and server details from the database.

    # Parse the url to get the file name and check if it is a .pbo file i.e. exported mission file for A3.
    parsed_url = urllib.parse.urlparse(url)
    file_name = parsed_url.path.split("/")[-1]
    if not (file_name[-4:] == ".pbo"):
        # 2 Throw error about incorrect file extension.
        pass

    # Open asynchronous HTTP session and download the file from the provided url.
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async with aiofiles.open(f"{file_name}", mode="wb") as f:
                await f.write(await response.read())

    # Open SSH connection to the server and upload the file to the correct directory.
    try:
        async with asyncssh.connect(host, port, username, password) as connection:
            async with connection.start_sftp_client() as sftp:
                await sftp.put(f"{file_name}", f"/mpmissions/{file_name}")
    except asyncssh.SFTPError as ex:
        logging.error(f"Mission upload failed: {ex}")
    else:
        logging.info(f"Mission upload completed successfully.")
        os.remove(file_name)


class ArmAMapUpload(commands.Cog):
    """
    """

    @commands.slash_command()
    async def arma(self, inter):
        pass

    @arma.sub_command()
    async def upload_map(
            self,
            inter: disnake.ApplicationCommandInteraction,
            file=commands.Param()
    ):
        """
        Upload a map to the server.
        """
        await inter.response.defer(ephemeral=True)



def setup(bot: commands.Bot):
    bot.add_cog(ArmAMapUpload(bot))
