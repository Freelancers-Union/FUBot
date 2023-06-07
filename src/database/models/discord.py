from datetime import datetime
from beanie import Indexed, Document, TimeSeriesConfig, Granularity
from pydantic import BaseModel, Field


class DiscordUserRole(BaseModel):
    id: int
    name: str | None
    added: datetime | None


class DiscordUserPresence(BaseModel):
    joined: datetime
    left: datetime


class DiscordUser(BaseModel):
    id: Indexed(int) = Field(title="_id")
    name: Indexed(str) | None
    nick: str | None
    joined: datetime | None
    roles: list[DiscordUserRole]
    is_present: bool | None
    presence_history: list[DiscordUserPresence] | None


class DiscordGuildTSMetadata(BaseModel):
    guild_id: Indexed(int)


class DiscordGuildTS(Document):
    timestamp: datetime
    metadata: DiscordGuildTSMetadata
    member_count: int

    class Settings:
        name = "discord_guild_ts"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="metadata",  # Optional
            granularity=Granularity.hours,  # Optional
        )
