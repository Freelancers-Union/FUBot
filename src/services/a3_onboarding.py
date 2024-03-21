import time
import logging
import datetime
import disnake
from disnake.ext import commands
import helpers.discord_checks as dc


class OnboardA3Member(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.a3_role = "Arma 3"
        self.a3_officer_role = "Arma Division Officer"
        self.notification_channel = "arma-on-board"
        self.onboarding_category = "📜-ArmA-onboarding"
        self.onbarding_id = "a3onb-"
        self.assign_id = "assign"
        self.accepted_id = "accepted"
        self.rejected_id = "rejected"

    async def coog_load(self):
        # create the onboarding category if it doesn't exist
        for guild in self.bot.guilds:
            arma_officer_role = disnake.utils.get(
                guild.roles, name=self.a3_officer_role
            )
            if not arma_officer_role:
                logging.warning(
                    f"Role {self.a3_officer_role} not found in {guild.name}"
                )
                continue
            if not disnake.utils.get(guild.categories, name=self.onboarding_category):
                overwrites = {
                    arma_officer_role: disnake.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        manage_channels=True,
                        manage_messages=True,
                        read_message_history=True,
                    ),
                    guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                }
                await guild.create_category(
                    self.onboarding_category,
                    overwrites=overwrites,  # pyright: ignore
                )
            if not disnake.utils.get(guild.channels, name=self.notification_channel):
                category = disnake.utils.get(
                    guild.categories, name=self.onboarding_category
                )
                await guild.create_text_channel(
                    name=self.notification_channel, category=category
                )

    @commands.Cog.listener(name="on_member_update")
    async def notify_officers(self, old: disnake.Member, new: disnake.Member):
        """
        Send message to officers that new member has selected a3 role
        """
        if not (
            disnake.utils.get(new.roles, name=self.a3_role)
            and not disnake.utils.get(old.roles, name=self.a3_role)
        ):
            return

        member_request = disnake.Embed(
            title=f"New ArmA Player - {new.name}",
            description=f"Contact newly enlisted {new.mention} to get them on battle field! :military_helmet:",
            colour=disnake.Colour(14812691),
        )

        channel = disnake.utils.get(new.guild.channels, name=self.notification_channel)
        if channel is not None and channel.type == disnake.ChannelType.text:
            await channel.send(
                embed=member_request,
                components=[
                    disnake.ui.Button(
                        label="Assign to me",
                        style=disnake.ButtonStyle.success,
                        custom_id=self.onbarding_id
                        + self.assign_id
                        + "-"
                        + str(new.id),
                    )
                ],
            )

    @commands.Cog.listener("on_button_click")
    async def onboard_listener(self, inter: disnake.MessageInteraction):
        """
        Onboarding listener
            Handles the onboarding task message in Officer chat.

        Args:
            inter (disnake.MessageInteraction): The interaction

        Returns:
            None
        """
        a3_onbarding_id = "a3onb-"
        try:
            if not (inter.component.custom_id and inter.guild):
                return
            if not inter.component.custom_id.startswith(a3_onbarding_id):
                logging.info(
                    f"New member assigned to officer: {inter.component.custom_id}"
                )

            split = inter.component.custom_id.split("-")
            action = split[1]
            member_id = int(split[2])

            member_id = int(inter.component.custom_id.split("-")[-1])
            member = inter.guild.get_member(member_id)
            if member is None:
                embed = inter.message.embeds[0]
                embed.description = (
                    "Member not found"
                    if not embed.description
                    else embed.description + "\nMember not found"
                )
                await inter.response.edit_message(embed=embed)
                return

            onbaoarding_channel_name = f"onboarding-{str(member.name).lower()}"

            # Create a private channel for the new member and the officer
            if action == self.assign_id:
                overwrites = {
                    inter.guild.default_role: disnake.PermissionOverwrite(
                        view_channel=False
                    ),
                    member: disnake.PermissionOverwrite(
                        view_channel=True, send_messages=True, read_message_history=True
                    ),
                }

                # Create the channel
                category = disnake.utils.get(
                    inter.guild.categories, name=self.onboarding_category
                )
                onboarding_channel = await inter.guild.create_text_channel(
                    name=onbaoarding_channel_name,
                    overwrites=overwrites,
                    category=category,
                )
                for member in [member, inter.author]:
                    await onboarding_channel.set_permissions(
                        target=member,
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                    )

                # Update the embed to show the new member has been assigned to an officer
                embed = inter.message.embeds[0]
                embed.add_field(
                    name="Assigned To:", value=f"{inter.author.mention}", inline=False
                ).set_footer(text=f"Communication initiated: <t:{time.time()}:F>")
                embed.colour = disnake.Colour(12757760)
                await inter.response.edit_message(
                    embed=embed,
                    components=[
                        disnake.ui.Button(
                            label="Accepted",
                            style=disnake.ButtonStyle.green,
                            custom_id=self.onbarding_id
                            + self.accepted_id
                            + "-"
                            + str(member.id),
                        ),
                        disnake.ui.Button(
                            label="Rejected",
                            style=disnake.ButtonStyle.red,
                            custom_id=self.onbarding_id
                            + self.rejected_id
                            + "-"
                            + str(member.id),
                        ),
                    ],
                )

            else:
                embed = inter.message.embeds[0]
                if action == self.accepted_id:
                    embed.description = f"{member.mention} has been onbarded"
                elif action == self.rejected_id:
                    embed.description = f"{member.mention} has Failed onboarding"
                # Update the embed to show the new member has accepted and add the member role
                embed.colour = disnake.Colour(1150720)
                embed.add_field(
                    name="Closed at:", value=f"<t:{time.time()}:F>", inline=False
                )
                await inter.response.edit_message(embed=embed, components=None)
                onboarding_channel = await dc.get_channel(
                    inter, channel_name=onbaoarding_channel_name
                )
                if not onboarding_channel:
                    embed.add_field(
                        name="Error",
                        value="Onboarding channel not found. I can't delete it",
                        inline=False,
                    )
                else:
                    await onboarding_channel.delete()

        except Exception as e:
            logging.exception(e)
            await inter.send(
                content=f"Something went wrong, you should check the user's roles. and give Botanists this timestamp: {datetime.datetime.now()}",
            )


def setup(bot: commands.Bot):
    bot.add_cog(OnboardA3Member(bot))
