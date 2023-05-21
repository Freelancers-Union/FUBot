from beanie import Document, Link
from database.models.planetside2 import Ps2Character
from database.models.discord import DiscordUser


class Member(Document):
    discord: DiscordUser
    ps2_character_ids: list[int] | None

    class Settings:
        collection = "members"
