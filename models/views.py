import discord
from discord.ui import Button
from discord.ui import View
from discord import Embed, TextChannel, Thread
from discord.ui import Select
from agents import DnDUtilityAgent, DnDAgent
from models.custom_bot import DiscordBot
from dotagent.memory import SummaryMemory

class DnDUtilityView(View):
    def __init__(self, description, bot):
        self.bot: DiscordBot = bot
        self.description = description
        self.title = None
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
        message = await interaction.original_response()
        await message.delete()
        channel: TextChannel = interaction.channel
        thread = await channel.create_thread(name=self.title)
        dnd_agent = DnDAgent(system_prompt=self.description, memory=SummaryMemory())
        self.bot.dnd_threads.append(thread.id)
        self.bot.dnd_clients[thread.id] = dnd_agent
        followup = await dnd_agent.run(player_choice='Begin Journey')
        view = DnDView(followup=followup, title=self.title, dnd_agent=dnd_agent)
        await thread.send(embed=view.embed, view=view)

    async def new_button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.embed, view=self)

    def update_embed(self, new_description, themes=None, title=None):
        self.description = new_description
        self.title = title
        self.accept_button.disabled = False
        self.new_button.disabled = False
        print(f'NEW DESCRIPTION : {new_description}')
        self.construct_embed(new_description, themes)

    def construct_embed(self, new_description, themes=None):
        self.embed = Embed(title='Prompt for DND master', colour=discord.Colour.green(),
                           description=f'{new_description}'+(f'\n\nThemes: {themes}' if themes is not None else ''))


class PromptModal(discord.ui.Modal):
    def __init__(self, view) -> None:
        super().__init__(title='New theme')
        self.view: DnDUtilityView = view
        self.add_item(discord.ui.InputText(label="New theme for the prompt", placeholder="For ex. Zombies in New york"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.update_embed('Generating scene..')
        await self.view.update_message(interaction)
        output = await self.view.dnd_utility_agent.run(themes=self.children[0].value)
        new_description = output.get('followup')
        title = output.get('title')
        self.view.update_embed(new_description, themes=self.children[0].value, title=title)
        await self.view.update_message(interaction)


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

        scene_view = DnDView(followup='Generating next scene..', title=self.view.title, dnd_agent=self.view.dndagent)
        message: discord.Message = await thread.send(embed=scene_view.embed, view=scene_view)
        new_description = await self.view.dndagent.run(player_choice=self.children[0].value)
        scene_view.update_embed(new_description=new_description)
        await message.edit(embed=scene_view.embed, view=scene_view)


class DnDView(View):
    def __init__(self, followup, title, dnd_agent):
            self.dndagent = dnd_agent
            self.action_button = Button(label='Action')
            self.action_button.callback = self.action_button_callback
            self.continue_button = Button(label='Continue')
            self.continue_button.callback = self.continue_button_callback
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
        scene_view = DnDView(followup='Generating next scene..', title=self.title, dnd_agent=self.dndagent)
        message: discord.Message = await thread.send(embed=scene_view.embed, view=scene_view)
        new_description = await self.dndagent.run(player_choice=f'Continue generating next event')
        scene_view.update_embed(new_description=new_description)
        await message.edit(embed=scene_view.embed, view=scene_view)

    def update_embed(self, new_description):
        self.construct_embed(new_description=new_description)

    def construct_embed(self, new_description):
        self.embed = Embed(title=self.title, colour=discord.Colour.green(),
                           description=new_description)

    async def remove_buttons(self, interaction: discord.Interaction):
        self.remove_item(self.continue_button)
        self.remove_item(self.action_button)
        await interaction.edit_original_response(embed=self.embed, view=self)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.embed, view=self)


