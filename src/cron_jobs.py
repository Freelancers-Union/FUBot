from aiocron import Cron
from fubot import FUBot
import logging
import commands.new_discord_members as new_discord_members


class CronJob:
    def __init__(self, expression, func=None):
        Cron(expression, func=func, start=True)


def init_cron_jobs(bot: FUBot):
    """
    Initialize cron jobs
    """

    async def send_new_member_list():
        """
        Scheduled task to post new Discord members report.
        Cron: Every Friday at 1700 UTC
        """
        weekly_new_member_report = new_discord_members.NewDiscordMembers(bot)
        try:
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    if str(channel) == "officers":
                        await channel.send(
                            embed=await weekly_new_member_report.build_member_report(
                                guild=guild
                            )
                        )
                        return
        except Exception as e:
            logging.exception(e)

    loop = bot.loop
    CronJob(expression="0 17 * * 5", func=send_new_member_list)
