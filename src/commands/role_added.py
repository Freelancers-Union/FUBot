# from datetime import datetime
# import disnake
# from beanie.operators import Push, Pull, ElemMatch
# from disnake.ext import commands

# from database.models.discord import DiscordUserRole
# from database.models.members import Member


# class MemberRoleUpdate(commands.Cog):
#     """
#     Triggers when a member role changes
#     """

#     def __init__(self,
#                  client: commands.Bot):
#         self.client = client

#     @commands.Cog.listener("on_member_update")
#     async def on_member_update(self, before: disnake.Member, after: disnake.Member):
#         """
#         listens for changes to members such as role change
#         If role is onboardable, DM onboarding message.
#         If a role is removed, remove from database
#         If a role is added, add to database

#         Parameters
#         ----------
#         before : class : disnake.Member before change
#         after : class : disnake.Member after change

#         """
#         # Check if the member has gained a role
#         if len(before.roles) < len(after.roles):
#             for gained in (set(before.roles) ^ set(after.roles)):
#                 await Member.find_one({Member.discord.id: before.id}).update(
#                     Push({
#                         Member.discord.roles: DiscordUserRole(
#                             id=gained.id, 
#                             name=gained.name, 
#                             added=datetime.utcnow()
#                         ),
#                     })
#                     )

#         # Check if the member has lost a role
#         elif len(before.roles) > len(after.roles):
#             for lost in (set(before.roles) ^ set(after.roles)):
#                 await Member.find_one({Member.discord.id: before.id}).update(
#                     Pull({Member.discord.roles: ElemMatch({"id": lost.id})})
#                     )


# def setup(client):
#     client.add_cog(MemberRoleUpdate(client))
