import logging
import os
from steam import SteamQuery
from disnake.ext.commands import Cog, Bot
from disnake.ext import tasks
from database.models.arma import OnlineFUArmaPlayers, ArmAPlayer


class ArmALogger(Cog):

    def __init__(self, bot: Bot):
        try:
            self.bot = bot
            self.server_query = SteamQuery(os.getenv("ARMA_HOST"), int(os.getenv("ARMA_QUERY_PORT")))
            self.log_server_status.start()
        except Exception as exception:
            logging.error("Failed to initialize ArmA logger", exc_info=exception)

    def cog_unload(self):
        self.log_server_status.cancel()

    @tasks.loop(minutes=5)
    async def log_server_status(self):
        """
            Logs the max amount of players in server currently.
            If it can't connect to ArmA, it saves -1 as player count
        """
        try:
            response = self.server_query.query_game_server()
            player_count: int = response.get("players")
            mission = response.get("description")

            last = await OnlineFUArmaPlayers.find().sort(-OnlineFUArmaPlayers.timestamp).first_or_none()
            new = OnlineFUArmaPlayers(
                online_count=player_count,
                online_players=[
                    ArmAPlayer(name=player.name, score=player.score, duration=player.duration) for player in
                    self.server_query.query_player_info()
                ],
                mission=mission,
            )

            if last is None or last.online_players != new.player_count:
                await new.insert()
        except Exception as exception:
            logging.error("Something went wrong logging ArmA3 server", exc_info=exception)


def setup(bot: Bot):
    bot.add_cog(ArmALogger(bot))
