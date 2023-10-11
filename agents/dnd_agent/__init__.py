from typing import Any, Dict, Union
from dotagent.agent.base_agent import BaseAgent
import logging
from agents.utils import initialize_dotagent_client
from .utils import DnDUtilityAgent
from dotagent import compiler
from dotagent.compiler import Program
import json
import ctypes


class DnDAgent(BaseAgent):

    def __init__(self, system_prompt,
                 final_name,
                 final_class,
                 final_race,
                 final_area,
                 final_attributes,
                 all_areas,
                 all_races,
                 all_classes,
                 llm=None, memory=None, **kwargs):
        super().__init__(**kwargs)
        if llm is None:
            llm = compiler.llms.OpenAI(model='gpt-3.5-turbo-16k')
        self.all_areas = all_areas,
        self.all_races = all_races,
        self.all_classes = all_classes,
        self.system_prompt = system_prompt
        self.player_name = final_name,
        self.player_class = final_class,
        self.player_race = final_race,
        self.player_attributes = final_attributes,
        self.current_area = final_area,
        self.tools = (self.get_all_classes, self.get_all_races, self.get_all_areas)
        self.compiler: Program = initialize_dotagent_client(llm=llm, file_name='dnd', memory=memory, async_mode=True)
        # self.output_key = 'followup'
        self.return_complete = True

    def agent_type(self):
        return "chat"

    def get_all_classes(self):
        return '\n'.join([f'{unique_class.name} - {unique_class.description}' for unique_class in self.all_classes])

    def get_all_races(self):
        return '\n'.join([f'{unique_race.name} - {unique_race.description}' for unique_race in self.all_races])

    def get_all_areas(self):
        return '\n'.join([f'{unique_area.name} - {unique_area.description}' for unique_area in self.all_races])

    async def run(self, **kwargs):
        kwargs = {**{'dungeon_master_info': self.system_prompt,
                     'player_name': self.player_name,
                     'player_class': self.player_class,
                     'player_race':self.player_race,
                     'player_attributes': self.player_attributes,
                     'current_area': f'Area name: {self.current_area}\n'
                                     f'Area description {self.current_area}'},
                    'dnd_agent' : id(self),
                    'tool' : self.tools,
                    'tool_func' : tool_use, **kwargs}
        output = await super().run(**kwargs)
        return output


def tool_use(var: dict):
    var = json.loads(var)
    print('VAR:', var)
    dnd_agent: DnDAgent = ctypes.cast(var['dnd_agent'], ctypes.py_object).value
    tools = (dnd_agent.get_all_classes, dnd_agent.get_all_races, dnd_agent.get_all_areas)
    return tools[int(var['index'])]()
