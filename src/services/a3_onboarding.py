import os
import logging
import datetime
from typing import List
import disnake
from disnake.ext import commands
from disnake.enums import ButtonStyle
import helpers.discord_checks as dc


class Menu(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed], member=disnake.Member):
        super().__init__(timeout=None)
        self.guild_member = member
        self.embeds = embeds
        self.index = 0
        self.member_role = "Member"
        self.notification_channel = "officers"
        self.requested = False

        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            white_dots = "⚪️" * (i + 1)
            black_dots = "⚫️" * (len(self.embeds) - i - 1)
            embed.set_footer(
                text=f"{white_dots}{black_dots}\n\nIf this message stops responding, you can regenerate it using /intro in the FU server"
            )

        self._update_state()

    def _update_state(self) -> None:
        # self.member.disabled = self.index != len(self.embeds) - 1
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = (
            self.index == len(self.embeds) - 1
        )
        if self.index == len(self.embeds) - 1 and self.requested is False:
            member_role = disnake.utils.get(
                self.guild_member.roles, name=self.member_role
            )
            if member_role is None:
                self.add_item(self.member)
        else:
            self.remove_item(self.member)

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
    async def first_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        self.index = 0
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        self.index -= 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Membership", style=disnake.ButtonStyle.green)
    async def member(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        await self.notify_send(author=inter.author)
        self.remove_item(self.member)
        request = disnake.Embed(
            title="Membership",
            description="Request received!\nAn Officer will be in touch soon to get you onboard :ship:\n\nIn the meantime, head over and chat with the rest of the community in the [#general](https://discord.com/channels/282514718445273089/282514718445273089) channel!",
            colour=disnake.Colour(14812691),
        ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/986678839008690176/1071460284922855444/09-membership.png"
        )
        self.requested = True
        await inter.response.edit_message(embed=request, view=self)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        self.index += 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        self.index = len(self.embeds) - 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    async def notify_send(self, author=None):
        member_request = disnake.Embed(
            title=f"Membership Request - {author.name}",
            description="Please contact this player to get them onboard! :ship:",
            colour=disnake.Colour(14812691),
        ).add_field(name="User:", value=f"{author.mention}")
        channel = disnake.utils.get(
            self.guild_member.guild.channels, name=self.notification_channel
        )
        if channel is not None:
            await channel.send(
                embed=member_request,
                components=[
                    disnake.ui.Button(
                        label="Assign to me",
                        style=disnake.ButtonStyle.success,
                        custom_id="assign",
                    )
                ],
            )


class OnboardA3Member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.a3_role = "Arma 3"
        self.member_role = "Member"
        self.public_role = "Public player"
        self.guest_role = "Guest"
        self.notification_channel = "arma-on-board"

    @commands.Cog.listener(name="on_member_update")
    async def notify_officers(self, old: disnake.Member, new: disnake.Member):
        """
        Send message to officers that new meber has selected a3 role
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
                        custom_id="assign",
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
        try:
            if inter.component.custom_id not in ["assign", "accepted", "rejected"]:
                return
            Embed = inter.message.embeds[0]
            new_member = inter.guild.get_member(int(Embed.fields[0].value[2:-1]))

            if inter.component.custom_id == "assign":
                # Create a private channel for the new member and the officer
                overwrites = {
                    inter.guild.default_role: disnake.PermissionOverwrite(
                        view_channel=False
                    ),
                    new_member: disnake.PermissionOverwrite(
                        view_channel=True, send_messages=True, read_message_history=True
                    ),
                    inter.author: disnake.PermissionOverwrite(
                        view_channel=True, send_messages=True, read_message_history=True
                    ),
                    self.bot.user: disnake.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                        manage_channels=True,
                        manage_messages=True,
                    ),
                }
                onboarding_channel = await inter.guild.create_text_channel(
                    name=f"onboarding-{str(new_member.name).lower()}",
                    overwrites=overwrites,
                )
                for member in [new_member, inter.author]:
                    await onboarding_channel.set_permissions(
                        target=member,
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                    )

                # Update the embed to show the new member has been assigned to an officer
                Embed.description = f"Created private channel: {onboarding_channel.mention}\nChannel will self-destruct once onboarding is complete."
                Embed.add_field(
                    name="Assigned To:", value=f"{inter.author.mention}", inline=False
                ).set_footer(
                    text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}"
                )
                Embed.colour = disnake.Colour(12757760)
                await inter.response.edit_message(
                    embed=Embed,
                    components=[
                        disnake.ui.Button(
                            label="Accepted",
                            style=disnake.ButtonStyle.green,
                            custom_id="accepted",
                        ),
                        disnake.ui.Button(
                            label="Rejected",
                            style=disnake.ButtonStyle.red,
                            custom_id="rejected",
                        ),
                    ],
                )

            elif inter.component.custom_id == "accepted":
                # Update the embed to show the new member has accepted and add the member role

                await new_member.add_roles(
                    disnake.utils.get(inter.guild.roles, name=self.member_role),
                    reason="Accepted membership",
                )
                await new_member.remove_roles(
                    disnake.utils.get(inter.guild.roles, name=self.public_role),
                    reason="Accepted membership",
                )
                Embed.colour = disnake.Colour(1150720)
                Embed.description = f"{new_member.mention} has accepted membership!"
                Embed.remove_field(1)
                Embed.remove_field(0)
                Embed.set_footer(
                    text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}"
                )
                await inter.response.edit_message(embed=Embed, components=None)
                onboarding_channel = await dc.get_channel(
                    inter, channel_name=f"onboarding-{str(new_member.name).lower()}"
                )
                await onboarding_channel.delete()

                # announce the new member in the notification channel
                channel = disnake.utils.get(
                    inter.guild.channels, name=self.notification_channel
                )
                if channel is not None:
                    await channel.send(
                        embed=disnake.Embed(
                            title="New Member 🎉",
                            description=f"{new_member.mention} has completed the Introduction Module and is now a Member of The Freelancers Union!",
                            colour=disnake.Colour(14812691),
                        ).set_thumbnail(
                            file=disnake.File(fp="./assets/splash_art/fu/fu-logo.png")
                        )
                    )

            elif inter.component.custom_id == "rejected":
                # Update the embed to show the new member has declined.
                Embed.colour = disnake.Colour(14812691)
                Embed.description = f"{new_member.mention} has declined membership."
                Embed.remove_field(1)
                Embed.remove_field(0)
                Embed.set_footer(
                    text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}"
                )
                await new_member.add_roles(
                    disnake.utils.get(inter.guild.roles, name=self.guest_role),
                    reason="Rejected membership",
                )
                await new_member.remove_roles(
                    disnake.utils.get(inter.guild.roles, name=self.public_role),
                    reason="Rejected membership",
                )
                await inter.response.edit_message(embed=Embed, components=None)
                onboarding_channel = await dc.get_channel(
                    inter, channel_name=f"onboarding-{str(new_member.name).lower()}"
                )
                logging.info(
                    f"Deleting channel {onboarding_channel}\n{new_member.name}"
                )
                await onboarding_channel.delete()
        except Exception as e:
            logging.exception(e)
            await inter.send(
                embed=None,
                content="Something went wrong, you should check the user's roles",
                components=None,
            )


def setup(bot):
    bot.add_cog(OnboardA3Member(bot))
