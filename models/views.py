import discord
from discord.ui import Button
from discord.ui import View
from discord import Embed
from discord.ui import Select
from agents import DnDUtilityAgent


class DnDView(View):
    def __init__(self, description):
        self.description = description
        self.embed = Embed(title='Prompt for DND master', colour=discord.Colour.green(),
                           description=self.description)
        self.dnd_utility_agent = DnDUtilityAgent()
        self.accept_button = Button(label='Accept', style=discord.ButtonStyle.green)
        self.accept_button.callback = self.accept_button_callback
        self.accept_button.disabled = True
        self.new_button = Button(label='New', style=discord.ButtonStyle.gray, emoji='🔁')
        self.new_button.callback = self.new_button_callback
        self.modal = PromptModal(view=self)
        super().__init__(self.accept_button, self.new_button)

    async def accept_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # await self.accept_prompt()
        await self.update_message(interaction)

    async def new_button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.embed, view=self)

    def update_embed(self, new_description):
        self.description = new_description
        self.accept_button.disabled = False
        self.new_button.disabled = False
        self.embed = self.construct_embed(new_description)

    def construct_embed(self, new_description):
        self.embed = Embed(title='Prompt for DND master', colour=discord.Colour.green(),
                           description=new_description)


class PromptModal(discord.ui.Modal):
    def __init__(self, view) -> None:
        super().__init__(title='New theme')
        self.view: DnDView = view
        self.add_item(discord.ui.InputText(label="New theme for the prompt", placeholder="For ex. Zombies in New york"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        new_description = await self.view.dnd_utility_agent.run(themes=self.children[0].value)
        self.view.update_embed(new_description)
        await self.view.update_message(interaction)