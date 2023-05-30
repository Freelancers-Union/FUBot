from datetime import datetime

from beanie import Document, TimeSeriesConfig, Granularity
from pydantic import Field, BaseModel


class ArmAPlayer(BaseModel):
    """
    ArmAPlayer model for storing online players in the database.

    name: str
        The name of the player.
    score: int
        The score of the player.
    duration: int
        The duration the player has been online. (in seconds)
    """
    # The name of the player.
    name: str
    score: int
    duration: int


class OnlineFUArmaPlayers(Document):
    """
    OnlineFUArmaPlayers model for storing online players in the database.
    saves to timeseries collection "arma_online_members"
    timestamp: datetime
        The timestamp of the event.
    online_count: int
        The number of players online.
    online_players: list[ArmAPlayer]
        The list of online players.
    mission: str
        Name of the mission currently running on server.
    """
    timestamp: datetime
    online_count: int = -1
    online_players: list[ArmAPlayer] | None
    mission: str | None

    class Settings:
        name = "arma_online_member_log"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="mission",  # Optional
            granularity=Granularity.hours,  # Optional
        )
