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
            embed.set_footer(text=f"{white_dots}{black_dots}\n\nIf this message stops responding, you can regenerate it using /intro in the FU server")

        self._update_state()

    def _update_state(self) -> None:
        # self.member.disabled = self.index != len(self.embeds) - 1
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1
        if self.index == len(self.embeds) - 1 and self.requested is False:
            member_role = disnake.utils.get(self.guild_member.roles, name=self.member_role)
            if member_role is None:
                self.add_item(self.member)
        else:
            self.remove_item(self.member)

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

    @disnake.ui.button(label="Membership", style=disnake.ButtonStyle.green)
    async def member(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
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
    async def next_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index += 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index = len(self.embeds) - 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    async def notify_send(self,author=None):
        member_request = disnake.Embed(
              title="Membership Request <:fu:914187604168171581>",
              description="Please contact this player to get them onboard! :ship:",
              colour=disnake.Colour(14812691)
          ).add_field(
                name="User:",
                value=f"{author.mention}"
          )
        channel = disnake.utils.get(self.guild_member.guild.channels, name=self.notification_channel)
        if channel is not None:
            await channel.send(
            embed=member_request,
            components=[
            disnake.ui.Button(label="Assign to me", style=disnake.ButtonStyle.success, custom_id="assign")
        ],)


class SendIntro(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.member_role = "Member"

    async def paginator(self):
        # Creates the embeds as a list.
        embeds = [
          disnake.Embed(
                title="Welcome to The Freelancers Union [FU]!",
                description="This message is a quick start guide to help you get the most out of what FU has to offer.\nUse the buttons below to navigate through the pages.\n\nIf you have any questions, feel free to ask in the [#general](https://discord.com/channels/282514718445273089/282514718445273089) channel.",
                colour=disnake.Colour(3092790),
            ).set_thumbnail(
              url="https://cdn.discordapp.com/attachments/986678839008690176/1071460285170327572/01-logo.png"
              ),

          disnake.Embed(
              title="Schedule",
              description="FU is mostly EU based, Prime Time for us is:\n<t:1669921200:t> - <t:1667340000:t>\n(Handily converted to your timezone!)\n\nWe run events almost everyday! Check the [#schedule](https://discord.com/channels/282514718445273089/539196000000000000/539196000000000000) channel for more info.",
              colour=disnake.Colour(4533298),
          ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/986678839008690176/1071460285430366249/02-schedule.png"
          ),

          disnake.Embed(
              title="Divisions",
              description="FU is sub-divided based on the main games we play, but you'll find the same FU ethos and playstyle throughout.\n:white_small_square: **PlanetSide 2**\n:white_small_square: **Arma 3**",
              colour=disnake.Colour(6039085),
          ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/986678839008690176/1071460285736558735/03-divs.png"
          ),

          disnake.Embed(
              title="Platforms",
              description="We use **Discord** as our main text forum, and **Teamspeak** for voice chat.",
              colour=disnake.Colour(7479593),
          ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/986678839008690176/1071460286009200650/04-discord.png"
            ).add_field(
              name="Discord",
              value="Discord is our main hub for chatting outside of games. Meet the community, grab roles for the games you want to play, and chat with fellow players in  the divisional channels:\n> [#role-menu](https://discordapp.com/channels/282514718445273089/983432774935531551)\n> [#ps2-general](https://discord.com/channels/282514718445273089/290929845788213249)\n> [#a3-general](https://discord.com/channels/282514718445273089/531220605391994892)\n** **",
              inline=False
              ).add_field(
                name="Teamspeak",
                value="TeamSpeak is our main voice platform and the perfect place to get to know the community. With it, you'll be able to communicate with your teammates, plan strategy, and make new friends. \n\nDownload it for free: [Download TeamSpeak3](https://www.teamspeak.com/en/downloads/)\n```\nServer: ts.fugaming.org \nPassword: futs\n```",
                inline=False
              ),

          disnake.Embed(
                title="Leadership",
                description="There are two main categories of leadership in FU: \n:white_small_square: **Community Leadership**\n:white_small_square: **Game Leadership**\n(*they are similar but not the same*)",
                colour=disnake.Colour(8985637),
            ).set_thumbnail(
                url="https://cdn.discordapp.com/attachments/986678839008690176/1071460286269227068/05-leadership.png"
            ),

          disnake.Embed(
              title="Community Leadership",
              description="*Leadership on a longer timespan*\n\n:white_small_square: **The Community**, with its sub-divisions, are led by **Officers**.\n:white_small_square: Officers cooperate to **create content** and **develop the community**. \n:white_small_square: An Officer contributes what is **within their reasonable limits**.\n:white_small_square: In you are interested to learn more about leadership contact Mordus#5149",
              colour=disnake.Colour(10425888),
          ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/986678839008690176/1071460286269227068/05-leadership.png"
          ),

          disnake.Embed(
              title="Game Leadership",
              description="*Leadership on a short timespan*\n\n:white_small_square: **Game leadership** is **open to everyone**. It is not limited to Officers or even FU members.\n:white_small_square:  Whoever is the squad/platoon leader is the highest ranking in that context.\n:white_small_square: Your squad, your rules! \n:white_small_square:  The FU Ethos should always be followed.",
              colour=disnake.Colour(11866396),
          ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/986678839008690176/1071460286269227068/05-leadership.png"
          ),

          disnake.Embed(
                title="The FU Ethos",
                description=">  It's just a game and the first rule of the game is to deny that it is a game because it is, in fact, not just a game.\n\n*The FU Ethos refers to implicitly held values on what is considered as good practise when playing together.*\n\nIn no specific order:\n\n:white_small_square: Welcome everyone! You are engaging with people, not numbers.\n:white_small_square: Do not use coercive methods to as a means to influence others.\n:white_small_square: It is voluntary to join an FU squad but if you do you commit to cooperate and follow the leaders instructions.\n:white_small_square: Our leadership ethos in FU is Service. A leader is there to provide the group and a direction for others to join.\n:white_small_square: Appreciate those who lead by the Ethos. Thank them for their effort when they step down. \n:white_small_square: Be mindful of how you speak of other players and groups. Maybe they cant hear you but we can.\n:white_small_square: Discuss problems but do not complain. Figure out improvements or ways to adapt.\nUse your initiative and step up when asked to volunteer.",
                colour=disnake.Colour(13372183),
            ).set_thumbnail(
                url="https://cdn.discordapp.com/attachments/986678839008690176/1071460286516699226/08-ethos.png"
            ),

          disnake.Embed(
              title="Membership",
              description="*FU membership means identifying with the goals and values of the community. \nBecoming a member is **your choice**, not something we need you to become.\nYou can still play with us without being a member.*\n\nMembership gives you the member rank in PlanetSide, the **[FU]** tag on TS and exclusive access to Member only events and the Discord member's channels. \n\n**To become a member:**\n:white_small_square: (Optional but recommended) Read the [**Introduction**](https://wiki.fugaming.org/intro-module) document on our Wiki\n:white_small_square: Click the **Membership** button at the bottom of this message.\n\nIf you don't want membership right now you will be given Guest status on our discord and not notified again about introduction events. \nYou may at any time ask for membership should you change your mind.",
              colour=disnake.Colour(14812691),
          ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/986678839008690176/1071460284922855444/09-membership.png"
          ),
        ]
        return embeds

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Send a DM of the intro message
        """
        embeds = await self.paginator()
        await member.send(content=None, embed=embeds[0], view=Menu(embeds=embeds, member=member))

    @commands.slash_command(dm_permission=False)
    async def intro(self, inter):
        """
        Send a DM of the intro message
        """
        await inter.response.send_message("Check your DMs!", ephemeral=True)
        embeds = await self.paginator()
        await inter.author.send(content=None, embed=embeds[0], view=Menu(embeds=embeds, member=inter.author))

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

        if inter.component.custom_id not in ["assign", "accepted", "rejected"]:
            return
        Embed = inter.message.embeds[0]

        if inter.component.custom_id == "assign":
            # Update the embed to show the new member has been assigned to an officer
            Embed.add_field(
                name="Assigned To:",
                value=f"{inter.author.mention}",
                inline=False
            ).set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}")
            Embed.colour = disnake.Colour(12757760)
            if inter.component.custom_id == "assign":
                await inter.response.edit_message(embed=Embed, components=[
                disnake.ui.Button(label="Accepted", style=disnake.ButtonStyle.green, custom_id="accepted"),
                disnake.ui.Button(label="Rejected", style=disnake.ButtonStyle.red, custom_id="rejected")
            ])

        elif inter.component.custom_id == "accepted":
            # Update the embed to show the new member has accepted and add the member role
            new_member = inter.guild.get_member(int(inter.message.embeds[0].fields[0].value[2:-1]))
            await new_member.add_roles(disnake.utils.get(inter.guild.roles, name=self.member_role),
                                       reason="Accepted membership")
            Embed.colour = disnake.Colour(1150720)
            Embed.description = f"{new_member.mention} has accepted membership!"
            Embed.remove_field(1)
            Embed.remove_field(0)
            Embed.set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}")
            await inter.response.edit_message(embed=Embed, components=None)

        elif inter.component.custom_id == "rejected":
            # Update the embed to show the new member has declined.
            new_member = inter.guild.get_member(int(inter.message.embeds[0].fields[0].value[2:-1]))
            Embed.colour = disnake.Colour(14812691)
            Embed.description = f"{new_member.mention} has declined membership."
            Embed.remove_field(1)
            Embed.remove_field(0)
            Embed.set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%d/%m %H:%M')}")
            await inter.response.edit_message(embed=Embed, components=None)

def setup(bot):
    bot.add_cog(SendIntro(bot))
