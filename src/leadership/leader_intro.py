import os
import logging
import datetime
from typing import List
import disnake
from disnake.ext import commands
from disnake.enums import ButtonStyle
import helpers.discord_checks as dc


class Menu(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed], member = disnake.Member):
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
            embed.set_footer(text=f"{white_dots}{black_dots}\n\nIf this message stops responding, you can regenerate it using /leadership in the FU server")

        self._update_state()

    def _update_state(self) -> None:
        # self.member.disabled = self.index != len(self.embeds) - 1
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1
        # if self.index == len(self.embeds) - 1 and self.requested is False:
        #     member_role = disnake.utils.get(self.guild_member.roles, name=self.member_role)
        #     if member_role is None:
        #         self.add_item(self.member)
        # else:
        #     self.remove_item(self.member)

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
    async def first_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index = 0
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index -= 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index += 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index = len(self.embeds) - 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    # async def notify_send(self,author=None):
    #     member_request = disnake.Embed(
    #           title=f"Membership Request - {author.name}",
    #           description="Please contact this player to get them onboard! :ship:",
    #           colour=disnake.Colour(14812691)
    #       ).add_field(
    #             name="User:",
    #             value=f"{author.mention}"
    #       )
    #     channel = disnake.utils.get(self.guild_member.guild.channels, name=self.notification_channel)
    #     if channel is not None:
    #         await channel.send(
    #         embed=member_request,
    #         components=[
    #         disnake.ui.Button(label="Assign to me", style=disnake.ButtonStyle.success, custom_id="assign")
    #     ],)


class LeaderIntro(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # self.member_role = "Member"
        # self.public_role = "Public player"
        # self.guest_role = "Guest"
        # self.notification_channel = "community-announcements"
        self.onboard_channel = None

    async def paginator(self):
        # Creates the embeds as a list.
        s3_assets = "https://fu-static-assets.s3.eu-west-1.amazonaws.com/intro-icons/"
        embeds = [
          disnake.Embed(
                title="Introduction",
                description=":stars: Welcome to the FU leadership development program! :stars:\n\n Leadership is a broad topic and can mean a lot of things and is a discipline that you can explore indefinitely!\nWe hope you will find interesting perspectives and inspiring challenges as we move forward!\nOur program is unique in its blend of opportunities by providing active practise through actually leading groups as well as in its continuous building of the very organization this program emerge within. You decide how you wish to participate!\n\nThe training program is built on several components:\n\n:white_small_square:**Active practice**\nThe most efficient learning will come from engaging in leadership during gameplay.\nAt more advanced levels you may be able to practice leadership on an organizational level as you build the actual community.\n\n:white_small_square:**Theory related to context**\nUnderlying theories and designs will be explained for different areas and layers of involvement depending on your own activity and initiative. We want to keep the information as relevant to your context as possible. Everything is accessible should you be interested to just study the material.\n\n:white_small_square:**Private mentoring and leadership channels**\nEach module will provide you an option to request a temporary private mentor channel where you can discuss the topics further with an experienced leader. There are also leadership channels where you can discuss topics together with the larger community.\n\n:white_small_square:**FU WIKI**\nFind all kind of information about FU and the games we play at https://wiki.fugaming.org/\n\n:white_small_square:**Bot systems**\nThe bots cover different topics. The system is non-linear and you can pick whatever topic you are interested in. The bots tie together the various sources of information and activities. Consider the bots as your AI assistants there to help you move forward!",
                colour=disnake.Colour(3092790),
            ).set_thumbnail(
              url="https://fu-static-assets.s3.eu-west-1.amazonaws.com/splash_art/fu/fu-logo.png"
              ),

          disnake.Embed(
              title="Why leadership?",
              description="We consider **leadership** to be an **extremely valuable skill** that can be applied in all areas of life. Our vision is to create the best possible gaming community where you can play and have fun while you simultaneously develop  a leadership skillset that is transferable.\n\n**Gaming is the perfect medium** to teach and practice leadership skills because:\n\n:white_small_square:**Information and opportunity** to develop is available to everyone regardless of background\n:white_small_square:**It is a safe and dynamic environment** in which to experiment, lead, learn and grow\n:white_small_square:**You will not be alone.** FU is not just a gaming community but a leader network. You will be joining a team of players supporting each other as we explore and learn more about leadership.",
              colour=disnake.Colour(4533298),
          ).set_thumbnail(
            url=f"{s3_assets}leadership.png"
          ),

          disnake.Embed(
              title="How do I get started?",
              description="Remember that at no point do we expect you to commit to anything you don't consider to be reasonable.\n\n**Ways to get started:**\n\n:white_small_square:**Opt in for our leadership program**\nIf you are reading these messages you have already opted in for the program through our leadership bots. :white_check_mark: \n\n:white_small_square:**Talk to an officer**\nUse our channels or send a dm to any of our officers and they will help you get started. Don't be shy, we really appreciate you reaching out! \n\n:white_small_square:**In-game leading** \nWhen you play games together with others in FU you will have the opportunity to lead groups. How often and to what length you lead is entirely up to you. You will never be required to lead. \n\n**The best way to get into a leader position is to:**\n - Attend FUEL events \n - Volunteer when we're asking for new leaders during leadership rotations\n - If you are bold, start your own squads \n \n See **basic in-game leadership program** for more information.\n\n:white_small_square:**FUEL** \nFU Emerging Leaders is an event where new leaders rotate to lead short segments while a veteran leader supports and mentors.\n\n:white_small_square:**Discussions and feedback**\nDiscuss leadership topics, give or ask for feedback from the players you engage with in our leadership channels.",
              colour=disnake.Colour(6039085),
          ),

          disnake.Embed(
              title="What are we building?",
              description=":white_small_square:**A leadership network**\nWe aim to spot leaders early on, give them support and agency to grow and connect with other leaders. We develop the individual, the group and the leadership ethos. \n\n:white_small_square:**Expertise in digital leadership**\nWe believe that leadership skills acquired through gaming and managing gaming networks are valuable. Our aim is to create more expertise and recognition for this. \n\n:white_small_square:**An awesome gaming community**\nWith focus on leadership development and support we create a great gaming environment where leadership is fun, engaging and something useful to take with you. Great leaders, great players and great gameplay!",
              colour=disnake.Colour(7479593),
              ),

          disnake.Embed(
                title="Next Steps",
                description="You can choose any of the following leadership programs or you can open up a private mentoring channel in which an officer will contact you to provide further assistance!\n\n:white_small_square:**Mentor channel** (opens up a temporary private channel request)\n:white_small_square:**Metrics** (Allows you to create a profile that tracks whatever metrics are available)\n:white_small_square:**Self leadership program** (another bot that goes through personality profiles, vision building and goal setting) \n:white_small_square:**Basic in-game leadership** (FU leadership methodology on a basic level applicable to all games)\n:white_small_square:**FU leadership Ethos** (more FU leadership values and philosophies)",
                colour=disnake.Colour(8985637),
            ),
        ]
        return embeds

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     """
    #     Send a DM of the intro message
    #     """
    #     embeds = await self.paginator()
    #     await member.send(content=None, embed=embeds[0], view=Menu(embeds=embeds, member=member))

    @commands.slash_command(dm_permission=True)
    async def leadership(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        pass
    @leadership.sub_command()
    async def intro(self, inter):
        """
        Send a DM of the intro message
        """
        await inter.response.send_message("Check your DMs!", ephemeral=True)
        embeds = await self.paginator()
        await inter.author.send(content=None, embed=embeds[0], view=Menu(embeds=embeds, member=inter.author))

    # @commands.Cog.listener("on_button_click")
    # async def onboard_listener(self, inter: disnake.MessageInteraction):
    #     """
    #     Onboarding listener
    #         Handles the onboarding task message in Officer chat.

    #     Args:
    #         inter (disnake.MessageInteraction): The interaction

    #     Returns:
    #         None
    #     """
    #     try:
    #         if inter.component.custom_id not in ["assign", "accepted", "rejected"]:
    #             return
    #         Embed = inter.message.embeds[0]
    #         new_member = inter.guild.get_member(int(Embed.fields[0].value[2:-1]))

    #         if inter.component.custom_id == "assign":

    #             # Create a private channel for the new member and the officer
    #             overwrites = {
    #                 inter.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
    #                 new_member: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    #                 inter.author: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    #                 self.bot.user: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, manage_messages=True)
    #             }
    #             self.onboard_channel = await inter.guild.create_text_channel(name=f"onboarding-{new_member.name}",overwrites=overwrites)
    #             for member in [new_member, inter.author]:
    #                 await self.onboard_channel.set_permissions(
    #                                                     target=member,
    #                                                     view_channel=True,
    #                                                     send_messages=True,
    #                                                     read_message_history=True,
    #                                                     )

    #             # Update the embed to show the new member has been assigned to an officer
    #             Embed.description = f"Created private channel: {self.onboard_channel.mention}\nChannel will self-destruct once onboarding is complete."
    #             Embed.add_field(
    #                 name="Assigned To:",
    #                 value=f"{inter.author.mention}",
    #                 inline=False
    #             ).set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}")
    #             Embed.colour = disnake.Colour(12757760)
    #             await inter.response.edit_message(embed=Embed, components=[
    #             disnake.ui.Button(label="Accepted", style=disnake.ButtonStyle.green, custom_id="accepted"),
    #             disnake.ui.Button(label="Rejected", style=disnake.ButtonStyle.red, custom_id="rejected")
    #         ])

    #         elif inter.component.custom_id == "accepted":
    #             # Update the embed to show the new member has accepted and add the member role
                
    #             await new_member.add_roles(disnake.utils.get(inter.guild.roles, name=self.member_role),
    #                                     reason="Accepted membership")
    #             await new_member.remove_roles(disnake.utils.get(inter.guild.roles, name=self.public_role),
    #                                     reason="Accepted membership")
    #             Embed.colour = disnake.Colour(1150720)
    #             Embed.description = f"{new_member.mention} has accepted membership!"
    #             Embed.remove_field(1)
    #             Embed.remove_field(0)
    #             Embed.set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}")
    #             await inter.response.edit_message(embed=Embed, components=None)
    #             await self.onboard_channel.delete()

    #             # announce the new member in the notification channel
    #             channel = disnake.utils.get(inter.guild.channels, name=self.notification_channel)
    #             if channel is not None:
    #                 await channel.send(
    #                 embed=disnake.Embed(
    #                     title="New Member 🎉",
    #                     description=f"{new_member.mention} has completed the Introduction Module and is now a Member of The Freelancers Union!",
    #                     colour=disnake.Colour(14812691)
    #                 ).set_thumbnail(
    #                     file=disnake.File(fp="./assets/splash_art/fu/fu-logo.png")
    #                 ))

    #         elif inter.component.custom_id == "rejected":
    #             # Update the embed to show the new member has declined.
    #             Embed.colour = disnake.Colour(14812691)
    #             Embed.description = f"{new_member.mention} has declined membership."
    #             Embed.remove_field(1)
    #             Embed.remove_field(0)
    #             Embed.set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}")
    #             await new_member.add_roles(disnake.utils.get(inter.guild.roles, name=self.guest_role),
    #                                     reason="Rejected membership")
    #             await new_member.remove_roles(disnake.utils.get(inter.guild.roles, name=self.public_role),
    #                                     reason="Rejected membership")
    #             await inter.response.edit_message(embed=Embed, components=None)
    #             await self.onboard_channel.delete()
    #     except Exception as e:
    #         logging.exception(e)
    #         await inter.send(embed=None, content="Something went wrong, you should check the user's roles", components=None)

def setup(bot):
    bot.add_cog(LeaderIntro(bot))
