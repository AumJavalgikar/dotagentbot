import discord
from discord.ui import Button, View, Select
from discord import Embed, TextChannel, Thread
from discord.ui import Select
from agents import DnDUtilityAgent, DnDAgent
from models.custom_bot import DiscordBot
from dotagent.memory import SummaryMemory
import re
from typing import List


class DnDUtilityView(View):
    def __init__(self, description, bot):
        self.bot: DiscordBot = bot

        self.description = description
        self.title = None
        self.themes = None

        self.classes: List[CharacterClass] = []
        self.races: List[CharacterClass] = []
        self.areas: List[CharacterClass] = []

        self.chosen_class = None
        self.chosen_race = None
        self.chosen_area = None


        self.final_description = None
        self.final_title = None
        self.final_class = None
        self.final_race = None

        self.embed = Embed(title='Prompt for DND master', colour=discord.Colour.green(),
                           description=self.description)

        self.dnd_utility_agent = DnDUtilityAgent()

        self.accept_button = Button(label='Accept', style=discord.ButtonStyle.green)
        self.accept_button.callback = self.accept_button_callback
        self.accept_button.disabled = True

        self.new_button = Button(label='New', style=discord.ButtonStyle.gray, emoji='🔁')
        self.new_button.callback = self.new_button_callback

        self.modal = PromptModal(view=self)

        self.class_select_menu = Select()
        self.race_select_menu = Select()
        self.area_select_menu = Select()

        self.class_select_menu.callback = self.class_select_callback
        self.race_select_menu.callback = self.race_select_callback
        self.area_select_menu.callback = self.area_select_callback

        super().__init__(self.accept_button, self.new_button)

    async def accept_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.final_description is None:
            self.final_description = self.description
            self.final_title = self.title
            await self.create_class_view(interaction)

        elif self.final_class is None:
            self.final_class = self.chosen_class
            await self.create_race_view(interaction)

        elif self.final_race is None:
            self.final_race = self.chosen_race
            await self.create_area_view(interaction)

        # message = await interaction.original_response()
        # await message.delete()
        # channel: TextChannel = interaction.channel
        # thread = await channel.create_thread(name=self.title, type=discord.ChannelType.public_thread)
        # await thread.add_user(interaction.user)
        # dnd_agent = DnDAgent(system_prompt=self.description, memory=SummaryMemory())
        # self.bot.dnd_threads.append(thread.id)
        # self.bot.dnd_clients[thread.id] = dnd_agent
        # followup = await dnd_agent.run(player_choice='Begin Journey')
        # view = DnDView(followup=followup, title=self.title, dnd_agent=dnd_agent)
        # await thread.send(embed=view.embed, view=view)

    async def class_select_callback(self, interaction: discord.Interaction):
        chosen_value = self.class_select_menu.values[0]
        char_class = [char_class for char_class in self.classes if char_class.name == chosen_value][0]
        self.update_description(new_description=f'Class title : **{char_class.name}**\n\n'
                                                f'Class description : \n{char_class.description}\n\n'
                                                f'Click **Accept** to choose the {char_class.name} class',
                                title='Select a class for your character!')
        self.chosen_class = chosen_value
        await interaction.response.edit_message(embed=self.embed, view=self)


    async def race_select_callback(self, interaction: discord.Interaction):
        chosen_value = self.race_select_menu.values[0]
        char_class = [char_class for char_class in self.races if char_class.name == chosen_value][0]
        self.update_description(new_description=f'Race title : **{char_class.name}**\n\n'
                                                f'Race description : \n{char_class.description}\n\n'
                                                f'Click **Accept** to choose the {char_class.name} race',
                                title='Select a race for your character!')
        self.chosen_race = chosen_value
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def area_select_callback(self, interaction: discord.Interaction):
        chosen_value = self.area_select_menu.values[0]
        char_class = [char_class for char_class in self.areas if char_class.name == chosen_value][0]
        self.update_description(new_description=f'Area title : **{char_class.name}**\n\n'
                                                f'Area description : \n{char_class.description}\n\n'
                                                f'Click **Accept** to choose the {char_class.name} area',
                                title='Select a starting area for your character!')
        self.chosen_area = chosen_value
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def new_button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.embed, view=self)

    async def create_class_view(self, interaction):
        self.update_description('Generating classes..', title='Classes for theme', disable_buttons=True)
        await self.update_message(interaction)
        response = await self.dnd_utility_agent.run(gen_type='class', theme=self.themes)
        classes = response.get('classes')
        # print(f'classes: {classes}')
        races = response.get('races')
        # print(f'races: {races}')
        areas = response.get('areas')
        # print(f'areas: {areas}')

        class_regex = re.compile(r'[0-9]\. (\w+(?: \w+)*) \((.*)\) - (\w+(?: \w+|.)*)')
        for match in class_regex.finditer(classes):
            print(f'matches class : {match.groups()}')
            self.classes.append(CharacterClass(match.groups()))
        for match in class_regex.finditer(races):
            print(f'matches race : {match.groups()}')
            self.races.append(CharacterClass(match.groups()))
        for match in class_regex.finditer(areas):
            print(f'matches area : {match.groups()}')
            self.areas.append(CharacterClass(match.groups()))
        self.update_description(new_description=f'Class title : **{self.classes[0].name}**\n\n'
                                                f'Class description : \n{self.classes[0].description}\n\n'
                                                f'Click **Accept** to choose the {self.classes[0].name} class',
                                title='Select a class for your character!')
        self.create_select_menu(menu_type='class')
        self.chosen_class = self.classes[0].name
        await self.update_message(interaction)

    async def create_race_view(self, interaction):
        self.update_description('Generating races..', title='Races for theme', disable_buttons=True)
        await self.update_message(interaction)
        self.update_description(new_description=f'Race title : **{self.races[0].name}**\n\n'
                                                f'Race description : \n{self.races[0].description}\n\n'
                                                f'Click **Accept** to choose the {self.races[0].name} race',
                                title='Select a race for your character!')
        self.create_select_menu(menu_type='race')
        self.chosen_race = self.races[0].name
        await self.update_message(interaction)

    async def create_area_view(self, interaction):
        self.update_description('Generating map areas..', title='Areas for theme', disable_buttons=True)
        await self.update_message(interaction)
        self.update_description(new_description=f'Area title : **{self.areas[0].name}**\n\n'
                                                f'Area description : \n{self.areas[0].description}\n\n'
                                                f'Click **Accept** to choose the {self.areas[0].name} area',
                                title='Select a starting area for your character!')
        self.create_select_menu(menu_type='area')
        self.chosen_area = self.races[0].name
        await self.update_message(interaction)

    def create_select_menu(self, menu_type):
        if menu_type == 'class':
            to_iter_over = self.classes
            menu = self.class_select_menu
            chosen_value = self.chosen_class
        elif menu_type == 'race':
            to_iter_over = self.races
            menu = self.race_select_menu
            chosen_value = self.chosen_race
            self.remove_item(self.class_select_menu)
        else:
            to_iter_over = self.areas
            menu = self.area_select_menu
            chosen_value = self.chosen_area
            self.remove_item(self.race_select_menu)

        for char_class in to_iter_over:
            if char_class.name != chosen_value:
                menu.add_option(label=char_class.name,
                                description=f'{char_class.description[:40]}..',
                                emoji=char_class.emoji.replace(' ', '')[:1])
        self.add_item(menu)

    def update_description(self, new_description, title, disable_buttons=False, colour=discord.Colour.green(),
                           **kwargs):
        self.description = new_description
        self.title = title

        if (themes := kwargs.get('themes')) is not None:
            self.themes = themes

        if not disable_buttons:
            self.accept_button.disabled = False
            self.new_button.disabled = False
        else:
            self.accept_button.disabled = True
            self.new_button.disabled = True
        print(f'NEW DESCRIPTION : {new_description}')
        self.construct_embed_for_description(new_description, title, colour)

    def construct_embed_for_description(self, new_description, title, colour=discord.Colour.green()):
        self.embed = Embed(title=title, colour=colour,
                           description=f'{new_description}' + (
                               f'\n\nThemes: {self.themes}' if self.themes is not None else ''))


class PromptModal(discord.ui.Modal):
    def __init__(self, view) -> None:
        super().__init__(title='New theme')
        self.view: DnDUtilityView = view
        self.add_item(discord.ui.InputText(label="New theme for the prompt", placeholder="For ex. Zombies in New york"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.update_description('Generating scene..', title='Prompt for DND master', disable_buttons=True)
        await self.view.update_message(interaction)
        output = await self.view.dnd_utility_agent.run(themes=self.children[0].value, gen_type='description')
        new_description = output.get('followup')
        title = output.get('title')
        self.view.update_description(new_description, themes=self.children[0].value, title=title)
        await self.view.update_message(interaction)


class DnDView(View):
    def __init__(self, followup, title, dnd_agent, disable_buttons=False):
        self.dndagent = dnd_agent
        self.action_button = Button(label='Action')
        self.action_button.callback = self.action_button_callback
        self.continue_button = Button(label='Continue')
        self.continue_button.callback = self.continue_button_callback

        if disable_buttons:
            self.action_button.disabled = True
            self.continue_button.disabled = True

        self.modal = ActionModal(view=self)
        self.title = title
        self.followup = followup
        self.embed = Embed(title=title, color=discord.Colour.nitro_pink(), description=followup)
        super().__init__(self.action_button, self.continue_button)

    async def action_button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal)

    async def continue_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.remove_buttons(interaction=interaction)
        action_embed = Embed(title='You chose to continue the scene', colour=discord.Colour.blue())
        thread: Thread = interaction.channel
        await thread.send(embed=action_embed)
        scene_view = DnDView(followup='Generating next scene..', title=self.title, dnd_agent=self.dndagent,
                             disable_buttons=True)
        message: discord.Message = await thread.send(embed=scene_view.embed, view=scene_view)
        new_description = await self.dndagent.run(player_choice=f'Continue generating next event')
        scene_view.update_embed(new_description=new_description)
        await message.edit(embed=scene_view.embed, view=scene_view)

    def update_embed(self, new_description):
        self.construct_embed(new_description=new_description)
        self.continue_button.disabled = False
        self.action_button.disabled = False

    def construct_embed(self, new_description):
        self.embed = Embed(title=self.title, colour=discord.Colour.nitro_pink(),
                           description=new_description)

    async def remove_buttons(self, interaction: discord.Interaction):
        self.remove_item(self.continue_button)
        self.remove_item(self.action_button)
        await interaction.edit_original_response(embed=self.embed, view=self)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.embed, view=self)


class ActionModal(discord.ui.Modal):
    def __init__(self, view) -> None:
        super().__init__(title='Perform an action')
        self.view: DnDView = view
        self.add_item(discord.ui.InputText(label="Perform an action", placeholder="For ex. Run away"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.view.remove_buttons(interaction)

        action_embed = Embed(title='You performed an action', description=f'Action: {self.children[0].value}',
                             colour=discord.Colour.green())
        thread: Thread = interaction.channel
        await thread.send(embed=action_embed)

        scene_view = DnDView(followup='Generating next scene..', title=self.view.title,
                             dnd_agent=self.view.dndagent, disable_buttons=True)
        message: discord.Message = await thread.send(embed=scene_view.embed, view=scene_view)
        new_description = await self.view.dndagent.run(player_choice=self.children[0].value)
        scene_view.update_embed(new_description=new_description)
        await message.edit(embed=scene_view.embed, view=scene_view)


class CharacterClass:
    def __init__(self, group):
        self.name = group[0]
        self.emoji = group[1]
        self.description = group[2]
