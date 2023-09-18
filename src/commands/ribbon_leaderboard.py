import itertools
import disnake
from disnake.ext import commands
from census import Census
from auraxium import ps2, Client, models
import logging
import aiohttp


class Ps2RibbonLeaderboard(commands.Cog):
    """
    Class cog for the PS2 ribbon leaderboard.
    """

    @commands.slash_command(dm_permission=True)
    async def ribbon(self, inter):
        pass

    @ribbon.sub_command()
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        """
        Print the current ribbon leaderboard
        """
        await inter.response.defer(ephemeral=True)

        outfit_members = await Census.get_outfit_with_member_characters(
            outfit_id=37509488620602936
        )

        id_list = []
        for member in outfit_members:
            id_list.append(member.character_id)

        http_url = "https://census.daybreakgames.com/s:fuofficers/get/ps2/outfit_member?c:limit=1500&c:join=character^on:character_id^to:character_id^list:0^inject_at:character(characters_achievement^on:character_id^to:character_id^inject_at:ribbons^list:1^terms:achievement_id=90040%27achievement_id=90042^show:achievement_id%27earned_count,characters_directive_tree^on:character_id^to:character_id^inject_at:directives^list:1^terms:directive_tree_id=49)&c:sort=rank_ordinal,member_since&outfit_id=37509488620602936"

        async with aiohttp.ClientSession() as session:
            async with session.get(http_url) as resp:
                data = await resp.json()

        leaderboard = {}
        for member in data["outfit_member_list"]:
            char_obj = member["character"]
            squad_ribbons = 0
            platoon_ribbons = 0
            if "ribbons" in char_obj:
                for ribbon in member["character"]["ribbons"]:

                    if ribbon["achievement_id"] == "90040":
                        squad_ribbons = int(ribbon["earned_count"])
                    elif ribbon["achievement_id"] == "90042":
                        platoon_ribbons = int(ribbon["earned_count"])
            leaderboard[char_obj["name"]["first"]] = {
                "squad_ribbons": squad_ribbons,
                "platoon_ribbons": platoon_ribbons,
            }
        top_10_squad = {}
        top_10_platoon = {}

        for name, values in leaderboard.items():
            squad_ribbons = values["squad_ribbons"]
            platoon_ribbons = values["platoon_ribbons"]

            if len(top_10_squad) < 10:
                top_10_squad[name] = squad_ribbons

            elif squad_ribbons > min(top_10_squad.values()):
                del top_10_squad[min(top_10_squad, key=top_10_squad.get)]
                top_10_squad[name] = squad_ribbons

            if len(top_10_platoon) < 10:
                top_10_platoon[name] = platoon_ribbons

            elif platoon_ribbons > min(top_10_platoon.values()):
                del top_10_platoon[min(top_10_platoon, key=top_10_platoon.get)]
                top_10_platoon[name] = platoon_ribbons

        dict_top_10_squad = dict(
            sorted(top_10_squad.items(), key=lambda x: x[1], reverse=True)
        )
        dict_top_10_platoon = dict(
            sorted(top_10_platoon.items(), key=lambda x: x[1], reverse=True)
        )

        # Format leaderboard into tables
        table_squad = "```\n"
        table_squad += f"{'Name':<20}{'Ribbons':<20}\n"
        i = 1
        for name, ribbons in dict_top_10_squad.items():
            if i == 1:
                table_squad += f"🥇 {name:<17}{ribbons:<20}\n"
            elif i == 2:
                table_squad += f"🥈 {name:<17}{ribbons:<20}\n"
            elif i == 3:
                table_squad += f"🥉 {name:<17}{ribbons:<20}\n"
            else:
                table_squad += f"{i}.  {name:<17}{ribbons:<20}\n"
            i += 1
        table_squad += "```"

        table_platoon = "```\n"
        table_platoon += f"{'Name':<20}{'Ribbons':<20}\n"
        i = 1
        for name, ribbons in dict_top_10_platoon.items():
            if i == 1:
                table_platoon += f"🥇 {name:<17}{ribbons:<20}\n"
            elif i == 2:
                table_platoon += f"🥈 {name:<17}{ribbons:<20}\n"
            elif i == 3:
                table_platoon += f"🥉 {name:<17}{ribbons:<20}\n"
            else:
                table_platoon += f"{i}.  {name:<17}{ribbons:<20}\n"
            i += 1
        table_platoon += "```"

        message = disnake.Embed(
            title="Leaderboard",
            description="Top Planetside 2 Leadership Ribbons of all time",
            color=0x9E0B0F,
        )
        message.add_field(name="Top 10 Squad Leaders", value=table_squad)
        message.add_field(name="Top 10 Platoon Leaders", value=table_platoon)
        await inter.edit_original_message(embed=message)


def setup(bot: commands.Bot):
    bot.add_cog(Ps2RibbonLeaderboard(bot))
