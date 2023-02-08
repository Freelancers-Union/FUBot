import disnake
from disnake.ext import commands
from editor.edit_events import EditorEventMenu, event_list, EditorEventModal


class EditorMenu(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # self.selected_channel = None
        self.selected_event_name = None

    @disnake.ui.string_select(
        placeholder="Event to edit",
        options=[event.name for event in event_list],
        max_values=1
    )
    async def event_selector(self, selector: disnake.ui.StringSelect, inter: disnake.MessageInteraction):
        await inter.response.edit_message(
            view=EditorEventMenu(parent_view=self, guild=inter.guild, event_name=selector.values[0])
        )

    @disnake.ui.button(label="New Event", style=disnake.ButtonStyle.blurple)
    async def _new_event(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(
            view=EditorEventMenu(parent_view=self, guild=inter.guild, event_name=self.selected_event_name)
        )


class Editor(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed = disnake.Embed(
            title="Choose what do you wish to edit",
            description="you have 15 minutes to work on each page or I may become bored and disappear"
        )

    @commands.slash_command(dm_permission=True)
    async def edit(self, inter: disnake.ApplicationCommandInteraction):
        """
        edit stuff
        """
        await inter.response.send_message(embed=self.embed, view=EditorMenu(), ephemeral=True)

# def setup(bot):
#     bot.add_cog(Editor(bot))
