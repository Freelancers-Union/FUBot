from datetime import datetime

from beanie import Document, Indexed, TimeSeriesConfig, Granularity
from pydantic import BaseModel, Field


class OnlineTeamspeakTS(Document):
    timestamp: datetime
    online_count: int

    class Settings:
        name = "ts3_online_member_ts"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            granularity=Granularity.minutes,  # Optional
        )
