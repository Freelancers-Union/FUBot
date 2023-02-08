import copy
import disnake
from editor.event_images import EditorEventImageMenu


class Event:
    def __init__(
            self,
            event_id,
            guild_id: int,
            name: str,
            title_name: str,
            channel_id: int,
            ping_role_list: [int],
            game: str = None,
            # ts_channel: str = None,
            description: str = None,
            secondary_tite: str = None,
            secondary_text: str = None,
            embed_side_colour: int = None,
            time_to_show: int = None,
            image_urls: dict[str:str] = None
    ):
        self.guild_id: int = guild_id
        self.name: str = name
        self.title_name: str = title_name
        self.channel_id: int = channel_id
        self.ping_role_list: [int] = ping_role_list
        self.game: str = game
        # self.ts_channel: str = ts_channel
        self.secondary_text: str = secondary_text
        self.secondary_tite: str = secondary_tite
        self.description: str = description
        self.embed_side_colour: int = embed_side_colour
        self.time_to_show: int = time_to_show
        self._image_urls: dict[str:str] = image_urls

    def add_image(self, name: str, url: str):
        """
        Saves image in DB for this event
        """
        self._image_urls[name] = url

    def get_images(self) -> dict[str:str]:
        """
        Reads the list of images from DB
        Returns
        -------
            Returns a dictionary in style {name: URL}
        """
        return self._image_urls
        # return tmp

    def delete_image(self, name):
        """
        Deletes image with :name:
        """
        self._image_urls.pop(name)


event_list = [
    Event(
        event_id=123123123123,
        guild_id=1111111111,
        name="1sad",
        title_name="1ttttt",
        channel_id=986317590811017268,
        ping_role_list=[914188301764812820, 991046923647606864],
        image_urls={
            "BadMen": "https://media.discordapp.net/attachments/986317590811017268/1068251636209823824/HUNTSMEN.png",
            "FUEL": "https://media.discordapp.net/attachments/993193764095017030/1054469214150344714/FU_Feed_4.png"
        }
    ),
    Event(
        event_id=2222222222222,
        guild_id=1111111111,
        name="1rsad",
        title_name="1ttttt",
        channel_id=986317590811017268,
        ping_role_list=[914188301764812820, 991046923647606864]
    ), Event(
        event_id=3333333333333333333,
        guild_id=1111111111,
        name="2sad",
        title_name="2tttt",
        channel_id=986317590811017268,
        ping_role_list=[914188301764812820, 991046923647606864]
    )
]


class EditorEventMenu(disnake.ui.View):
        # return self._image_urls
    def __init__(self, parent_view, guild: disnake.Guild, event_name: str = None):
        super().__init__(timeout=None)
        self.parent_view = parent_view
        self.guild = guild
        self.value_container = []
        event = None
        for _event in event_list:
            if _event.name == event_name:
                event = _event
        self.event = copy.copy(event)
        pass

    @disnake.ui.role_select(row=0)
    async def _event_editor_role_select(self, role_select: disnake.ui.RoleSelect, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=self)

    @disnake.ui.channel_select(min_values=1, row=1)
    async def _event_editor_chanel_select(self, channel_select: disnake.ui.ChannelSelect,
                                          inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=self)

    @disnake.ui.button(label="Edit Text", style=disnake.ButtonStyle.blurple, row=2)
    async def _event_edit_text_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=EditorEventModal(parent=self))

    @disnake.ui.button(label="Edit Images", style=disnake.ButtonStyle.blurple, row=2)
    async def _event_edit_images_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = EditorEventImageMenu(parent=self)
        await inter.response.edit_message(view=view)

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.blurple, row=4)
    async def _event_edit_back_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=self.parent_view)


class EditorEventModal(disnake.ui.Modal):
    def __init__(self, parent: EditorEventMenu):
        # self.parent_view = parent_view
        event = parent.event
        self.parent = parent
        title = "Edit " + event.name if event else "Create Event"
        # The details of the modal, and its components
        components = [
            disnake.ui.TextInput(
                label="* Event name (used in /announce `name`)",
                placeholder="Required",
                custom_id="name",
                value=event.name if event else None,
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Default Title",
                placeholder="Required",
                custom_id="title_name",
                value=event.title_name if event else None,
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="(opt) Description",
                placeholder=" (optional) Description",
                custom_id="description",
                value=event.description if event else None,
                style=disnake.TextInputStyle.paragraph,
                required=False
            ),
            disnake.ui.TextInput(
                label="(opt) Secondary title",
                placeholder="(optional) small, bold letters",
                custom_id="secondary_tite",
                value=event.secondary_tite if event else None,
                style=disnake.TextInputStyle.short,
                required=False,
                max_length=100,
            ),
            disnake.ui.TextInput(
                label="(opt) Secondary text",
                placeholder="(optional)",
                custom_id="secondary_text",
                value=event.secondary_text if event else None,
                style=disnake.TextInputStyle.paragraph,
                required=False
            )
        ]
        super().__init__(title=title, components=components)

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        values = inter.text_values
        event = self.parent.event
        event.name = values["name"]
        event.title_name = values["title_name"]
        event.description = values["description"]
        event.secondary_tite = values["secondary_tite"]
        event.secondary_text = values["secondary_text"]
        await inter.response.edit_message(self.parent)
