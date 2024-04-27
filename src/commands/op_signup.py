import os
import re
import logging
from typing import Union

import disnake
from disnake.ext import commands

user_playstyle = None  # This could be None if no preference has been set

class CharacterNameModal(disnake.ui.Modal):
    def __init__(self, view):
        self.view = view
        text_input = disnake.ui.TextInput(
            label="Character Name",
            custom_id="character_name",
            placeholder="Enter your character name here...",
            min_length=3,
            max_length=20,
        )
        action_row = disnake.ui.ActionRow(text_input)
        super().__init__(title="Enter Character Name", components=[action_row])

    async def callback(self, inter: disnake.ModalInteraction):
        # Save the character name to the view
        self.view.character_name = inter.text_values["character_name"]
        await inter.response.send_message("Select your playstyle and class:", view=self.view, ephemeral=True)


class Playstyle(disnake.ui.Select):
    def __init__(self, parent):
        self.parent = parent
        options = [
            disnake.SelectOption(label="Infantry", emoji="<:infantry:1233791815891812455>"),
            disnake.SelectOption(label="Vehicles", emoji="<:vehicles:1233791864361189437>"),
            disnake.SelectOption(label="Air", emoji="<:air:1233791904299221033>"),
        ]

        super().__init__(placeholder="Choose your preferred playstyle...", options=options, min_values=1, max_values=3)

    async def callback(self, inter: disnake.Interaction):
        self.parent.playstyle = self.values
        await inter.response.defer()


class Infantry(disnake.ui.StringSelect):
    def __init__(self, parent):
        self.parent = parent  # Reference to the DropdownView to store selections
        options = [
            disnake.SelectOption(label="Medic", emoji="<:infantry:1233791815891812455>"),
            disnake.SelectOption(label="Heavy Assault", emoji="<:heavy:1233794699186274424>"),
            disnake.SelectOption(label="Light Assault", emoji="<:light_assault:1233794798121517197>"),
            disnake.SelectOption(label="Engineer", emoji="<:engineer:1233794729091665920>"),
            disnake.SelectOption(label="Max", emoji="<:max:1233794845953359892>"),
            disnake.SelectOption(label="Infiltrator", emoji="<:infil:1233794765066338396>")
        ]
        super().__init__(placeholder="Select Infantry Classes...",
                         min_values=1, max_values=6, options=options)

    async def callback(self, inter: disnake.MessageInteraction):
        self.parent.infantry_selection = self.values
        await inter.response.defer()


class Vehicles(disnake.ui.StringSelect):
    def __init__(self, parent):
        self.parent = parent  # Reference to the DropdownView to store selections
        options = [
            disnake.SelectOption(label="Prowler", emoji="<:infantry:1233791815891812455>"),
            disnake.SelectOption(label="Lightning", emoji="<:heavy:1233794699186274424>"),
            disnake.SelectOption(label="Ant", emoji="<:light_assault:1233794798121517197>"),
            disnake.SelectOption(label="Harasser", emoji="<:engineer:1233794729091665920>"),
            disnake.SelectOption(label="Chimera", emoji="<:infil:1233794765066338396>")
        ]
        super().__init__(placeholder="Select Vehicles...",
                         min_values=1, max_values=5, options=options)

    async def callback(self, inter: disnake.MessageInteraction):
        self.parent.vehicle_selection = self.values
        await inter.response.defer()


class Aircraft(disnake.ui.StringSelect):
    def __init__(self, parent):
        self.parent = parent  # Reference to the DropdownView to store selections
        options = [
            disnake.SelectOption(label="Mosquito", emoji="<:infantry:1233791815891812455>"),
            disnake.SelectOption(label="Valkyrie", emoji="<:heavy:1233794699186274424>"),
            disnake.SelectOption(label="Galaxy", emoji="<:light_assault:1233794798121517197>"),
            disnake.SelectOption(label="Liberator", emoji="<:engineer:1233794729091665920>"),
            disnake.SelectOption(label="Dervish", emoji="<:infil:1233794765066338396>")
        ]
        super().__init__(placeholder="Select Aircraft...",
                         min_values=1, max_values=5, options=options)

    async def callback(self, inter: disnake.MessageInteraction):
        self.parent.aircraft_selection = self.values
        await inter.response.defer()


class SubmitButton(disnake.ui.Button):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(label="Submit", style=disnake.ButtonStyle.green)

    def embed_builder(self):
        playstyle = self.parent.playstyle or 'No playstyle selected'
        infantry_selection = self.parent.infantry_selection or 'No infantry selected'
        vehicle_selection = self.parent.vehicle_selection or 'No vehicle selected'
        aircraft_selection = self.parent.aircraft_selection or 'No aircraft selected'
        character_name = self.parent.character_name or 'No name entered'
        embed = disnake.Embed(title="Preferences", color=disnake.Color.green())
        embed.add_field(name="Character Name", value=character_name, inline=False)
        embed.add_field(name="Playstyles", value=playstyle, inline=False)
        embed.add_field(name="Infantry", value=infantry_selection, inline=False)
        embed.add_field(name="Vehicles", value=vehicle_selection, inline=False)
        embed.add_field(name="Aircraft", value=aircraft_selection, inline=False)
        return embed

    async def callback(self, inter: disnake.Interaction):
        await inter.response.send_message(embed=self.embed_builder(), ephemeral=True)

class DropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.character_name = None
        self.playstyle = None
        self.infantry_selection = None
        self.vehicle_selection = None
        self.aircraft_selection = None
        self.add_item(Playstyle(self))
        self.add_item(Infantry(self))
        self.add_item(Vehicles(self))
        self.add_item(Aircraft(self))
        self.add_item(SubmitButton(self))

class Ps2Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def ps2_op_preferences(self, inter: disnake.CommandInteraction):
        # Trigger the modal for character name first
        modal = CharacterNameModal(DropdownView())
        await inter.response.send_modal(modal)

def setup(bot: commands.Bot):
    bot.add_cog(Ps2Preferences(bot))
