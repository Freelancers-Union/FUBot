from typing import List
import disnake
from disnake.ext import commands
from disnake.enums import ButtonStyle


class Menu(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed]):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.index = 0

        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            green_dots = "⚪️" * (i + 1)
            white_dots = "⚫️" * (len(self.embeds) - i - 1)
            embed.set_footer(text=f"{green_dots}{white_dots}\n\nIf this message stops responding, you can regenerate it using /intro")

        self._update_state()

    def _update_state(self) -> None:
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1

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

    # @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red)
    # async def remove(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
    #     await inter.response.edit_message(view=None)

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

class SendIntro(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def paginator(self):
        # Creates the embeds as a list.
        embeds = [
          disnake.Embed(
                title="Welcome to The Freelancers Union [FU]!",
                description="This message is a quick start guide to help you get the most out of what FU has to offer.\nUse the buttons below to navigate through the pages.\n\nIf you have any questions, feel free to ask in the [#general](https://discord.com/channels/282514718445273089/282514718445273089) channel.",
                colour=disnake.Colour(0),
            ).set_thumbnail(
              url="https://www.fugaming.org/uploads/1/3/0/9/130953309/editor/pslogo1417p.png?1617516785"
              ),

          disnake.Embed(
              title="Schedule",
              description="FU is mostly EU based, Prime Time for us is:\n<t:1669921200:t> - <t:1667340000:t>\n(Handily converted to your timezone!)\n\nWe run events almost everyday! Check the [#schedule](https://discord.com/channels/282514718445273089/539196000000000000/539196000000000000) channel for more info.",
              colour=disnake.Colour(1331732),
          ).set_thumbnail(
            url="https://emojipedia-us.s3.amazonaws.com/source/skype/289/calendar_1f4c5.png"
          ),

          disnake.Embed(
              title="Divisions",
              description="FU is sub-divided based on the main games we play, but you'll find the same FU ethos and playstyle throughout.\n:white_small_square: **PlanetSide 2**\n:white_small_square: **Arma 3**",
              colour=disnake.Colour(1997598),
          ).set_thumbnail(
            url="https://cdn.onlinewebfonts.com/svg/img_486271.png"
          ),

          disnake.Embed(
              title="Platforms",
              description="We use **Discord** as our main text forum, and **Teamspeak** for voice chat.",
              colour=disnake.Colour(2663464),
          ).set_thumbnail(
            url="https://logodownload.org/wp-content/uploads/2017/11/discord-logo-0-2048x2048.png"
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
                colour=disnake.Colour(3329330),
            ).set_thumbnail(
                url="https://cdn2.iconfinder.com/data/icons/business-rounded-3/512/xxx002-512.png"
            ),

          disnake.Embed(
              title="Community Leadership",
              description="*Leadership on a longer timespan*\n\n:white_small_square: **The Community**, with its sub-divisions, are led by **Officers**.\n:white_small_square: Officers cooperate to **create content** and **develop the community**. \n:white_small_square: An Officer contributes what is **within their reasonable limits**.\n:white_small_square: In you are interested to learn more about leadership contact Mordus#5149",
              colour=disnake.Colour(3329330),
          ).set_thumbnail(
            url="https://cdn2.iconfinder.com/data/icons/business-rounded-3/512/xxx002-512.png"
          ),

          disnake.Embed(
              title="Game Leadership",
              description="*Leadership on a short timespan*\n\n:white_small_square: **Game leadership** is **open to everyone**. It is not limited to Officers or even FU members.\n:white_small_square:  Whoever is the squad/platoon leader is the highest ranking in that context.\n:white_small_square: Your squad, your rules! \n:white_small_square:  The FU Ethos should always be followed.",
              colour=disnake.Colour(2017046),
          ).set_thumbnail(
            url="https://cdn2.iconfinder.com/data/icons/business-rounded-3/512/xxx002-512.png"
          ),

          disnake.Embed(
                title="The FU Ethos",
                description=">  It's just a game and the first rule of the game is to deny that it is a game because it is, in fact, not just a game.\n\n*The FU Ethos refers to implicitly held values on what is considered as good practise when playing together.*\n\nIn no specific order:\n\n:white_small_square: Welcome everyone! You are engaging with people, not numbers.\n:white_small_square: Do not use coercive methods to as a means to influence others.\n:white_small_square: It is voluntary to join an FU squad but if you do you commit to cooperate and follow the leaders instructions.\n:white_small_square: Our leadership ethos in FU is Service. A leader is there to provide the group and a direction for others to join.\n:white_small_square: Appreciate those who lead by the Ethos. Thank them for their effort when they step down. \n:white_small_square: Be mindful of how you speak of other players and groups. Maybe they cant hear you but we can.\n:white_small_square: Discuss problems but do not complain. Figure out improvements or ways to adapt.\nUse your initiative and step up when asked to volunteer.",
                colour=disnake.Colour(2357273),
            ).set_thumbnail(
                url="https://pngimg.com/uploads/scales/scales_PNG10.png"
            ),

          disnake.Embed(
              title="Membership",
              description="*FU membership means identifying with the goals and values of the community. \nBecoming a member is **your choice**, not something we need you to become.\nYou can still play with us without being a member.*\n\nTo become a member:\n:white_small_square: (Optional but recommended) Read the [Introduction](https://wiki.fugaming.org/intro-module) document on our Wiki\n:white_small_square: (1/2) Contact an Officer about an introduction meeting on TS\n:white_small_square: (2/2) Attend a scheduled introduction meeting. See [#schedule](https://discordapp.com/channels/282514718445273089/539192935258783744)\n:white_small_square: During the meeting the Officer will discuss any questions you have regarding FU (assuming you've read the intro document or played with us for some time)\n:white_small_square: You will be offered FU membership during the meeting which you can accept or reject. \n:white_small_square: If you reject membership you will be given Guest status on our discord and not notified again about introduction events. You may at any time ask for membership should you change your mind.\n\nMembership gives you the member rank in PlanetSide, the **[FU]** tag on TS and exclusive access to the Discord member's channel category. \n\n**Membership is completely optional**, accept if you wish to associate with the community and wear the **[FU]** tag.",
              colour=disnake.Colour(2357273),
          ).set_thumbnail(
            url="https://i.pinimg.com/originals/1a/a0/47/1aa04756777580a5328ad9f456c9dadb.png"
          ),
        ]
        return embeds

    @commands.Cog.listener()
    async def on_member_join(self, member):

        # Send a DM to the new member
        embeds = await self.paginator()
        await member.send(content=None, embed=embeds[0], view = Menu(embeds))

    @commands.slash_command(dm_permission=True)
    async def intro(self, inter):
        """
        Send a DM of the intro message
        """
        await inter.response.send_message("Sending intro message to DM...", ephemeral=True)
        embeds = await self.paginator()
        await inter.author.send(content=None, embed=embeds[0], view=Menu(embeds))


def setup(bot):
    bot.add_cog(SendIntro(bot))
