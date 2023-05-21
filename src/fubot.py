from disnake.ext import commands
from census import Census, auraxium


class FUBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ps2_census_client: auraxium.Client = Census.get_client()
