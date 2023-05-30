from beanie import Document
from database.models.discord import DiscordUser


class Member(Document):
    discord: DiscordUser
    ps2_character_ids: list[int] = []
    class Settings:
        collection = "members"
