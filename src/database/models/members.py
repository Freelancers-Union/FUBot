from datetime import datetime
from beanie import Document, Link
from pydantic import BaseModel
from typing import Optional, List
from database.models.planetside2 import Ps2character


class DiscordUserRoles(BaseModel):
    name: str
    added: datetime


class DiscordUser(BaseModel):
    name: str
    nick: Optional[str]
    joined: datetime
    left: Optional[datetime]
    roles: Optional[List[str]]


class Member(Document):
    discord: DiscordUser
    ps2_characters: Optional[List[Link[Ps2character]]]

