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
            if response.status != 200:
                logging.error(f"Failed to get Arma players: {response.status}")
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
            if response.status != 200:
                logging.error(f"Failed to get mapping: {response.status}")
                return "Failed to get mapping."
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

async def add_mapping(username: str, discord_id: str, steam_id: str):
    """
    Adds a Discord <--> Steam user mapping.
    """

    if len(steam_id) < 1:
        return "Steam ID cannot be empty."

    host = os.getenv("ARMA_DB_HOST")
    api_key = os.getenv("ARMA_DB_TOKEN")
    if not (host and api_key):
        raise EnvironmentError("Missing configuration for Arma DB.")

    # Prepare the url and headers for the request.
    url = f"https://{host}/mapping" + "?q={" f'"Discord_ID":"{discord_id}"' + "}"

    headers = {
        "content-type": "application/json",
        "x-apikey": api_key,
        "cache-control": "no-cache",
    }

    # Open asynchronous HTTP session and get the collection of players.
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                logging.error(f"Failed to get mapping: {response.status}")
                return "Failed to get mapping."
            records = await response.json()

            # Check if the response is a list and if it is empty.
            if type(records) is list:
                if len(records) > 0:  # Check if the record already exists
                    id = records[0]["_id"]
                    if records[0]["Steam_ID"] == steam_id:
                        return f"Mapping for `{username} ({discord_id})` to `{steam_id}` already exists."

                    url = f"https://{host}/mapping/{id}"

                    payload = {
                        "Discord_Username": username,
                        "Discord_ID": discord_id,
                        "Steam_ID": steam_id,
                    }

                    async with session.put(url, json=payload) as response_2:
                        if response_2.status != 200:
                            logging.error(f"Failed to update mapping: {response_2.status}")
                            return "Failed to update mapping."
                        return f"Mapping for `{username} ({discord_id})` to `{steam_id}` updated successfully."


                else: # Create a new record
                    url = f"https://{host}/mapping"

                    payload = {
                        "Discord_Username": username,
                        "Discord_ID": discord_id,
                        "Steam_ID": steam_id,
                    }

                    async with session.post(url, json=payload) as response_2:
                        if response_2.status != 201:
                            logging.error(f"Failed to add mapping: {response_2.status}")
                            return "Failed to add mapping."
                        return f"Mapping for `{username} ({discord_id})` to `{steam_id}` added successfully."

            else:
                logging.error("Response is not a list.")
                raise Exception("Response is not a list.")

