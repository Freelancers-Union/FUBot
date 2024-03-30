import aiohttp
import disnake
from disnake.ext import commands
import logging
import os
import pandas as pd


async def get_players():
    """
    Gets the list of players that have played on the Arma server.
    """
    host = os.getenv("ARMA_DB_HOST")
    api_key = os.getenv("ARMA_DB_TOKEN")
    if not (host and api_key):
        raise EnvironmentError("Missing configuration for Arma DB.")

    # Prepare the url and headers for the request.
    url = f"https://{host}/attendance"

    headers = {
        "content-type": "application/json",
        "x-apikey": api_key,
        "cache-control": "no-cache",
    }

    # Open asynchronous HTTP session and get the collection of players.
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            assert response.status == 200, f"Failed to get players: {response.status}"
            records = await response.json()
            new_records = []

            # Check if the response is a list and if it is empty.
            if type(records) is list:
                if len(records) == 0:
                    return "No players found."

                # Prepare the data for a pandas DataFrame.
                for x, y in enumerate(records):
                    new_records.append(
                        (
                            y["Profile_Name"],
                            y["Missions_Attended"],
                            y["Date_Of_Last_Mission"].split("T")[0],
                            y["Steam_UID"],
                        )
                    )

                df = pd.DataFrame(
                    new_records,
                    index=None,
                    columns=("Name", "Missions Attended", "Last Seen", "Steam UID"),
                )

                return f"```{df.to_string(index=False)}\nTotal Players Tracked: {len(df)}```"

            else:
                logging.error("Response is not a list.")
                raise Exception("Response is not a list.")

async def get_mapping():
    """
    Gets the Discord <--> Steam user mapping.
    """
    host = os.getenv("ARMA_DB_HOST")
    api_key = os.getenv("ARMA_DB_TOKEN")
    if not (host and api_key):
        raise EnvironmentError("Missing configuration for Arma DB.")

    # Prepare the url and headers for the request.
    url = f"https://{host}/mapping"

    headers = {
        "content-type": "application/json",
        "x-apikey": api_key,
        "cache-control": "no-cache",
    }

    # Open asynchronous HTTP session and get the collection of players.
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            assert response.status == 200, f"Failed to get records: {response.status}"
            records = await response.json()
            new_records = []

            # Check if the response is a list and if it is empty.
            if type(records) is list:
                if len(records) == 0:
                    return "No records found."

                # Prepare the data for a pandas DataFrame.
                for x, y in enumerate(records):
                    new_records.append(
                        (
                            y["Discord_Username"],
                            y["Discord_ID"],
                            y["Steam_ID"],
                        )
                    )

                df = pd.DataFrame(
                    new_records,
                    index=None,
                    columns=("Username", "Discord ID", "Steam ID"),
                )

                return f"```{df.to_string(index=False)}\nTotal Players Mapped: {len(df)}```"

            else:
                logging.error("Response is not a list.")
                raise Exception("Response is not a list.")

