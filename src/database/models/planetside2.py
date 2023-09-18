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
        projection = {"_id": 1, "outfit_id": 1, "rank": 1}


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
    meta: Ps2RibbonMetaData | None

    class Settings:
        name = "ps2_ribbon_ts"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",  # Required
            meta_field="meta",  # Optional
            granularity=Granularity.hours,  # Optional
        )


class PS2RibbonDiff(BaseModel):
    character: Ps2Character | None
    _id: int | None
    diff: int | None
    before: PS2RibbonTS | None
    latest: PS2RibbonTS | None

    @staticmethod
    async def get_top_ribbons_in_timpespan(
        ribbon_id: Ps2RibbonIDs,
        start: datetime,
        end: datetime,
        count: int = 10,
    ):
        #  some stuff here isn't supported by beanie yet
        aggregation = PS2RibbonTS.aggregate(
            # aggregation_model=PS2RibbonDiff,
            aggregation_pipeline=[
                {
                    "$match": {
                        "$and": [
                            {"meta.ribbon_id": ribbon_id.value},
                            {"timestamp": {"$gt": start, "$lt": end}},
                        ]
                    }
                },
                {"$sort": {"timestamp": -1}},
                {
                    "$group": {
                        "_id": "$meta.character_id",
                        "latest": {
                            "$first": {
                                "timestamp": "$timestamp",
                                "ribbon_count": "$ribbon_count",
                            }
                        },
                    }
                },
                {
                    "$lookup": {
                        "from": "ps2_ribbon_ts",
                        "let": {"char_id": "$_id", "timestamp": start},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {
                                                "$eq": [
                                                    "$meta.character_id",
                                                    "$$char_id",
                                                ]
                                            },
                                            {
                                                "$eq": [
                                                    "$meta.ribbon_id",
                                                    ribbon_id.value,
                                                ]
                                            },
                                            {"$lt": ["$timestamp", "$$timestamp"]},
                                        ]
                                    }
                                }
                            },
                            {
                                "$project": {
                                    "_id": 0,
                                    "timestamp": "$timestamp",
                                    "ribbon_count": {
                                        "$cond": {
                                            "if": {"$ne": ["$ribbon_count", None]},
                                            "then": "$ribbon_count",
                                            "else": 0,
                                        }
                                    },
                                }
                            },
                        ],
                        "as": "previous",
                    }
                },
                {
                    "$lookup": {
                        "from": "ps2_characters",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "character",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "character": {"$arrayElemAt": ["$character", 0]},
                        "diff": {
                            "$subtract": [
                                "$latest.ribbon_count",
                                {"$first": "$previous.ribbon_count"},
                            ]
                        },
                        "latest": 1,
                        "before": {
                            "ribbon_count": {"$first": "$previous.ribbon_count"},
                            "timestamp": {"$first": "$previous.timestamp"},
                        },
                    }
                },
                {"$match": {"before": {"$ne": None}}},
                {"$sort": {"diff": -1}},
                {"$limit": count},
            ]
        )
        result = await aggregation.to_list()
        # # write result to json file
        # with open("result.json", "w") as f:
        #     f.write(str(result))
        return result
