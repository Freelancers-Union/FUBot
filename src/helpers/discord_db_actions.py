from datetime import datetime
import logging
from database_connector import Database

class DiscordDB(object):
    """
    Class for handling discord database actions

    """

    DB = Database.DATABASE
    COLLECTION = DB["members"]

    @staticmethod
    async def add_role(role, member):
        """
        Adds a role to a member

        Parameters
        ----------
        role : class : disnake.Role
        member : class : disnake.Member

        """
        try:
            logging.info(f"Discord : Adding role {role.name} to {member.name}")
            DiscordDB.COLLECTION.update_one({'discord_user.id': str(member.id)}, {
                '$push': {'discord_user.roles': {
                    "role": role.name,
                    "timestamp": datetime.utcnow()
                    }}
                })
            return True
        except Exception as e:
            logging.error(f"Discord : Error adding role {role.name} to {member.name} : {e}")
            raise e


    @staticmethod
    async def remove_role(role, member):
        """
        Removes a role from a member

        Parameters
        ----------
        role : class : disnake.Role
        member : class : disnake.Member

        """
        try:
            logging.info(f"Discord : Removing role {role.name} from {member.name}")
            DiscordDB.COLLECTION.update_one({'discord_user.id': str(member.id)}, {
                '$pull': {'discord_user.roles': {"role": role.name}}
            })
            return True
        except Exception as e:
            logging.error(f"Discord : Error removing role {role.name} from {member.name} : {e}")
            raise e