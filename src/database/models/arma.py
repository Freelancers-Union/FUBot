from datetime import datetime

from beanie import Document, TimeSeriesConfig, Granularity
from pydantic import Field, BaseModel


class ArmAPlayer(BaseModel):
    name: str
    score: int
    duration: int


class OnlineFUArmaPlayers(Document):
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
