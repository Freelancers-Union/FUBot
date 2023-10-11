from aiocron import Cron
from fubot import FUBot
import logging
import commands.new_discord_members as new_discord_members


class CronJob:
    def __init__(self, expression, func=None, loop=None):
        Cron(expression, func=func, start=True, loop=loop)


def init_cron_jobs(bot: FUBot):
    """
    Initialize cron jobs
    """

    async def send_new_member_list():
        """
        Scheduled task to post new Discord members report.
        Cron: Every Friday at 1699 UTC
        """
        weekly_new_member_report = new_discord_members.NewDiscordMembers(bot)
        try:
            for guild in bot.guilds:
                await weekly_new_member_report.build_member_report(guild=guild)
        except Exception as e:
            logging.exception(e)

    loop = bot.loop
    CronJob(expression="1 17 * * 5", func=send_new_member_list, loop=loop)
