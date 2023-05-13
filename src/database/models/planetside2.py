from typing import Optional, List
from datetime import datetime

from beanie import Document, Indexed, TimeSeriesConfig, Granularity
from pydantic import BaseModel, Field


class HistoryRank(BaseModel):
    name: str
    outfit_id: int
    added: datetime


class Ps2character(Document):
    id: Indexed(int)
    current_outfit_id: Indexed(int)
    name: str
    rank: Optional[str]
    rank_history: Optional[List[HistoryRank]]
    joined: datetime
    left: Optional[datetime]


class OnlineOutfitMemberLog(Document):
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: str

    class Settings:
        name = "ps2_online_outfit_member_log"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="metadata",  # Optional
            granularity=Granularity.minutes,  # Optional
        )
