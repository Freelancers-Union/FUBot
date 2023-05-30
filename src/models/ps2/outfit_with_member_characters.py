from datetime import datetime
from dataclasses import dataclass


@dataclass
class Name:
    first: str
    first_lower: str


class Character:
    name: Name

    def __init__(self, char_dict: dict):
        try:
            self.name = Name(**char_dict['name'])
        except Exception as e:
            print(f"KeyError: {e}")


class Ps2OutfitMember:
    def __init__(self, member_dict: dict):
        self.outfit_id: int = int(member_dict['outfit_id'])
        self.character_id: int = int(member_dict['character_id'])
        self.member_since: int = int(member_dict['member_since'])
        self.member_since_date: datetime = datetime.strptime(
            member_dict['member_since_date'],
            '%Y-%m-%d %H:%M:%S.%f'
        )
        self.rank: str = member_dict['rank']
        self.rank_ordinal: int = int(member_dict['rank_ordinal'])
        self.character: Character = Character(
            member_dict['character']
        ) if 'character' in member_dict.keys() else Character(
            {"name": {"first_lower": None, "first": None}}
        )

    def __repr__(self):
        return "OutfitMember({}, {},{}, {})".format(
            self.character_id, self.character.name.first, self.rank, self.outfit_id
        )