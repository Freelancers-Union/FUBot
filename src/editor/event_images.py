import disnake
import re


# from editor.edit_events import EditorEventMenu, Event


class EditorEventImageMenu(disnake.ui.View):
    def __init__(self, parent):
        super().__init__(timeout=None)
        self.event = parent.event
        self.parent = parent
        self.selected_image_name: str = None
        self._regenerate_image_selector()

    def _regenerate_image_selector(self):
        self.selected_image_name = None
        self.children[0] = ImageSelector(parent=self, event=self.event, placeholder="Select image to delete")

    @disnake.ui.string_select()
    async def _placeholder(self):
        pass

    @disnake.ui.button(label="Delete Images", style=disnake.ButtonStyle.blurple, row=2)
    async def _event_edit_images_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.selected_image_name and self.selected_image_name in self.event.get_images().keys():
            self.event.delete_image(self.selected_image_name)
            content = None
        else:
            content = "No Image selected to delete!"
            self._regenerate_image_selector()
        await inter.response.edit_message(content=content, view=self)

    @disnake.ui.button(label="Add Image", style=disnake.ButtonStyle.blurple, row=3)
    async def _event_edit_add_image_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self._regenerate_image_selector()
        await inter.response.send_modal(modal=ImageAddModal(self))

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.blurple, row=4)
    async def _event_edit_back_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=self.parent)


class ImageSelector(disnake.ui.StringSelect):
    def __init__(self, parent: EditorEventImageMenu, event, placeholder: str = "Select image to delete"):
        self.parent = parent
        self.event = event
        options = list(self.event.get_images().keys())
        super().__init__(placeholder=placeholder, options=options, max_values=1)

    async def callback(self, inter: disnake.MessageInteraction):
        self.parent.selected_image_name = inter.values[0]
        self.placeholder = inter.values[0]
        # self._underlying.placeholder = inter.values[0]
        await inter.response.edit_message(view=self.parent)


class ImageAddModal(disnake.ui.Modal):
    def __init__(self, parent: EditorEventImageMenu):
        event = parent.event
        self.parent = parent
        title = "Add image to " + event.name
        # ACCEPTS ONLY TEXT INPUTS
        components = [
            disnake.ui.TextInput(
                label="Image Name",
                placeholder="Takes A-Z a-z 0-9 _",
                custom_id="image_name",
                style=disnake.TextInputStyle.short,
                max_length=50,
                required=True
            ),

            disnake.ui.TextInput(
                label="Link to image",
                placeholder="Required. Should start with https://",
                custom_id="image_url",
                style=disnake.TextInputStyle.short,
                required=True
            )
        ]
        super().__init__(title=title, components=components)

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        values = inter.text_values
        if re.fullmatch(r"^[a-zA-Z0-9_]+$", values["image_name"]) and values["image_url"].startswith("https://"):
            await inter.send(
                content="Adding this images URL to the list!\n" + "You can always delete it by deleting `" +
                        values["image_name"] + "` from the image dropdown\n" +
                        values["image_url"],
                ephemeral=True
            )
            self.parent.event.add_image(name=values["image_name"], url=values["image_url"])
        else:
            await inter.send(
                content="Sorry, but I dont think you read the gray text.\n Name or URL didn't look ok.\n" +
                        "Try again!",
                ephemeral=True,
                delete_after=10
            )

        await inter.response.edit_message(self.parent)
