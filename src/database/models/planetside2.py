from datetime import datetime

from beanie import Document, Indexed, TimeSeriesConfig, Granularity, PydanticObjectId
from pydantic import BaseModel, Field


class RankHistory(BaseModel):
    name: str
    outfit_id: int
    added: datetime


class Ps2Character(Document):
    id: Indexed(int)
    outfit_id: Indexed(int, unique=False) | None
    name: str | None
    rank: str | None
    rank_history: list[RankHistory] | None
    joined: datetime | None

    class Settings:
        name = "ps2_characters"
        projection = {
            "_id": 1,
            "outfit_id": 1,
            "rank": 1
        }


class OnlineOutfitMemberTS(Document):
    timestamp: datetime = Field(default=datetime.utcnow())
    outfit_id: int
    online_count: int
    id: PydanticObjectId

    class Settings:
        name = "ps2_online_outfit_member_ts"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="outfit_id",  # Optional
            granularity=Granularity.minutes,  # Optional
        )
