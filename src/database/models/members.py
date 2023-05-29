from beanie import Document
from database.models.discord import DiscordUser


class Member(Document):
    discord: DiscordUser
    ps2_character_ids: list[int] | None

    class Settings:
        collection = "members"
