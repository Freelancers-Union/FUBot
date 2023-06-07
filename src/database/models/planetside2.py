
from datetime import datetime

from beanie import Document, Indexed, TimeSeriesConfig, Granularity
from pydantic import BaseModel, Field
from models.ps2.general import Ps2RibbonIDs


class RankHistory(BaseModel):
    name: str
    outfit_id: int
    added: datetime


class Ps2Character(Document):
    id: Indexed(int) = Field(title="_id")
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
    timestamp: datetime
    outfit_id: int
    online_count: int

    class Settings:
        name = "ps2_online_outfit_member_ts"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="outfit_id",  # Optional
            granularity=Granularity.minutes,  # Optional
        )


class Ps2RibbonMetaData(BaseModel):
    character_id: int
    ribbon_id: int


class PS2RibbonTS(Document):
    """
    Timeseries of ribbon counts
    timestamp: datetime
        Timestamp of the count
    count: int  
        Count of the ribbon
    meta: Ps2RibbonMetaData
        Metadata of the ribbon
    """
    timestamp: datetime
    ribbon_count: int
    meta: Ps2RibbonMetaData

    class Settings:
        name = "ps2_ribbon_ts"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="meta",  # Optional
            granularity=Granularity.hours,  # Optional
        )
    
    async def get_top_ribbons_in_timpespan(
            self,
            ribbon_id: Ps2RibbonIDs,
            start: datetime,
            end: datetime
        ):
        #  some stuff here isn't supported by beanie yet
        self.aggregate()
