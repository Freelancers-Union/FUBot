from datetime import datetime
from typing import List, Optional

from beanie import Document, TimeSeriesConfig, Granularity
from pydantic import Field, BaseModel


class ArmAPlayer(BaseModel):
    name: str
    score: int
    duration: int

class OnlineFUArmaPlayers(Document):
    timestamp: datetime = Field(default_factory=datetime.now)
    online_count: int = -1
    online_players: Optional[List[ArmAPlayer]]
    mission: Optional[str]

    class Settings:
        name = "arma_online_outfit_member_log"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="mission",  # Optional
            granularity=Granularity.hours,  # Optional
        )
