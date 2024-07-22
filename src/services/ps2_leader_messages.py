import logging
from datetime import datetime
import os
import disnake
from disnake.ext.commands import Cog, Bot
from disnake.ext import tasks
import json
import disnake
import aiohttp


class PS2LeaderBoaed(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        self.leaderbpard_channel = "🏆-leaderboard"
        self.ps2_category = "═【 Planetside 2 】═"

        self.api_url = "http://fu:3000"

        self.sl_querry = f"{self.api_url}/api/card/4/query"
        self.pl_querry = f"{self.api_url}/api/card/5/query"
        self.api_key = os.getenv("METABASE_KEY")

    async def cog_load(self):
        if not self.api_key:
            logging.error("METABASE_KEY is not set")
        try:
            logging.info("Creating Leaderboard channel")
            for guild in self.bot.guilds:
                if not disnake.utils.get(guild.channels, name=self.leaderbpard_channel):
                    category = disnake.utils.get(
                        guild.categories, name=self.ps2_category
                    )
                    await guild.create_text_channel(
                        name=self.leaderbpard_channel, category=category
                    )
        except Exception as e:
            logging.exception(
                "Error creating onboarding category and notification channel", e
            )
        self.update_leader_message.start()

    async def response_to_text(self, api_url):
        response_data = {}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json={
                    "ignore_cache": True,
                    "collection_preview": False,
                    "parameters": [],
                },
                headers={
                    "x-api-key": self.api_key,
                },
            ) as response:
                response_data = await response.json()

        table = "  #  Ribbons Name\n"
        for index, row in enumerate(response_data["data"]["rows"]):
            name = row[0]
            ribbons = row[1]
            table += f"{index:>3}.{ribbons:>6}   {name}\n"
        return table

    @tasks.loop(minutes=10)
    async def update_leader_message(self):
        try:
            logging.info("Updating ps2 Leaderboard message")
            embeds = []

            for guild in self.bot.guilds:
                leaderboard_channel = disnake.utils.get(
                    guild.channels, name=self.leaderbpard_channel
                )
                if not leaderboard_channel:
                    logging.error(
                        f"Leaderboard channel {self.leaderbpard_channel} not found in {guild.name}"
                    )
                    continue
                if not leaderboard_channel.permissions_for(guild.me).send_messages:
                    logging.error(
                        f"Bot doesn't have permissions to send messages in {leaderboard_channel.name}"
                    )
                    continue

                # check for the leaderboard message posted by bot
                leaderboard_message = disnake.utils.get(
                    await leaderboard_channel.history(limit=100).flatten(),
                    author=guild.me,
                )

                try:
                    SL_embed = disnake.Embed(
                        title="Best SLs in 7 Days",
                        description="Updated every 5 minutes",
                        color=0xFF0000,
                        timestamp=datetime.now(),
                    )
                    table = await self.response_to_text(self.sl_querry)
                    SL_embed.description += f"```{table}```"
                    embeds.append(SL_embed)
                except Exception as e:
                    logging.error("Error getting SL leaderboard", exc_info=e)

                try:
                    PL_embed = disnake.Embed(
                        title="Best PLs in 7 Days",
                        description="Updated every 5 minutes",
                        color=0xFF0000,
                        timestamp=datetime.now(),
                    )
                    table = await self.response_to_text(self.pl_querry)
                    PL_embed.description += f"```{table}```"
                    embeds.append(PL_embed)
                except Exception as e:
                    logging.error("Error getting PL leaderboard", exc_info=e)

                # Assuming 'leaderboard_message' is the variable that holds the leaderboard message
                if leaderboard_message:
                    await leaderboard_message.edit(embeds=embeds)
                else:
                    await leaderboard_channel.send(embed=embeds)

        except Exception as exception:
            logging.error(
                "Something went wrong logging ArmA3 server", exc_info=exception
            )


def setup(bot: Bot):
    bot.add_cog(PS2LeaderBoaed(bot))
