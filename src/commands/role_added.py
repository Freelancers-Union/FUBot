from datetime import datetime
import logging
import disnake
from disnake.ext import commands
from database_connector import Database
from loggers.discord_logger import DiscordMemberLogger
from helpers.discord_db_actions import DiscordDB


class MemberRoleUpdate(commands.Cog):
    """
    Triggers when a member role changes
    """
    def __init__(self,
    client: commands.Bot):
        self.DiscordDBActions = DiscordDB()
        self.client = client
        self.onboard_roles = ["Planetside 2"]
        self.onboard_embeds = {}
        self.onboard_embeds["Planetside 2"] = self.ps2_onboard_payload


    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        """
        listens for changes to members such as role change
        If role is onboardable, DM onboarding message.
        If a role is removed, remove from database
        If a role is added, add to database

        Parameters
        ----------
        before : class : disnake.Member before change
        after : class : disnake.Member after change

        """

        try:
            # Check if the member has gained a role
            if len(before.roles) < len(after.roles):
                for gained in (set(before.roles) ^ set(after.roles)):
                    await self.DiscordDBActions.add_role(gained, after)
                # Check if the user has gained a role that has an onboarding message
                    if str(gained.name) in self.onboard_roles:
                        await after.send(embed=self.onboard_embeds[str(gained.name)])
                        return
            # Check if the member has lost a role
            elif len(before.roles) > len(after.roles):
                for lost in (set(before.roles) ^ set(after.roles)):
                    await self.DiscordDBActions.remove_role(lost, after)
                    return
        except disnake.HTTPException:
            raise
        except disnake.Forbidden:
            raise
        except disnake.TypeError:
            raise
        except disnake.ValueError:
            raise

    ps2_onboard_payload = disnake.Embed(
        title="Welcome to PlanetSide 2 with Freelancers Union!",
        color=13729282,
        description="This message is a quick-start guide to help you get the most out of playing PlanetSide with FU.\nAny questions ping \n`@PS2 Division Officer`\n\n** **"
        )
    ps2_onboard_payload.add_field(
        name="Channels :newspaper:",
        value="> [#ps2-general](https://discord.com/channels/282514718445273089/290929845788213249) : Main chatroom to talk with your fellow soldiers.\n> [#ps2-announcements](https://discord.com/channels/282514718445273089/567172184913739787) : Noticeboard for events.\n> [#ps2-roles](https://discord.com/channels/282514718445273089/983434676477775922) : Role menu for PS2.\n> [#ps2-loadouts](https://discord.com/channels/282514718445273089/803987308935643167) : Share and discuss class loadouts.\n\n** **",
        inline=False
    )
    ps2_onboard_payload.add_field(
        name="Ops Nights :calendar:",
        value="Our Ops days are usually on **Mon**, **Wed**, **Sat** at **19:00** CET/CEST \nYou can find the most up-to-date event info in the [#schedule](https://discord.com/channels/282514718445273089/539192935258783744)\n\n** **",
        inline=False
    )
    ps2_onboard_payload.add_field(
        name="TeamSpeak :speaking_head:",
        value="We use [TeamSpeak](https://www.teamspeak.com/en/)  to chat as well as in-game comms\nIt's free and a great place to get to know the rest of the community.\n> `ts3server:` `ts.fugaming.org`\n> `password :` `futs           ` \nYou'll see a button to open TS automatically with every PS2 event announcement.\n\n** **",
        inline=False
    )
    ps2_onboard_payload.add_field(
        name="Specialist Squads :scientist:",
        value="Armour, Galaxy bombing, Construction and more... *experimental* playstyles to keep the fight interesting.\nCheck out [#ps2-roles](https://discord.com/channels/282514718445273089/983434676477775922) to learn more.\n\n** **",
        inline=False
    )
    ps2_onboard_payload.add_field(
        name="Learning and Leadership :military_medal:",
        value="> *\"Glory is loyalty, perfected.\"*\nFU Squads are cohesive and organised. We pride ourselves on being teachers as well as leaders.\n\n** **",
        inline=False
    )
    ps2_onboard_payload.add_field(
        name="Connect to FUBot :robot:",
        value="This bot is custom made by FU members!\nIt can do all sorts of cool things;\nTry it out by linking your PS2 character to FU with:\n`/link_planetside_account`\n> *Bot commands work in this DM channel too*\n\n** **",
        inline=False
    )
    ps2_onboard_payload.add_field(
        name="What Next? :thinking:",
        value="**1.** Say hello to your fellow soldiers in [Discord](https://discord.com/channels/282514718445273089/290929845788213249)\n\n**2.** Hop on [TeamSpeak](https://invite.teamspeak.com/ts.fugaming.org/?password=futs)\n\n**3.** And join us, ***Planetside***",
        inline=False
    )
    ps2_onboard_payload.set_thumbnail(
        url="https://forums.daybreakgames.com/ps2/styles/PS2/xenforo/avatars/avatar_l.png"
    )

def setup(client):
    client.add_cog(MemberRoleUpdate(client))
